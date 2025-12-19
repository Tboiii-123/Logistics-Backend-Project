from django.db import models, transaction

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
          

import datetime



class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
          



class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('driver', 'Driver'),
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='driver'
    )

    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin =models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

               
class Profile(models.Model):
            
            #Linking the fk to the use models that is imported
            user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    
            number =models.CharField(max_length=200,blank=True,null=True)
        
            address =models.CharField(max_length=200, blank=True,null=True)
        
            dob =models.DateField(blank=True, null=True)
            
            
             
            last_active = models.DateTimeField(null=True, blank=True)
          
            profile_img  =models.ImageField(upload_to='profile',default ='blank.png',blank=True,null=True)
            completed_deliveries = models.PositiveIntegerField(default=0)
            is_available = models.BooleanField(default=True)
            vehicle_number = models.CharField(max_length=50, blank=True, null=True)
            vehicle_type = models.CharField(max_length=50, blank=True, null=True)




            def __str__(self):
                    
                    return self.user.email 
            





# class Driver(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
        
        
#     profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True)
#     vehicle =models.CharField(max_length=200, blank=True, null=True)
#     status =models.CharField(max_length=200, blank=True, null=True)
    
    
    
    
#     list_of_order =models.IntegerField(default=0,null=True, blank=True)
#     delivered_today = models.IntegerField(default=0,null=True, blank=True)
   

    
#     def __str__(self):
#         return str(self.user)  # or self
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('DELIVERED', 'Delievered'),
        ('IN_PROGRESS', 'In Progress'),

        ('CANCELLED', 'Cancelled'),
    ]

    id_number = models.CharField(max_length=200, null=False, blank=False)
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    name = models.CharField(max_length=200, null=True, blank=True)
    route = models.CharField(max_length=200,null=True, blank=True)
    pickup_time = models.DateTimeField(null=True,blank=True)
    quantity = models.IntegerField(default=1,null=True, blank=True)

    owner_name = models.CharField(max_length=200, blank=True, null=True)
    delivery_time =models.DateTimeField(null=True,blank=True)
    status =models.CharField(max_length=200,choices=STATUS_CHOICES,default='PENDING')
    service_type =models.CharField(max_length=200,null=True,blank=True)
    mail =models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id_number:
            self.id_number = self.generate_custom_id()
        super().save(*args, **kwargs)


    @staticmethod
    def generate_custom_id():
        with transaction.atomic():
            # Lock the last order row to avoid race conditions
            last_order = Order.objects.select_for_update().order_by('id').last()
            if not last_order or not last_order.id_number:
                return 'ST-8000'
            last_id = int(last_order.id_number.split('-')[1])
            return f"ST-{last_id + 1}"
    
    
    

    def __str__(self):
        return self.name
import uuid   
    
class Invoice(models.Model):
      invoice_id = models.UUIDField(default=uuid.uuid4,  editable=False,unique=True)
      STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
        ('Overdue', 'Overdue'),
    ]

      shipment_id=models.CharField(max_length=200, null=True , blank=True)
      customer =models.CharField(max_length=200, null=True , blank=True)
      amount =models.IntegerField(default=1,null=True, blank=True)
      issue_date=models.DateTimeField(default=datetime.datetime.today,null=True,blank=True)
      due_date =models.DateTimeField(default=datetime.datetime.today,null=True,blank=True)
      status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unpaid')
      note =models.CharField(max_length=200,null=True,blank=True)
      mail =models.EmailField(blank=True, null=True)


      
      def __str__(self):
        return self.customer
    
      

