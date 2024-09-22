from datetime import date

from rest_framework import serializers
from .models import *


class ProductCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCompany
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['company_name', 'product_model', 'date_on_market']

    def validate_release_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Дата выхода продукта не может быть в будущем.")
        return value


class RetailObjectSerializer(serializers.ModelSerializer):
    # retail_country = serializers.CharField()
    retail_products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True)

    class Meta:
        model = RetailObject
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.retail_type = validated_data.get('retail_type', instance.retail_type)
        instance.retail_email = validated_data.get('retail_email', instance.retail_email)
        instance.retail_name = validated_data.get('retail_name', instance.retail_name)
        instance.retail_city = validated_data.get('retail_city', instance.retail_city)
        instance.retail_street = validated_data.get('retail_street', instance.retail_street)
        instance.retail_building = validated_data.get('retail_building', instance.retail_building)
        instance.retail_country = validated_data.get('retail_country', instance.retail_country)
        instance.retail_supplier = validated_data.get('retail_supplier', instance.retail_supplier)
        validated_data.pop('retail_date', None)
        instance.retail_products.set(validated_data.get('retail_products', instance.retail_products.all()))
        instance.save()
        return instance

    def validate_retail_name(self, value):
        if len(value) > 50:
            raise serializers.ValidationError("Название сети не может превышать 50 символов.")
        return value


class GenerateQrRequestSerializer(serializers.Serializer):
    retail_object_id = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)
