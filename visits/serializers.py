from rest_framework import serializers
from .models import Visit
from customers.models import CustomerContact
from .utils import get_location_name
from sales.models import Sales, SalesItem
from django.core.cache import cache
from products.models import ProductInterest, Product  # included Product for update serializer

# --------------------- VisitSerializer ---------------------
class VisitSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    designation = serializers.CharField(source='company.designation', read_only=True)
    contact_person_name = serializers.CharField(source='contact_person.contact_name', read_only=True)
    contact_person_detail = serializers.CharField(source='contact_person.contact_detail', read_only=True)
    acquisition_stage = serializers.CharField(source='company.acquisition_stage', read_only=True)
    client_budget = serializers.DecimalField(source='company.client_budget', max_digits=15, decimal_places=2, read_only=True)
    products_interested = serializers.SerializerMethodField()
    sales_items = serializers.SerializerMethodField()

    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)

    place_name = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    zone = serializers.SerializerMethodField()
    nation = serializers.SerializerMethodField()

    class Meta:
        model = Visit
        fields = [
            'id', 'company', 'company_name', 'designation', 'acquisition_stage',
            'client_budget', 'products_interested', 'sales_items',
            'contact_person', 'contact_person_name', 'contact_person_detail',
            'item_discussed', 'meeting_type', 'latitude', 'longitude',
            'place_name', 'region', 'zone', 'nation', 'visit_image',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'status', 'company_name',
            'designation', 'contact_person_name', 'contact_person_detail',
            'acquisition_stage', 'client_budget', 'products_interested',
            'sales_items', 'place_name', 'region', 'zone', 'nation',
        ]

    def get_location_data(self, obj):
        if not (obj.latitude and obj.longitude):
            return {"place_name": "Not Available", "region": "", "zone": "", "nation": ""}

        cache_key = f"visit_location_{obj.latitude}_{obj.longitude}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            data = get_location_name(obj.latitude, obj.longitude)
            cache.set(cache_key, data, timeout=60 * 60 * 24)
            return data
        except Exception:
            return {"place_name": "Unavailable", "region": "", "zone": "", "nation": ""}

    def get_place_name(self, obj):
        return self.get_location_data(obj)["place_name"]

    def get_region(self, obj):
        return self.get_location_data(obj)["region"]

    def get_zone(self, obj):
        return self.get_location_data(obj)["zone"]

    def get_nation(self, obj):
        return self.get_location_data(obj)["nation"]

    def get_products_interested(self, obj):
        """
        Return products related to the latest sales record for this visit's company.
        Returns list of objects: {id, product_name}.
        """
        if obj.company:
            sales = Sales.objects.filter(customer=obj.company).order_by('-id').first()  # latest sale
            if sales:
                return [
                    {
                        "id": pi.id,
                        "product_name": pi.product.name if pi.product else "Unnamed Product"
                    }
                    for pi in sales.product_interests.all()
                ]
        return []

    def get_sales_items(self, obj):
        """
        Return the existing sales items for the latest sales record for this visit's company with prices.
        """
        sales = Sales.objects.filter(customer=obj.company).order_by('-id').first()  # latest sale
        if sales:
            return [
                {
                    "product": item.product.id if item.product else None,
                    "price": item.price
                }
                for item in sales.items.all()
            ]
        return []

    def validate(self, data):
        company = data.get('company')
        existing_visit = Visit.objects.filter(company=company, status="Open").first()
        if existing_visit:
            added_by = str(existing_visit.added_by) if existing_visit.added_by else "Unknown user"
            raise serializers.ValidationError({
                "company": f"A visit for this company already exists, added by {added_by}."
            })
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        validated_data['added_by'] = user
        validated_data['sales'] = None
        return super().create(validated_data)


# --------------------- VisitUpdateSerializer ---------------------
NEXT_STAGE_MAP = {
    "Prospecting": "Qualifying",
    "Qualifying": "Proposal or Negotiation",
    "Proposal or Negotiation": "Closing",
    "Closing": "Payment Followup",
    "Payment Followup": None,
}

class VisitUpdateSerializer(serializers.ModelSerializer):
    product_interests = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    available_products = serializers.SerializerMethodField(read_only=True)
    contact_person = serializers.PrimaryKeyRelatedField(
        queryset=CustomerContact.objects.all(),
        required=False,
        allow_null=True
    )
    client_budget = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        write_only=True
    )

    class Meta:
        model = Visit
        fields = [
            'item_discussed', 'meeting_type', 'visit_image',
            'latitude', 'longitude', 'contact_person',
            'product_interests', 'available_products', 'client_budget',
        ]

    def get_available_products(self, obj):
        return [{"id": p.id, "name": p.name} for p in Product.objects.all()]

    def update(self, instance, validated_data):
        customer = instance.company
        if not customer:
            raise serializers.ValidationError("Visit must be linked to a company to update sales.")

        current_stage = customer.acquisition_stage
        next_stage = NEXT_STAGE_MAP.get(current_stage)

        client_budget = validated_data.pop('client_budget', None)
        products = validated_data.pop('product_interests', None)

        if current_stage == "Prospecting":
            if client_budget is None:
                raise serializers.ValidationError({"client_budget": "Client budget is required to move to Qualifying."})
            if not products:
                raise serializers.ValidationError({"product_interests": "At least one product must be selected to move to Qualifying."})
            customer.acquisition_stage = "Qualifying"

        if client_budget is not None:
            customer.client_budget = client_budget
        customer.save()

        if products:
            sales = Sales.objects.filter(customer=customer).order_by('-id').first()
            if not sales:
                sales = Sales.objects.create(customer=customer)

            interest_objs = []
            for product in products:
                pi, _ = ProductInterest.objects.get_or_create(product=product)
                interest_objs.append(pi)
            sales.product_interests.set(interest_objs)
            sales.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
