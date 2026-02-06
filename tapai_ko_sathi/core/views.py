from django.shortcuts import render

def home(request):
    """
    Landing page for Tapai Ko Sathi.
    """
    return render(request, "core/home.html")

