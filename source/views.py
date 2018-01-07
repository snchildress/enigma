from django.shortcuts import render

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
    message = request.POST.get('message')
    message_record = models.Secret(message=message)
    message_record.save()


def view_secret_confirmation(request, uuid):
    """Renders a modal that asks for users to confirm whether they
    would like to view the secret they intended to load"""
    try:
        message = models.Secret.objects.get(uuid=uuid)
        context = {'secret_exists': True}
    except:
        context = {'secret_exists': False}

    return render(request, 'home.html', context)
