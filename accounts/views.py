from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import CustomUserCreationForm, CustomErrorList, PasswordResetForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile
#Changed from user-input security question to hardcoded question: "What is your favorite movie"
#User's answer is now stored in User.first_name field instead of a separate field
@login_required
def logout(request):
    auth_logout(request)
    return redirect('movies.index')

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(
            request,
            username = request.POST['username'],
            password = request.POST['password'],
        )
        if user is None:
            template_data['error'] = '* The username or password is incorrect.'
            return render(request, 'accounts/login.html',
                {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('movies.index')


def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'

    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})

    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)

        if form.is_valid():
            # Save the user with the security answer in first_name
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']  # This will store the security answer
            user.save()

            # Create profile with hardcoded question
            user_profile, created = UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'security_question': "What is your favorite movie",
                    'security_answer': user.first_name  # Using first_name as the answer
                }
            )

            # Log the user in
            auth_login(request, user)

            messages.success(request, 'Account created successfully!')
            return redirect('movies.index')

        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})

@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    print(request.user.userprofile.security_question)
    return render(request, 'accounts/orders.html',
        {'template_data': template_data})


def reset(request):
    template_data = {}
    template_data['title'] = 'Reset Password'

    if request.method == 'GET':
        form = PasswordResetForm()
        return render(request, 'accounts/reset.html', {'template_data': template_data, 'form': form})

    elif request.method == 'POST':
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            new_password = form.cleaned_data['new_password']
            security_answer = form.cleaned_data.get('security_answer')

            try:
                user = User.objects.get(username=username)
                user_profile = user.userprofile

                stored_answer = user_profile.security_answer.strip().lower()
                user_answer = security_answer.strip().lower()

                if user_answer == stored_answer:
                    user.set_password(new_password)
                    user.save()
                    auth_login(request, user)
                    messages.success(request, 'Your password has been reset successfully.')
                    return redirect('movies.index')
                else:
                    #The entered user answer is correct, the user_profile security answer is empty when checking in admin
                    print("Stored Answer:", user_profile.security_answer)
                    print("User Answer:", user_answer)
                    template_data['error'] = '* The security answer is incorrect.'
                    return render(request, 'accounts/reset.html', {'template_data': template_data, 'form': form})

            except User.DoesNotExist:
                template_data['error'] = '* No account found with that username.'
                return render(request, 'accounts/reset.html', {'template_data': template_data, 'form': form})
