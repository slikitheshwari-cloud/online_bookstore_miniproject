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

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    book=item['book'],
                    price=item['price'],
                    quantity=item['quantity']
                )

            cart.clear()
            return render(request, 'order/successfull.html', {'order': order})

        else:
            messages.error(request, "Fill out your information correctly.")

    if len(cart) > 0:
        return render(request, 'order/order.html', {"form": form})

    return redirect('store:books')


def order_list_view(request):
    orders = Order.objects.filter(customer_id=request.user.id).order_by('-created')

    paginator = Paginator(orders, 5)
    page = request.GET.get('page')
    paginated_orders = paginator.get_page(page)

    return render(request, 'order/list.html', {"myorder": paginated_orders})


def order_detail_view(request, id):
    order = get_object_or_404(Order, id=id)

    if order.customer_id != request.user.id:
        return redirect('store:index')

    items = OrderItem.objects.filter(order_id=id)

    return render(request, 'order/details.html', {
        "o_summary": order,
        "o_item": items
    })


# =========================
# PDF VIEW
# =========================
class pdf(View):
    def get(self, request, id):
        order = get_object_or_404(Order, id=id)

        context = {
            "order": order
        }

        pdf_file = renderPdf('order/pdf.html', context)

        return HttpResponse(pdf_file, content_type='application/pdf')


# =========================
# REST API VIEWS
# =========================

# GET ALL ORDERS
@api_view(['GET'])
def order_list_api(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


# GET SINGLE ORDER
@api_view(['GET'])
def order_detail_api(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = OrderSerializer(order)
    return Response(serializer.data)


# CREATE ORDER
@api_view(['POST'])
def create_order_api(request):
    serializer = OrderSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# UPDATE ORDER
@api_view(['PUT'])
def update_order_api(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = OrderSerializer(order, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# UPDATE PAYMENT STATUS
@api_view(['PUT'])
def update_payment_api(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    order.paid = True
    order.save()

    return Response({'message': 'Payment Updated Successfully'})


# DELETE ORDER
@api_view(['DELETE'])
def delete_order_api(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    order.delete()

    return Response({'message': 'Order Deleted Successfully'})