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
            SELECT TS.schedule_id, TS.transit_line_name, TS.departure_time, TS.arrival_time, TS.fare, 
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
                'schedule_id': row[0],
                'transit_line_name': row[1],
                'departure_time': row[2],
                'arrival_time': row[3],
                'fare': row[4],
                'origin': {'name': row[5]},
                'dest': {'name': row[6]},
                'stops': []
            } for row in cursor.fetchall()]

            # stops
            for schedule in schedules:
                cursor.execute(
                    """
                    SELECT S.name, ST.stop_time_arrival, ST.stop_time_departure
                    FROM Stops ST
                    JOIN Station S ON ST.sid = S.sid
                    WHERE ST.schedule_id = %s
                    ORDER BY ST.stop_order ASC
                    """,
                    [schedule['schedule_id']]
                )
                schedule['stops'] = [{'name': row[0], 'stop_time_arrival': row[1], 'stop_time_departure': row[2]} for row in cursor.fetchall()]

    context = {
        'stations': stations,
        'schedules': schedules,
        'sort': sort
    }
    return render(request, "railway/home.html", context)

# cart page view
def cart(request, schedule_id):
    if not request.session.get('is_logged_in'):
        return redirect('railway:index')

    train_details = {}
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT TS.schedule_id, TS.transit_line_name, TS.departure_time, TS.arrival_time, TS.fare, 
                   O.name as origin_name, D.name as dest_name
            FROM TrainSchedule TS
            JOIN Station O ON TS.origin = O.sid
            JOIN Station D ON TS.dest = D.sid
            WHERE TS.schedule_id = %s
            """,
            [schedule_id]
        )
        row = cursor.fetchone()
        if row:
            train_details = {
                'schedule_id': row[0],
                'transit_line_name': row[1],
                'departure_time': row[2],
                'arrival_time': row[3],
                'fare': row[4],
                'origin': row[5],
                'destination': row[6],
            }

    # hardcoded discount values
    if request.method == 'POST':
        num_children = int(request.POST.get('children', 0))
        num_adults = int(request.POST.get('adults', 0))
        num_seniors = int(request.POST.get('seniors', 0))
        num_disabled = int(request.POST.get('disabled', 0))
        trip_type = request.POST.get('trip_type', 'one-way')

        base_fare = train_details['fare']
        total_fare = (
            num_children * base_fare * 0.5 +
            num_adults * base_fare +
            num_seniors * base_fare * 0.8 +
            num_disabled * base_fare * 0.7
        )
        if trip_type == 'round-trip':
            total_fare *= 2

        total_fare = round(total_fare, 2)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO Reservation (date, pid, total_fare, schedule_id, dsid, asid, children, adults, seniors, disabled)
                VALUES (CURRENT_DATE, %s, %s, %s,
                        (SELECT origin FROM TrainSchedule WHERE schedule_id = %s),
                        (SELECT dest FROM TrainSchedule WHERE schedule_id = %s),
                        %s, %s, %s, %s)
                """,
                [
                    request.session['user_id'], total_fare, schedule_id,
                    schedule_id, schedule_id,
                    num_children, num_adults, num_seniors, num_disabled
                ]
            )
        return redirect('railway:user')

    return render(request, "railway/cart.html", {'train': train_details})

