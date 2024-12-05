from django.shortcuts import render, redirect
from django.db import connection
# Create your views here.
# Remember to write a view for every single page, then link the function in railway/urls.py to display the view

# view for home page - where all the railway booking will be done
def home(request):
    if not request.session.get('is_logged_in'):
        return redirect('railway:index')

    stations = []
    schedules = []
    sort = request.GET.get('sort', 'departure_time')

    with connection.cursor() as cursor:
        # dropdowns
        cursor.execute("SELECT sid, name FROM Station")
        stations = [{'sid': row[0], 'name': row[1]} for row in cursor.fetchall()]

    origin = request.GET.get('origin', None)
    destination = request.GET.get('destination', None)
    date = request.GET.get('date', None)

    if date:
        query = """
            SELECT TS.transit_line_name, TS.departure_time, TS.arrival_time, TS.fare, 
                   O.name as origin_name, D.name as dest_name
            FROM TrainSchedule TS
            JOIN Station O ON TS.origin = O.sid
            JOIN Station D ON TS.dest = D.sid
            WHERE DATE(TS.departure_time) = %s
        """
        params = [date]

        # allow default options to search for all
        if origin:
            query += " AND TS.origin = %s"
            params.append(origin)
        if destination:
            query += " AND TS.dest = %s"
            params.append(destination)

        # sort
        query += f" ORDER BY {sort} ASC"

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            schedules = [{
                'transit_line_name': row[0],
                'departure_time': row[1],
                'arrival_time': row[2],
                'fare': row[3],
                'origin': {'name': row[4]},
                'dest': {'name': row[5]},
                'stops': []
            } for row in cursor.fetchall()]

            # stops
            for schedule in schedules:
                cursor.execute(
                    """
                    SELECT S.name, ST.stop_time_arrival, ST.stop_time_departure
                    FROM Stops ST
                    JOIN Station S ON ST.sid = S.sid
                    WHERE ST.transit_line_name = %s
                    ORDER BY ST.stop_order ASC
                    """,
                    [schedule['transit_line_name']]
                )
                schedule['stops'] = [{'name': row[0], 'stop_time_arrival': row[1], 'stop_time_departure': row[2]} for row in cursor.fetchall()]

    context = {
        'stations': stations,
        'schedules': schedules,
        'sort': sort
    }
    return render(request, "railway/home.html", context)

# cart page view
def cart(request):
    return render(request, "railway/cart.html", {})
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
# admin_account view
def railway_admin(request):
    return render(request, "railway/admin_account.html", {})
# rep_account view
def rep(request):
    return render(request, "railway/rep_account.html", {})
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
                if user_type == 'admin':
                    return redirect('railway:railway_admin')
                elif user_type == 'rep':
                    return redirect('railway:rep')
                elif user_type == 'customer':
                    return redirect('railway:home')
            else:
                context['message'] = "Invalid credentials"

        elif 'logout' in request.POST:
            request.session.flush()
            context['message'] = "Successfully logged out."
            
    return render(request, "railway/index.html", context)




