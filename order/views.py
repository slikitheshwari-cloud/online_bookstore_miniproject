from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.views import View
from django.core.paginator import Paginator
from django.http import Http404

from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
from .pdfcreator import renderPdf

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderSerializer

import qrcode
from io import BytesIO
from django.core.files import File


from store.models import Book
from store.models import Writer


from django.shortcuts import render

from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def orders_view(request):

    form = OrderCreateForm()

    return render(
        request,
        'order/order.html',
        {
            'form': form
        }
    )

# =========================
# QR CODE GENERATOR
# =========================

def generate_qr_code(order):

    items = OrderItem.objects.filter(order=order)

    book_details = ""

    for item in items:

        book_details += f"""
        Book Name : {item.book.name}
        Quantity : {item.quantity}
        Price : {item.price}
        """

    qr_data = f"""
    Order ID : {order.id}

    Customer Name : {order.name}

    Email : {order.email}

    Phone : {order.phone}

    Transaction ID : {order.transaction_id}

    Payment Method : {order.payment_method}

    Total Books : {order.totalbook}

    Total Amount : {order.payable}

    {book_details}
    """

    qr_image = qrcode.make(qr_data)

    buffer = BytesIO()

    qr_image.save(buffer, format='PNG')

    file_name = f'order_{order.id}.png'

    order.qr_code.save(
        file_name,
        File(buffer),
        save=True
    )

# =========================
# FLEXIBLE PAYMENT QR CODE
# =========================

def generate_payment_qr(order):

    # Your UPI ID
    upi_id = "9885858317@ybl"

    # Business Name
    business_name = "Online Book Store"

    # Payment Note
    note = f"Payment for Order {order.id}"

    # UPI Link WITHOUT fixed amount
    upi_link = (
        f"upi://pay?"
        f"pa={upi_id}&"
        f"pn={business_name}&"
        f"cu=INR&"
        f"tn={note}"
    )

    # Generate QR
    qr = qrcode.make(upi_link)

    # Save Image
    buffer = BytesIO()

    qr.save(buffer, format='PNG')

    file_name = f'payment_qr_{order.id}.png'

    # Save QR Image
    order.payment_qr.save(
        file_name,
        File(buffer),
        save=True
    )


# =========================
# HTML VIEWS (FRONTEND)
# =========================

def order_create_view(request):

    cart = Cart(request)

    if not request.user.is_authenticated:
        return redirect('store:signin')

    customer = get_object_or_404(User, id=request.user.id)

    form = OrderCreateForm(
        request.POST or None,
        initial={
            "name": customer.first_name,
            "email": customer.email
        }
    )

    if request.method == 'POST':

        if form.is_valid():

            order = form.save(commit=False)

            order.customer = customer

            order.payable = cart.get_total_price()

            order.totalbook = len(cart)

            order.save()

            # Save Order Items
            for item in cart:

                OrderItem.objects.create(
                    order=order,
                    book=item['book'],
                    price=item['price'],
                    quantity=item['quantity']
                )

            # Generate Order Details QR
            generate_qr_code(order)

            # Generate Payment QR
            generate_payment_qr(order)

            # Clear Cart
            cart.clear()

            return render(
                request,
                'order/successfull.html',
                {
                    'order': order
                }
            )

        else:
            messages.error(
                request,
                "Fill out your information correctly."
            )

    if len(cart) > 0:

        return render(
            request,
            'order/order.html',
            {
                "form": form
            }
        )

    return redirect('store:books')


def order_list_view(request):

    orders = Order.objects.filter(
        customer_id=request.user.id
    ).order_by('-created')

    paginator = Paginator(orders, 5)

    page = request.GET.get('page')

    paginated_orders = paginator.get_page(page)

    return render(
        request,
        'order/list.html',
        {
            "myorder": paginated_orders
        }
    )


def order_detail_view(request, id):

    order = get_object_or_404(Order, id=id)

    if order.customer_id != request.user.id:
        return redirect('store:index')

    items = OrderItem.objects.filter(order_id=id)

    return render(
        request,
        'order/details.html',
        {
            "o_summary": order,
            "o_item": items
        }
    )


class pdf(View):

    def get(self, request, id):

        order = get_object_or_404(Order, id=id)

        context = {
            "order": order
        }

        pdf_file = renderPdf(
            'order/pdf.html',
            context
        )

        return HttpResponse(
            pdf_file,
            content_type='application/pdf'
        )


@login_required
def manage_orders(request):
    return render(request, 'order/manage_orders.html')


@api_view(['GET'])
def order_list_api(request):

    orders = Order.objects.all()

    serializer = OrderSerializer(orders, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def order_detail_api(request, id):

    try:
        order = Order.objects.get(id=id)

    except Order.DoesNotExist:

        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = OrderSerializer(order)

    return Response(serializer.data)


@api_view(['POST'])
def create_order_api(request):

    serializer = OrderSerializer(data=request.data)

    if serializer.is_valid():

        order = serializer.save()

        generate_qr_code(order)

        return Response(
            {
                "message": "Order Created Successfully",
                "qr_code": order.qr_code.url,
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_order_api(request, id):

    try:
        order = Order.objects.get(id=id)

    except Order.DoesNotExist:

        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = OrderSerializer(order, data=request.data)

    if serializer.is_valid():

        serializer.save()

        generate_qr_code(order)

        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_payment_api(request, id):

    try:
        order = Order.objects.get(id=id)

    except Order.DoesNotExist:

        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    order.paid = True
    order.save()

    return Response({'message': 'Payment Updated Successfully'})


@api_view(['DELETE'])
def delete_order_api(request, id):

    try:
        order = Order.objects.get(id=id)

    except Order.DoesNotExist:

        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    order.delete()

    return Response({'message': 'Order Deleted Successfully'})