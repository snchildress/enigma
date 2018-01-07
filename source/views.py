from django.shortcuts import render
from django.utils.html import escape

from source import models


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
    # message = request.POST.get('message')
    message = escape(request.POST.get('message'))
    message_record = models.Secret(message=message)
    message_record.save()

    message_url = request.build_absolute_uri() + 'secret/confirm/' + str(message_record.uuid)
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
    try:
        secret = models.Secret.objects.get(uuid=uuid)
        message = secret.message
        context = {
            'open_modal': True,
            'uuid': uuid
        }
        ### Display the message and delete it if `/view` is in the path ###
        ### Otherwise ask for confirmation to display the message       ###
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
