from django.shortcuts import render, HttpResponse
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from source import models

from datetime import datetime
import pytz
import json
import requests
import re


### Internal functions ###

def authenticate(request):
    """Authenticates that an API request has a valid API key or Slack token"""
    authenticated = False

    ### Get the API key from the header if it exists ###
    api_key = request.META.get('HTTP_AUTHORIZATION')
    if api_key == settings.ENIGMA_API_KEY:
        authenticated = True

    else:
        ### Get the Slack token from the form request if it exists ###
        slack_token = request.POST['token']
        if slack_token == settings.SLACK_TOKEN:
            authenticated = True
            
    return authenticated


def create_secret(request):
    """Creates a record of a new secret message in the database and returns the
    URL to that access that message"""
    try:
        ### Try to get the message from the form ###
        message = request.POST.get('message')
        method = 'UI'
        ### Otherwise try to get the message from the API request body ###
        if not message:
            ### Try to get the message as the `message` param ###
            try:
                request_body = json.loads(request.body.decode())
                message = request_body['message']
                method = 'API'
            ### Otherwise use the `text` param Slack utilizes ###
            except:
                request_body = request.POST
                message = request_body['text']
                method = 'Slack'
                if message.startswith('<@'):
                    ### Remove the @mention of the recipient for the message ###
                    message = re.sub(r'[\<].*?[\>]', '', message)
                    ### Remove the extraneous space after the @mention ###
                    message = message.replace(' ', '', 1)
        if method == 'UI' or method == 'API':
            message = escape(message)
    except:
        return

    ### Save the message in the database ###
    message_record = models.Secret(message=message)
    message_record.save()

    ### Build the URL to access the secret ###
    protocol = 'https://'
    domain = request.META['HTTP_HOST']
    if 'localhost' in domain:
        protocol = 'http://'
    message_url =  protocol + domain + '/secret/confirm/' + str(message_record.uuid)
    return method, message_url


def send_slack_message(sender, recipient, message_url):
    """Sends a Slack message to the specified user in a direct message"""
    url = 'https://slack.com/api/chat.postMessage'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + settings.SLACK_OAUTH_TOKEN
    }
    data = {
        'channel': recipient,
        'text': 'You just received a secret from ' + sender + ':',
        'attachments': [{'text': '<' + message_url + '|One Time Access URL>'}],
        'as_user': False,
    }
    data = json.dumps(data)
    response = requests.post(url, headers=headers, data=data)
    if not response.ok:
        print(response.json())


def return_response(status, message, parameter='message'):
    """Returns a JSON response with a given status and message"""
    success = False
    if status == 200:
        success = True
    message = {
        'success': success,
        parameter: message
    }
    message = json.dumps(message)
    return HttpResponse(message, status=status, content_type='application/json')


### External views ###

### UI views ###
def home(request):
    """Renders the secret submissions page as the homepage. If a user is
    submitting a secret, this function also saves the message in the
    database as an encrypted value and returns an access URL"""
    if request.method == 'GET':
        return render(request, 'home.html')

    elif request.method != 'POST':
        print('Form submission with invalid method ' + request.method)
        return render(request, 'home.html')

    ### Get the message from the form and save it to the database ###
    method, message_url = create_secret(request)
    context = {
        'open_modal': True,
        'display_url': True,
        'message_url': message_url
    }
    return render(request, 'home.html', context)


def view_secret(request, confirmation, uuid):
    """Renders a modal that asks for users to confirm whether they
    would like to view the secret they intended to load. If users do not
    want to view the secret, the modal closes. If users want to view the secret,
    display it and delete it from the database"""
    ### Ensure the path is either `view/` or `confirm/` ###
    if confirmation != 'view' and confirmation != 'confirm':
        return render(request, 'home.html')

    ### Check if the secret message exists ###
    try:
        secret = models.Secret.objects.get(uuid=uuid)
        message = secret.message
        context = {
            'open_modal': True,
            'uuid': uuid
        }
        ### Display the message and delete it if `view/` is in the path ###
        ### Otherwise ask for confirmation to display the message ###
        if confirmation == 'view':
            context['secret_message'] = message
            secret.delete()
    except:
        ### Display an error message that the secret no longer exists ###
        context = {
            'open_modal': True,
            'deleted_message': True
        }

    return render(request, 'home.html', context)


### API views ###
@csrf_exempt
def delete_expired_secrets(request):
    """Deletes any secrets that are beyond their expiration timestamps"""
    ### Only accept a POST method ###
    if request.method != 'POST':
        status = 405
        message = 'Invalid method'
        return return_response(status, message)

    ### Validate the Quartz API key ###
    api_key = request.META.get('HTTP_AUTHORIZATION')
    if api_key != settings.QUARTZ_API_KEY:
        status = 403
        message = 'Invalid Quartz job token'
        return return_response(status, message)

    ### Run the job ###
    ### Find all records that are beyond the expiration timestamp ###
    now = datetime.now(pytz.utc)
    secrets = models.Secret.objects.filter(expiration_timestamp__lt=now)
    ### Count the number of secrets to be deleted and delete them ###
    number_of_deleted_secrets = len(secrets)
    secrets.delete()
    status = 200
    if number_of_deleted_secrets == 1:
        message = '1 expired secret was deleted'
    elif number_of_deleted_secrets > 1:
        message = str(number_of_deleted_secrets) + ' expired messages were deleted'
    else:
        message = 'There weren\'t any expired secrets to delete'
    return return_response(status, message)


@csrf_exempt
def create_secret_api(request):
    """Accepts a POST API request to create a new secret and returns the URL
    to access that secret in the response body as the 'message_url' param"""
    ### Only accept a POST method ###
    if request.method != 'POST':
        status = 405
        message = 'Invalid method'
        return return_response(status, message)

    ### Authenticate that the request has valid credentials ###
    authenticated = authenticate(request)
    if not authenticated:
        status = 403
        message = 'Invalid API key or Slack token'
        return return_response(status, message)

    ### Get the request body and save it to the database ###
    method, message_url = create_secret(request)

    ### Return a 400 if the request body is missing the `message` parameter ###
    if not message_url:
        status = 400
        message = 'Request body missing the \'message\' parameter'
        return return_response(status, message)

    ### Otherwise successfully return the message access URL ###
    status = 200
    if method == 'Slack':
        message = request.POST['text']
        ### If there is an @mention, send that recipient the URL ###
        if message.startswith('<@'):
            ### Get recipient ID from beginning of message matching @ID| ###
            recipient_id = re.search(r'[@](.*?)[|]', message)
            recipient = recipient_id.group().replace('@', '').replace('|', '')

            ### Format the Slack syntax to @mention the sending user ###
            sender_name = request.POST['user_name']
            sender_id = request.POST['user_id']
            sender = '<@' + sender_id + '|' + sender_name  + '>'

            ### Message the URL to the recipient ###
            send_slack_message(sender, recipient, message_url)

            ### Message to the sender confirmation that the URL was delivered ###
            recipient_name = re.search(r'[<](.*?)[\>]', message)
            recipient_name = recipient_name.group()
            message = recipient_name + ' just received your message!'
            return return_response(status, message, parameter='text')

        ### Otherwise send the URL to the sender ###
        else:
            message = 'Send your recipient this one-time access URL: ' + message_url
            return return_response(status, message, parameter='text')

    ### Send the access URL in JSON if created via the API ###
    else:
        return return_response(status, message_url, parameter='message_url')
