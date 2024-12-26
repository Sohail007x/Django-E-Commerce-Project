from django.shortcuts import render, redirect,get_object_or_404
from account.forms import RegistrationForm, PasswordResetForm
from django.contrib import messages
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from account.utils import send_activation_email, send_reset_password_email
from account.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import SetPasswordForm

# Create your views here.


def home(request):
    return render(request, 'account/home.html')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False
            user.save()

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = reverse(
                'activate', kwargs={'uidb64': uidb64, 'token': token})
            activation_url = f'{settings.SITE_DOMAIN}{activation_link}'
            send_activation_email(user.email, activation_url)

            messages.success(
                request, 'Registration successful! Please check your email to activate your account.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'account/register.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if user.is_active:
            messages.warning(
                request, "This Account has already been activated.")
            return redirect('login')

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(
                request, "Your account has been activated successfully.")
            return redirect('login')
        else:
            messages.warning(request, "Invalid activation link or expired.")

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid Activation link.")
        return redirect('login')


def login_view(request):
    if request.user.is_authenticated:

        if request.user.is_seller:
            return redirect('seller_dashboard')

        elif request.user.is_customer:
            return redirect('customer_dashboard')

        else:
            return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid Email or Password")
            return redirect('login')

        if not user.is_active:
            messages.error(request, "Your account is inactive")
            return redirect('login')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.is_seller:
                return redirect('seller_dashboard')
            elif user.is_customer:
                return redirect('customer_dashboard')
            else:
                messages.error(
                    request, "You do not have permission to access this area")

                return redirect('home')

        else:
            messages.error(request, "Invalid Email or Password")
            return redirect('login')

    return render(request, 'account/login.html')


def password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = reverse('password_reset_confirm', kwargs={
                                    'uidb64': uidb64, 'token': token})
                absolute_reset_url = f"{request.build_absolute_uri(reset_url)}"
                send_reset_password_email(user.email, absolute_reset_url)
                messages.success(
                    request, ("We have sent you email reset link."))
                return redirect('login')

    else:
        form = PasswordResetForm()
    return render(request, 'account/password_reset.html', {'form': form})

def password_reset_confirm_view(request, uidb64, token):
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = get_object_or_404(User, pk=uid)
    if default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'account/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "The password reset link was invalid, possibly because it has already been used.")
        return redirect('password_reset')