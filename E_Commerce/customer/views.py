from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

@login_required
def customer_dashboard_view(request):
    return render(request, 'customer/dashboard.html')

@login_required
def change_password_view(request):
    if request.method == 'POST':
        # Use request.POST, not request.data.POST
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            logout(request)  # Log out the user after changing the password
            messages.success(request, "Password changed successfully. Please log in with your new password.")
            return redirect('login')  # Make sure to return the redirect
        '''else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)'''
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'customer/password_change.html',{'form':form})
