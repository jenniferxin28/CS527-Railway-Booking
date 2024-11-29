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

# login page view
def index(request):
    context = {}

    if request.method == 'POST':
        if 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')

            user_type = None
            login_info = None

            # employee table
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT level FROM Employee WHERE username = %s AND password = %s",
                    [username, password]
                )
                login_info = cursor.fetchone()
                if login_info:
                    user_type = login_info[0]
            
            # customer table
            if not login_info:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT 'customer' FROM Customer WHERE username = %s AND password = %s",
                        [username, password]
                    )
                    login_info = cursor.fetchone()
                    if login_info:
                        user_type = 'customer'

            # authy success
            if login_info:
                request.session['is_logged_in'] = True
                request.session['user_type'] = user_type
                return redirect('railway:home')
            else:
                context['message'] = "Invalid credentials"

        elif 'logout' in request.POST:
            request.session.flush()
            context['message'] = "Successfully logged out."
            
    return render(request, "railway/index.html", context)



