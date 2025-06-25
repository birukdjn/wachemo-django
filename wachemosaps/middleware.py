from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            
            if last_activity and (timezone.now() - last_activity > timedelta(seconds=300)):
                # Session expired - force logout
                from django.contrib.auth import logout
                logout(request)
                return redirect(reverse('login') + '?session_expired=1')
            
            # Update last activity time
            request.session['last_activity'] = timezone.now()
        
        response = self.get_response(request)
        
        # Prevent caching for authenticated pages
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response
    
    