# cancel
def cancel_reservation(request, rid):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Reservation WHERE rid = %s", [rid])
        return redirect('railway:user')

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
    # basic idea: fetch all reservations sorted by date
    # all reservations from today and beyond are considered current reservations and can be cancelled
    # the rest are past reservations
    if not request.session.get('is_logged_in'):
        return redirect('railway:index')

    current_reservations = []
    past_reservations = []

    with connection.cursor() as cursor:
        # Fetch current reservations
        cursor.execute(
            """
            SELECT R.rid, R.date, R.total_fare, TS.transit_line_name, S1.name as origin, S2.name as dest, 
                   TS.departure_time, TS.arrival_time, R.children, R.adults, R.seniors, R.disabled
            FROM Reservation R
            JOIN TrainSchedule TS ON R.schedule_id = TS.schedule_id
            JOIN Station S1 ON R.dsid = S1.sid
            JOIN Station S2 ON R.asid = S2.sid
            WHERE R.pid = %s AND R.date >= CURRENT_DATE
            """,
            [request.session['user_id']]
        )
        current_reservations = [
            {
                'rid': row[0],
                'date': row[1],
                'total_fare': row[2],
                'transit_line_name': row[3],
                'origin': row[4],
                'dest': row[5],
                'departure_time': row[6],
                'arrival_time': row[7],
                'children': row[8],
                'adults': row[9],
                'seniors': row[10],
                'disabled': row[11],
            }
            for row in cursor.fetchall()
        ]

        # Fetch past reservations
        cursor.execute(
            """
            SELECT R.rid, R.date, R.total_fare, TS.transit_line_name, S1.name as origin, S2.name as dest, 
                   TS.departure_time, TS.arrival_time, R.children, R.adults, R.seniors, R.disabled
            FROM Reservation R
            JOIN TrainSchedule TS ON R.schedule_id = TS.schedule_id
            JOIN Station S1 ON R.dsid = S1.sid
            JOIN Station S2 ON R.asid = S2.sid
            WHERE R.pid = %s AND R.date < CURRENT_DATE
            """,
            [request.session['user_id']]
        )
        past_reservations = [
            {
                'rid': row[0],
                'date': row[1],
                'total_fare': row[2],
                'transit_line_name': row[3],
                'origin': row[4],
                'dest': row[5],
                'departure_time': row[6],
                'arrival_time': row[7],
                'children': row[8],
                'adults': row[9],
                'seniors': row[10],
                'disabled': row[11],
            }
            for row in cursor.fetchall()
        ]

    return render(request, "railway/user_account.html", {
        'current_reservations': current_reservations,
        'past_reservations': past_reservations,
    })

def faq(request):
    query = request.GET.get('q', '').strip()
    faqs = []

    with connection.cursor() as cursor:
        if query:
            # Parameterized query to prevent SQL injection
            cursor.execute("SELECT id, question, answer FROM faqs WHERE question LIKE %s OR answer LIKE %s", [f"%{query}%", f"%{query}%"])
        else:
            cursor.execute("SELECT id, question, answer FROM faqs ORDER BY id ASC")
        
        rows = cursor.fetchall()
    
    # Convert rows (tuples) to dictionaries
    for row in rows:
        faqs.append({
            'id': row[0],
            'question': row[1],
            'answer': row[2]
        })

    return render(request, 'railway/faq.html', {
        'faqs': faqs,
        'query': query,
    })

def ask_question(request):
    if request.method == 'POST':
        user_question = request.POST.get('question', '').strip()
        if user_question:
            # Insert the new question into the questions table, answer will be NULL by default
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO faqs (question, answer) VALUES (%s, %s)",
                    [user_question, None]
                )

            # After insertion, redirect to a success page
            return redirect('railway:question_submitted')
        else:
            # If empty question submitted, re-display form with an error
            return render(request, 'railway/ask_question.html', {
                'error': 'Please enter a question.'
            })
    else:
        # GET request: display empty form
        return render(request, 'railway/ask_question.html')

def question_submitted(request):
    return render(request, 'railway/question_submitted.html')



# admin_account view
def railway_admin(request):
    return render(request, "railway/admin_account.html", {})
# rep_account view
def rep(request):
    return render(request, "railway/rep_account.html", {})

def unanswered_questions(request):
    # Fetch unanswered questions
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, question FROM faqs WHERE answer IS NULL ORDER BY id ASC")
        rows = cursor.fetchall()

    questions = [{'id': row[0], 'question': row[1]} for row in rows]
    return render(request, 'railway/unanswered_questions.html', {
        'questions': questions
    })

def submit_answer(request):
    if request.method == 'POST':
        question_id = request.POST.get('question_id', '').strip()
        answer = request.POST.get('answer', '').strip()

        if question_id and answer:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE faqs SET answer = %s WHERE id = %s", [answer, question_id])

        # After updating, redirect back to the unanswered questions page
        return redirect('railway:unanswered_questions')
    else:
        # If accessed via GET (unlikely in normal flow), just redirect to main page
        return redirect('railway:unanswered_questions')

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
            user_id = None  

            # employee
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT SSN, first_name, last_name, level FROM Employee WHERE username = %s AND password = %s",
                    [username, password]
                )
                login_info = cursor.fetchone()
                if login_info:
                    user_id, first_name, last_name, user_type = login_info

            # customer
            if not login_info:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT cid, first_name, last_name, 'customer' FROM Customer WHERE username = %s AND password = %s",
                        [username, password]
                    )
                    login_info = cursor.fetchone()
                    if login_info:
                        user_id, first_name, last_name, user_type = login_info

            # authy success
            if login_info:
                request.session['is_logged_in'] = True
                request.session['user_type'] = user_type
                request.session['first_name'] = first_name
                request.session['last_name'] = last_name
                request.session['user_id'] = user_id 

                # redirect
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





