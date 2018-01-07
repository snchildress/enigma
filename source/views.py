from django.shortcuts import render


def home(request):
    """Render the secret submissions page as the homepage"""
    return render(request, 'home.html')
