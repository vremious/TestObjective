from datetime import date

from rest_framework import serializers

from .models import *


class ProductCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCompany
        fields = '__all__'


# Сериализатор продукции с функционалом создания, обновления и валидацией
class ProductSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField()

    class Meta:
        model = Product
        fields = ['company_name', 'product_model', 'date_on_market']

    def create(self, validated_data):
        company_name = validated_data.pop('company_name')
        company, created = ProductCompany.objects.get_or_create(company_name=company_name)
        validated_data['company_name'] = company
        product = Product.objects.create(**validated_data)
        return product

    def update(self, instance, validated_data):
        company_name = validated_data.pop('company_name')
        company, created = ProductCompany.objects.get_or_create(company_name=company_name)
        validated_data['company_name'] = company
        instance.company_name = validated_data['company_name']
        instance.product_model = validated_data.get('product_model', instance.product_model)
        instance.date_on_market = validated_data.get('date_on_market', instance.date_on_market)
        instance.save()
        return instance

    def validate_release_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Дата выхода продукта не может быть в будущем.")
        return value


# Сериализатор объектов ретейла с функционалом создания, обновления и валидацией
class RetailObjectSerializer(serializers.ModelSerializer):
    retail_country = serializers.CharField()
    retail_products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True)

    class Meta:
        model = RetailObject
        fields = '__all__'

    def create(self, validated_data):
        country_name = validated_data.pop('retail_country')
        country, created = Country.objects.get_or_create(name=country_name)
        validated_data['retail_country'] = country
        retail_products = validated_data.pop('retail_products')
        retail_object = RetailObject.objects.create(**validated_data)
        retail_object.retail_products.set(retail_products)
        return retail_object

    def update(self, instance, validated_data):
        country_name = validated_data.pop('retail_country')
        country, created = Country.objects.get_or_create(name=country_name)
        validated_data['retail_country'] = country
        instance.retail_type = validated_data.get('retail_type', instance.retail_type)
        instance.retail_email = validated_data.get('retail_email', instance.retail_email)
        instance.retail_name = validated_data.get('retail_name', instance.retail_name)
        instance.retail_city = validated_data.get('retail_city', instance.retail_city)
        instance.retail_street = validated_data.get('retail_street', instance.retail_street)
        instance.retail_building = validated_data.get('retail_building', instance.retail_building)
        instance.retail_country = validated_data['retail_country']
        instance.retail_supplier = validated_data.get('retail_supplier', instance.retail_supplier)
        validated_data.pop('retail_date', None)
        instance.retail_products.set(validated_data.get('retail_products', instance.retail_products.all()))
        instance.save()
        return instance

    def validate_retail_name(self, value):
        if value is None:
            value = 0
        if len(value) > 50:
            raise serializers.ValidationError("Название сети не может превышать 50 символов.")
        return value

    def validate_retail_debt(self, value):
        if value < 0:
            raise serializers.ValidationError("Задолженность не должна  быть меньше нуля")
        return value


# Сериализатор для QR кода
class GenerateQrRequestSerializer(serializers.Serializer):
    retail_object_id = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)
