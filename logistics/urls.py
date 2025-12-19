
from  django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
      path('auth/register/', views.register_view, name='register'),
    #Return access token ad refresh token
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

     path('auth/logout/', views.logout_view, name='logout_view'),

    path('request_quote/', views.request_quote, name='request_quote'),
    
    path('contact/', views.contact_view, name='contact_view'),
   
     path('drivers/', views.driver_list, name='drivers'),
     path('profile/', views.profile, name='profile'),
  
     path('delete_users/<int:user_id>', views.delete_user, name='delete_user'),
       path('shipments/', views.shipments, name='shipments'),  
       path('dashboard/', views.dashboard_summary, name='dashboard_summary'),  
    path('shipments/<int:order_id>/assign_driver/', views.assign_driver_api, name='assign_driver'),
  path('shipments/<int:order_id>/delete/',views.delete_shipment_api,name="delete_shipment"),
path('invoices/', views.invoice_list_create, name='invoice_create'),

    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path("api/report/", views.report_api, name="report-api"),

  path("users/", views.list_users, name="list-users"),
path("users/<int:user_id>/make-admin/",views.make_admin, name="make-admin"),
path("users/<int:user_id>/",views.delete_user, name="delete_user"),
 path('driver/orders/', views.driver_orders_api, name='driver_orders_api'),
 path('all/orders/', views.all_orders_api, name='all_orders_api'),
   path('order/track/', views.track_order, name='track_order'),

    ]

    