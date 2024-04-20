from django.utils.decorators import method_decorator
from django.shortcuts import render
from datetime import datetime, timedelta
from .models import Transaction
from django.contrib import messages
from django.utils.safestring import mark_safe

def upcoming_payments_decorator(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # Define 'today' and 'threshold_date' at the beginning of the function
        today = datetime.now().date()
        threshold_date = today + timedelta(days=5)

        # Initialize `upcoming_payments` query outside of the conditional to ensure it's always defined
        upcoming_payments = Transaction.objects.filter(
            user=request.user,
            is_pre_auth=True,
            date__gt=today,  # Greater than today
            date__lte=threshold_date  # Less than or equal to 5 days from now
        )

        if not request.session.get('warning_dismissed', False):
            if upcoming_payments.exists():
                link = '<a href="/transactions/pre-auth/">Check Pre-Auth Payments</a>'
                message = mark_safe(f"You have upcoming Pre-Auth payments due soon! {link}")
                messages.warning(request, message)
        
        response = view_func(request, *args, **kwargs)
        
        # Reset the dismissal flag when the session ends or the user logs out
        request.session['warning_dismissed'] = False
        
        return response

    return _wrapped_view

