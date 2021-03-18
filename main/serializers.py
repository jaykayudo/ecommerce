from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['shipping_name',
        'shipping_address1',
        'shipping_address2',
        'shipping_zip_code',
        'shipping_city',
        'shipping_country',
        'date_updated',
        'date_added']