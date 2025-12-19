# Standard library imports
from collections import Counter
from django.utils import timezone
from django.shortcuts import render, get_object_or_404

# Third-party imports
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken

# Local app imports
from .serializers import (
    RegisterSerializer,
    OrderSerializer,
    ProfileSerializer,
    DriverSerializer,
    InvoiceSerializer
)
from .models import Order, Profile, User, Invoice
from .task import send_contact_email, send_quote_email, register_mail, invoice_generate
from .permissions import IsAdminRole, IsDriverUser


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
   

    serializer =RegisterSerializer(data=request.data)
    if serializer.is_valid():
        register=serializer.save()
        # register_mail.delay(
        #     register.email,
        #     register.last_name,
        #     register.first_name,
        #     register.role

        # )

        return Response({
            "data": serializer.data
        }, status =201)
    print(serializer.errors)
    return Response({
        "error":serializer.errors
    }, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def contact_view(request):
    try:
        name = request.data.get('name')
        number = request.data.get('number')
        mail = request.data.get('mail')
        message = request.data.get('message')

        # Validate required fields
        if not name or not number or not mail or not message:
            return Response({
                "success": False,
                "message": "All fields (name, number, mail, message) are required."
            }, status=400)

        # Trigger async task
        send_contact_email.delay(name, number, mail, message)

        return Response({
            "success": True,
            "message": "Message sent successfully."
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "success": False,
            "message": "Something went wrong.",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def request_quote(request):
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        order=serializer.save()
        # send_quote_email.delay(
        #     order.mail,
        #     order.name,
        #     order.number,
        #     order.message
        # )
        return Response({"success": True, "order": serializer.data}, status=status.HTTP_201_CREATED)
    print(serializer.errors)
    return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def track_order(request):
    tracking_id = request.data.get('tracking_id', '').strip()

    if not tracking_id:
        return Response(
            {"success": False, "message": "Tracking ID is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        order = Order.objects.get(id_number=tracking_id)

        start_loc = end_loc = None
        if order.route and ' - ' in order.route:
            start_loc, end_loc = order.route.split(' - ', 1)

        return Response({
            "success": True,
            "tracking_id": tracking_id,
            "driver":order.driver.first_name if order.driver else None,
            "order": {
                "id": order.id,
                "status": order.status,
                "route": order.route,
                "owner_name":order.owner_name,
               "pickup_time": order.pickup_time,          
                "delivery_time": order.delivery_time, 
                "service_type":order.service_type,
                "start_location": start_loc,
                "number_of_item":order.quantity,
                "end_location": end_loc,
            }
        }, status=status.HTTP_200_OK)

    except Order.DoesNotExist:
        return Response(
            {"success": False, "message": "No order found with that tracking ID"},
            status=status.HTTP_404_NOT_FOUND
        )





@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])

def profile(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = ProfileSerializer(
        profile,
        data=request.data,
        partial=True   # allows partial update
    )

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"success": True, "profile": serializer.data},
            status=status.HTTP_200_OK
        )

    return Response(
        {"success": False, "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminRole])
def make_admin(request, user_id):

    user = get_object_or_404(User, id=user_id)
  

    if user.role == "admin":
        return Response(
            {"message": "User is already an admin"},
            status=400
        )

    user.role = "admin"
    user.is_staff = True
    user.is_admin =True

    user.save()

    return Response(
        {
            "success": True,
            "message": f"{user.email} is now an admin"
        },
        status=200
    )
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def list_users(request):

    users = User.objects.select_related("profile").all()

    data = []
    for user in users:
        data.append({
            "id": user.id,
            "name": f"{user.first_name} {user.last_name}".strip(),
            "email": user.email,
            "role": user.role,
            "number": user.profile.number,
            "address": user.profile.address,
            "last_login": user.last_login,
            "is_active": user.is_active
        })

    return Response({"users": data}, status=200)

@api_view(['DELETE'])
@permission_classes([IsAdminRole])
def delete_user(request, user_id):

    if request.user.id == user_id:
        return Response(
            {"message": "You cannot delete your own account"},
            status=400
        )

    user = get_object_or_404(User, id=user_id)
    user.delete()  # Profile auto-deleted (CASCADE)

    return Response(
        {"success": True, "message": "User deleted successfully"},
        status=200
    )


# api/views.py

@api_view(["GET"])
@permission_classes([IsAdminRole])
def dashboard_summary(request):
    orders = Order.objects.all()
    total_pending = orders.filter(status="PENDING").count()
    total_progress = orders.filter(status="IN_PROGRESS").count()
    total_delivered = orders.filter(status="DELIVERED").count()
    total_cancelled = orders.filter(status="CANCELLED").count()

    active_drivers = User.objects.filter(is_active=True,role='driver').count()

    data = {
        "shipment_summary": {
            "pending": total_pending,
            "progress": total_progress,
            "delivered": total_delivered,
            "cancelled": total_cancelled
        },
        "driver_summary": {
            "active": active_drivers,
            "idle": 0
        },
        "orders": [
            {
                "id_number": order.id_number,
                "owner_name": order.owner_name,
                "route": order.route,
                "driver": order.driver.first_name if order.driver else None,
                "status": order.status
            }
            for order in orders
        ]
    }
    return Response(data)


#Shipment
@api_view(["GET"])
@permission_classes([IsAdminRole])
def shipments(request):
    # GET → list shipments
    if request.method == "GET":
        status_filter = request.query_params.get("status")

        orders = Order.objects.all().order_by("-created_at")

        if status_filter and status_filter != "All":
            orders = orders.filter(status=status_filter)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    # POST → create shipment
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@permission_classes([IsAdminRole])
def assign_driver_api(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    driver_id = request.data.get("driver_id")

    if driver_id in ["none", None]:
        order.driver = None
    else:
        try:
            driver = User.objects.get(id=driver_id)
            order.driver = driver
        except User.DoesNotExist:
            return Response({"detail": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)

    order.save()

    serializer = OrderSerializer(order)
    return Response({
        "message": "Driver assigned successfully",
        "order": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAdminRole])
def delete_shipment_api(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found"}, status=404)

    order.delete()
    return Response({"message": "Shipment deleted"})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def driver_list(request):
    """
    Returns all users with role='driver'
    """
    drivers = (
        User.objects
        .filter(role='driver')
        .select_related('profile')   # IMPORTANT
    )

    serializer = DriverSerializer(drivers, many=True)
    return Response(serializer.data)



@api_view(['GET', 'POST'])
def invoice_list_create(request):
    if request.method == 'GET':
        status_filter = request.query_params.get('status', None)  # Get status from query params
        invoices = Invoice.objects.all()
        
        if status_filter and status_filter != 'All':
            invoices = invoices.filter(status=status_filter)  # Filter by status if provided

        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = InvoiceSerializer(data=request.data)
        if serializer.is_valid():
            invoice=serializer.save()
            invoice_generate.delay(
                invoice.mail,
                invoice.customer,
                invoice.amount,
                invoice.issue_date,
                invoice.due_date,
                invoice.shipment_id
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Retrieve, update, or delete a single invoice
@api_view(['PUT', 'PATCH', 'DELETE'])
def invoice_detail(request, pk):
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        return Response({'detail': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
    
   
    if request.method == 'PUT':
        serializer = InvoiceSerializer(invoice, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PATCH':
        serializer = InvoiceSerializer(invoice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        invoice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def report_api(request):
    try:
        profile = Profile.objects.get(user=request.user)

        if profile.role != "admin":
            return Response(
                {"detail": "Only Admin can access this report"},
                status=403
            )

        drivers = User.objects.filter(profile__role="driver")

        labels = []
        orders_per_driver = []
        avg_times = []
        efficiencies = []

        for driver in drivers:
            labels.append(driver.first_name)

            driver_orders = Order.objects.filter(driver=driver)
            order_count = driver_orders.count()
            orders_per_driver.append(order_count)

            completed_orders = driver_orders.filter(
                pickup_time__isnull=False,
                delivery_time__isnull=False
            )

            if completed_orders.exists():
                total_minutes = sum(
                    (o.delivery_time - o.pickup_time).total_seconds() / 60
                    for o in completed_orders
                )
                avg_time = round(
                    total_minutes / completed_orders.count(), 2
                )
            else:
                avg_time = 0

            avg_times.append(avg_time)

            efficiency = round(
                (order_count / avg_time) * 10, 2
            ) if avg_time > 0 else 0

            efficiencies.append(efficiency)

        # Shipment volume by status
        all_orders = Order.objects.all()
        status_counter = Counter(
            o.status.title().strip()
            for o in all_orders if o.status
        )

        shipment_statuses = ["Delivered", "In Transit", "Delayed", "Failed"]
        shipment_counts = [
            status_counter.get(status, 0)
            for status in shipment_statuses
        ]

        return Response({
            "labels": labels,
            "orders_per_driver": orders_per_driver,
            "avg_times": avg_times,
            "efficiencies": efficiencies,
            "shipment_statuses": shipment_statuses,
            "shipment_counts": shipment_counts,
        })

    except Profile.DoesNotExist:
        return Response(
            {"detail": "Profile not found"},
            status=404
        )


@api_view(['GET', 'PATCH'])
@permission_classes([IsDriverUser])
def driver_orders_api(request):
    """
    GET: List all orders assigned to the logged-in driver.
    PATCH: Update the status of a specific order assigned to this driver.
    """
    user = request.user  # Logged-in User instance

    if request.method == 'GET':
        # Fetch orders assigned to this driver
        status_filter = request.query_params.get("status")
        orders = Order.objects.filter(driver=user, status=status_filter)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PATCH':
        order_id = request.data.get('order_id')
        new_status = request.data.get('status')

        if not order_id or not new_status:
            return Response(
                {"detail": "order_id and status are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure the order exists and belongs to this driver
        order_instance = get_object_or_404(Order, id=order_id, driver=user)

        # Update order status
        order_instance.status = new_status

        # Set delivery_time if delivered, otherwise clear
        if new_status == "DELIVERED":
            order_instance.delivery_time = timezone.now()
            # Call your Celery task if needed
            # delivered.delay(order_instance.id)
        elif new_status == "IN_PROGRESS":
             order_instance.delivery_time = timezone.now()
            # delivered.delay(order_instance.id)
         
        elif new_status == "CANCELLED":
            pass
        else:
            order_instance.delivery_time = None

        # Save changes
        order_instance.save()

        serializer = OrderSerializer(order_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'PATCH'])
@permission_classes([IsAdminRole])
def all_orders_api(request):
    """
    GET: List all orders assigned to the logged-in driver.
    PATCH: Update the status of a specific order assigned to this driver.
    """
 

    if request.method == 'GET':
        # Fetch orders assigned to this driver
        orders = Order.objects.all().order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PATCH':
        order_id = request.data.get('order_id')
        new_status = request.data.get('status')

        if not order_id or not new_status:
            return Response(
                {"detail": "order_id and status are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure the order exists and belongs to this driver
        order_instance = get_object_or_404(Order, id=order_id)

        # Update order status
        order_instance.status = new_status

        # Set delivery_time if delivered, otherwise clear
        if new_status == "Delivered":
            order_instance.delivery_time = timezone.now()
            # Call your Celery task if needed
            # delivered.delay(order_instance.id)
        elif new_status == "In Progress":
            # delivered.delay(order_instance.id)
            pass
        elif new_status == "Cancelled":
            pass
        else:
            order_instance.delivery_time = None

        # Save changes
        order_instance.save()

        serializer = OrderSerializer(order_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
        
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=400)
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Logout successful"})
    except Exception as e:
        print(str(e))
        return Response({"error": str(e)}, status=400)
       
