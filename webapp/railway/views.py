from django.shortcuts import render, redirect
from django.db import connection
# Create your views here.
# Remember to write a view for every single page, then link the function in railway/urls.py to display the view

# view for home page - where all the railway booking will be done
def home(request):
    if not request.session.get('is_logged_in'):
        return redirect('railway:index')
    
    user_type = request.session.get('user_type', 'Unknown')
    context = {'user_type': user_type}

    return render(request, "railway/home.html", context)  
# register page view
def register(request):
    context = {}

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM Customer WHERE username = %s OR email = %s",
                [username, email]
            )
            result = cursor.fetchone()
            if result[0] > 0:
                context['message'] = "Username or email already exists."
                return render(request, 'railway/register.html', context)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO Customer (first_name, last_name, email, username, password)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [first_name, last_name, email, username, password]
            )

        return redirect('railway:index')

    return render(request, 'railway/register.html', context)
# user_account view
def user(request):
    return render(request, "railway/user_account.html", {})
# login page view
def index(request):
    context = {}

    if request.method == 'POST':
        if 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')

            user_type = None
            login_info = None
            first_name = None
            last_name = None

            # employee
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT first_name, last_name, level FROM Employee WHERE username = %s AND password = %s",
                    [username, password]
                )
                login_info = cursor.fetchone()
                if login_info:
                    first_name, last_name, user_type = login_info
            
            # customer
            if not login_info:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT first_name, last_name, 'customer' FROM Customer WHERE username = %s AND password = %s",
                        [username, password]
                    )
                    login_info = cursor.fetchone()
                    if login_info:
                        first_name, last_name, user_type = login_info

            # authy success
            if login_info:
                request.session['is_logged_in'] = True
                request.session['user_type'] = user_type
                request.session['first_name'] = first_name
                request.session['last_name'] = last_name
                return redirect('railway:home')
            else:
                context['message'] = "Invalid credentials"

        elif 'logout' in request.POST:
            request.session.flush()
            context['message'] = "Successfully logged out."
            
    return render(request, "railway/index.html", context)




