import random
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser, FailedLoginAttempt

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def is_ip_blocked(ip_address):
    time_threshold = timezone.now() - timedelta(minutes=60)
    failed_attempts = FailedLoginAttempt.objects.filter(ip_address=ip_address, timestamp__gte=time_threshold).count()
    return failed_attempts >= 3

def generate_verification_code():
    return str(random.randint(100000, 999999))

def home(request):
    ip_address = get_client_ip(request)
    if is_ip_blocked(ip_address):
        return redirect('banned')
    return render(request, 'home.html')

def login_view(request):
    ip_address = get_client_ip(request)
    if is_ip_blocked(ip_address):
        return redirect('banned')

    if request.method == "POST":
        phone = request.POST.get('number')
        if CustomUser.objects.filter(phone_number=phone).exists():
            response_data = {'status': 'exists'}
            return JsonResponse(response_data)
        else:
            code = generate_verification_code()
            request.session['verification_code'] = code
            request.session['phone'] = phone
            response_data = {'status': 'new', 'code': code}
            return JsonResponse(response_data)
        
    return render(request, 'login.html')

def verify_code_view(request):
    ip_address = get_client_ip(request)
    if is_ip_blocked(ip_address):
        return redirect('banned')

    if request.method == "POST":
        code = request.POST.get('code')
        session_code = request.session.get('verification_code', '')
        if code == session_code:
            response_data = {'status': 'verified'}
            return JsonResponse(response_data)
        else:
            response_data = {'status': 'invalid'}
            return JsonResponse(response_data)

    return render(request, 'verify_code.html')

def authenticate_user_view(request):
    ip_address = get_client_ip(request)
    if is_ip_blocked(ip_address):
        return JsonResponse({'status': 'banned'})

    if request.method == "POST":
        phone = request.session.get('phone')
        password = request.POST.get('password')

        user = authenticate(request, username=phone, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'success'})
        else:
            # Log the failed attempt
            FailedLoginAttempt.objects.create(ip_address=ip_address)
            return JsonResponse({'status': 'error'})

def signup_view(request):
    ip_address = get_client_ip(request)
    if is_ip_blocked(ip_address):
        return redirect('banned')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone = request.session.get('phone')

        if username and password and phone:

            user = CustomUser(
                username=username,
                phone_number=phone,
                password=make_password(password)
            )
            user.save()

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error'})
        else:
            return JsonResponse({'status': 'error'})

    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def banned_view(request):
    return render(request, 'banned.html')
