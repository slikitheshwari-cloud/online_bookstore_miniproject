from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [

    # Existing URLs
    path('', views.order_list, name="order_list"),

    path('<int:id>/', views.order_details, name="order_details"),

    path('shipping/', views.order_create, name="order_create"),

    path('pdf/<int:id>/', views.pdf.as_view(), name="pdf"),


    # API URLs

    # GET ALL ORDERS
    path('api/orders/', views.order_list_api, name='order_list_api'),

    # GET SINGLE ORDER
    path('api/order/<int:id>/', views.order_detail_api, name='order_detail_api'),

    # CREATE ORDER
    path('api/create-order/', views.create_order_api, name='create_order_api'),

    # UPDATE ORDER
    path('api/update-order/<int:id>/', views.update_order_api, name='update_order_api'),

    # UPDATE PAYMENT STATUS
    path('api/update-payment/<int:id>/', views.update_payment_api, name='update_payment_api'),

    # DELETE ORDER
    path('api/delete-order/<int:id>/', views.delete_order_api, name='delete_order_api'),
]