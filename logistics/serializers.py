from rest_framework import serializers
from .models import User,Order,Profile,Invoice
from django.contrib.auth.password_validation import validate_password






class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
   

    class Meta:
        model = User
        fields = ('id','first_name','last_name','email','password')

    def create(self, validated_data):
        user = User( 
        email=validated_data['email'],
         first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
            )
        user.set_password(validated_data['password'])
       
        user.save()
        return user




class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', required=False)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    role = serializers.CharField(source='user.role', required=False)
    

    class Meta:
        model = Profile
        fields = (
            'profile_img',
            'first_name',
            'last_name',
            'number',
            'address',
            'email',
            'role'
        )

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        # Update user fields if provided
        if 'email' in user_data:
            user.email = user_data['email']
        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']
        user.save()

        # Update profile fields
        return super().update(instance, validated_data)


class DriverSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    delivered_today = serializers.SerializerMethodField()
    vehicle_type = serializers.EmailField(source='user.vehicle_type', required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "profile",
            "vehicle_type",
            "delivered_today",
        ]

    def get_delivered_today(self, obj):
        """
        If you don't yet track deliveries per day,
        return completed_deliveries for now
        """
        if hasattr(obj, "profile") and obj.profile:
            return obj.profile.completed_deliveries
        return 0



class OrderSerializer(serializers.ModelSerializer):
    id_number = serializers.CharField(read_only=True)
    pick_up = serializers.CharField(write_only=True, required=False)
    destination = serializers.CharField(write_only=True, required=False)
    driver = DriverSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        pick_up = validated_data.pop('pick_up', None)
        destination = validated_data.pop('destination', None)
        if pick_up and destination:
            validated_data['route'] = f"{pick_up} - {destination}"
        return Order.objects.create(**validated_data)






class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'id',       
            'shipment_id',
            'customer',
            'amount',
            'issue_date',
            'due_date',
            'status',
            'note',
            'mail'
        ]
