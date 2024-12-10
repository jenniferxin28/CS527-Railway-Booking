from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# path takes the arguments of (url, view function, name)
# e.g. a url like '/login' can be accessed from http://127.0.0.1:8000/login
# e.g. the name is what you use to link to the page in our html files
app_name = "railway"
urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("user/", views.user, name="user"),
    path("home/", views.home, name="home"),
    path("railway_admin/", views.railway_admin, name="railway_admin"),
    path("rep/", views.rep, name="rep"),
    path('cart/<int:schedule_id>/', views.cart, name='cart'),
    path('cancel_reservation/<int:rid>/', views.cancel_reservation, name='cancel_reservation'),
    path("faq/", views.faq, name="faq"),
    path('ask/', views.ask_question, name='ask_question'),
    path('submitted/', views.question_submitted, name='question_submitted'),
    path('unanswered/', views.unanswered_questions, name='unanswered_questions'),
    path('submit_answer/', views.submit_answer, name='submit_answer'),
    path('schedule_list/', views.schedule_list, name='schedule_list'),
    path('customer_list/', views.customer_list, name='customer_list'),
    path('add_customer_rep/', views.add_customer_rep, name='add_customer_rep'),
    path('add_customer_rep_form/', views.add_customer_rep_form, name='add_customer_rep_form'),
    path('search_customer_rep/', views.search_customer_rep, name='search_customer_rep'),
    path('edit_customer_rep/<int:ssn>/', views.edit_customer_rep, name='edit_customer_rep'),
    path('delete_customer_rep/<int:ssn>/', views.delete_customer_rep, name='delete_customer_rep'),
    path('sales_report/', views.sales_report, name='sales_report'),
    path('reservations_by_customer/', views.reservations_by_customer, name='reservations_by_customer'),
    path('reservations_by_transit_line/', views.reservations_by_transit_line, name='reservations_by_transit_line'),
    path('revenue_by_customer/', views.revenue_by_customer, name='revenue_by_customer'),
    path('revenue_by_transit_line/', views.revenue_by_transit_line, name='revenue_by_transit_line'),
    path('best_customers/', views.best_customers, name='best_customers'),
    path('active_train_lines/', views.active_train_lines, name='active_train_lines'),
    path('search_customer_rep/', views.search_customer_rep, name='search_customer_rep'),
]
urlpatterns += staticfiles_urlpatterns()