from django.utils.decorators import method_decorator
from django.shortcuts import render
from datetime import datetime, timedelta
from .models import Transaction
from django.contrib import messages
from django.utils.safestring import mark_safe

def upcoming_payments_decorator(view_func):
    def _wrapped_view(request, *args, **kwargs):
        today = datetime.now().date()
        threshold_date = today + timedelta(days=5)
        
        # Query for upcoming Pre-Auth payments that are due within the next 5 days
        upcoming_payments = Transaction.objects.filter(
            user=request.user,
            is_pre_auth=True,
            date__gt=today,  # Greater than today
            date__lte=threshold_date  # Less than or equal to 5 days from now
        )

        # Add a warning message if there are upcoming payments
        if upcoming_payments.exists():
            message = mark_safe(
                "You have upcoming Pre-Auth payments due soon! "
                "<a href='/transactions/pre-auth/' class='alert-link'>Check Pre-Auth Payments</a>"
                "<button type='button' class='btn-close' data-bs-dismiss='alert' aria-label='Close'></button>"
            )

            messages.warning(request, message)
        
        # Call the actual view function
        return view_func(request, *args, **kwargs)
    return _wrapped_view

