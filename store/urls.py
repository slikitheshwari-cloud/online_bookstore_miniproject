from django.urls import path , include
from . import views
from django.contrib import admin
app_name = 'store'

urlpatterns = [
	path('', views.index, name = "index"),
	path('login', views.signin, name="signin"),
	path('logout', views.signout, name="signout"),
	path('registration', views.registration, name="registration"),
	path('book/<int:id>', views.get_book, name="book"),
	path('books', views.get_books, name="books"),
	path('category/<int:id>', views.get_book_category, name="category"),
	path('writer/<int:id>', views.get_writer, name = "writer"),
    path('admin/', admin.site.urls),
    path('writers/', views.all_writers, name='all_writers'),
    path('', include('order.urls')),
    
    path('orders_manage/',views.orders_manage , name = 'orders_manage'),
    
	# ADMIN LOGIN
    path(
        'admin-login/',
        views.admin_login,
        name='admin_login'
    ),
    path(
    'add-book/',
    views.add_book,
    name='add_book'
),
    # ADMIN DASHBOARD
    path(
        'admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

]