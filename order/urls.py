from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [

    # =========================
    # FRONTEND PAGES
    # =========================

    # Orders dashboard page
    path(
        '',
        views.orders_view,
        name='order_list'
    ),

    # Manage Orders page
    path(
        'manage-orders/',
        views.manage_orders,
        name='manage_orders'
    ),

    # Create Order page
    path(
        'create/',
        views.order_create_view,
        name='order_create'
    ),

    # Order Details page
    path(
        '<int:id>/',
        views.order_detail_view,
        name='order_details'
    ),

    # PDF Invoice
    path(
        'pdf/<int:id>/',
        views.pdf.as_view(),
        name='order_pdf'
    ),

    # =========================
    # REST API
    # =========================

    # Get all orders
    path(
        'api/orders/',
        views.order_list_api,
        name='order_list_api'
    ),

    # Get single order
    path(
        'api/orders/<int:id>/',
        views.order_detail_api,
        name='order_detail_api'
    ),

    # Create order API
    path(
        'api/orders/create/',
        views.create_order_api,
        name='create_order_api'
    ),

    # Update order
    path(
        'api/orders/update/<int:id>/',
        views.update_order_api,
        name='update_order_api'
    ),

    # Update payment status
    path(
        'api/orders/payment/<int:id>/',
        views.update_payment_api,
        name='update_payment_api'
    ),

    # Delete order
    path(
        'api/orders/delete/<int:id>/',
        views.delete_order_api,
        name='delete_order_api'
    ),
]