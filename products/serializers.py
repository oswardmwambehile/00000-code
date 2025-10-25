from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        name = validated_data.get('name')
       
        product = Product.objects.filter(name__iexact=name).first()
        if product:
            return product  
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        name = validated_data.get('name', instance.name)
        if Product.objects.exclude(id=instance.id).filter(name__iexact=name).exists():
            raise serializers.ValidationError({"name": "Product with this name already exists."})
        instance.name = name
        instance.save()
        return instance
