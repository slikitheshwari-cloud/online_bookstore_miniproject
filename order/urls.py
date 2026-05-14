from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [

    # =========================
    # HTML (FRONTEND) VIEWS
    # =========================

    path('', views.order_list_view, name="order_list"),

    path('create/', views.order_create_view, name="order_create"),

    path('<int:id>/', views.order_detail_view, name="order_details"),

    path('pdf/<int:id>/', views.pdf.as_view(), name="order_pdf"),


    # =========================
    # REST API ENDPOINTS
    # =========================

    # GET ALL ORDERS
    path('api/orders/', views.order_list_api, name='order_list_api'),

    # GET SINGLE ORDER
    path('api/orders/<int:id>/', views.order_detail_api, name='order_detail_api'),

    # CREATE ORDER
    path('api/orders/create/', views.create_order_api, name='create_order_api'),

    # UPDATE ORDER
    path('api/orders/update/<int:id>/', views.update_order_api, name='update_order_api'),

    # UPDATE PAYMENT STATUS
    path('api/orders/payment/<int:id>/', views.update_payment_api, name='update_payment_api'),

    # DELETE ORDER
    path('api/orders/delete/<int:id>/', views.delete_order_api, name='delete_order_api'),
]