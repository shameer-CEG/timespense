# myapp/middleware.py

from django.shortcuts import redirect
from django.http import HttpResponse

class LogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Check if the 'next' parameter is present and equals '/'
        if 'next' in request.GET and request.GET['next'] == '/':
            # Log out the user and return a response with a JavaScript redirect
            from django.contrib.auth import logout
            logout(request)

            # JavaScript script for redirecting
            js_script = '<script>history.replaceState(null, null, "/");</script>'
            return HttpResponse(js_script)

        return response
