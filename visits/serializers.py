from rest_framework import serializers
from .models import Visit
from customers.models import CustomerContact
from .utils import get_location_name  # your existing reverse geocode function
from sales.models import Sales

class VisitSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    designation = serializers.CharField(source='company.designation', read_only=True)
    contact_person_name = serializers.CharField(source='contact_person.contact_name', read_only=True)
    contact_person_detail = serializers.CharField(source='contact_person.contact_detail', read_only=True)
    acquisition_stage = serializers.CharField(source='company.acquisition_stage', read_only=True)
    client_budget = serializers.DecimalField(source='company.client_budget', max_digits=15, decimal_places=2, read_only=True)
    products_interested = serializers.SerializerMethodField()

    latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )
    longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )

    place_name = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    zone = serializers.SerializerMethodField()
    nation = serializers.SerializerMethodField()

    class Meta:
        model = Visit
        fields = [
            'id',
            'company',
            'company_name',
            'designation',
            'acquisition_stage',
            'client_budget',
            'products_interested',
            'contact_person',
            'contact_person_name',
            'contact_person_detail',
            'item_discussed',
            'meeting_type',
            'latitude',
            'longitude',
            'place_name',
            'region',
            'zone',
            'nation',
            'visit_image',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'status',
            'company_name',
            'designation',
            'contact_person_name',
            'contact_person_detail',
            'acquisition_stage',
            'client_budget',
            'products_interested',
            'place_name',
            'region',
            'zone',
            'nation',
        ]

    def get_place_name(self, obj):
        if obj.latitude and obj.longitude:
            return get_location_name(obj.latitude, obj.longitude)["place_name"]
        return "Not Available"

    def get_region(self, obj):
        if obj.latitude and obj.longitude:
            return get_location_name(obj.latitude, obj.longitude)["region"]
        return ""

    def get_zone(self, obj):
        if obj.latitude and obj.longitude:
            return get_location_name(obj.latitude, obj.longitude)["zone"]
        return ""

    def get_nation(self, obj):
        if obj.latitude and obj.longitude:
            return get_location_name(obj.latitude, obj.longitude)["nation"]
        return ""

    def get_products_interested(self, obj):
        if obj.company and hasattr(obj.company, 'sales'):
            sales = getattr(obj.company, 'sales').first()
            if sales:
                return [pi.product.name for pi in sales.product_interests.all()]
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



from rest_framework import serializers
from .models import Visit
from customers.models import Customer
from sales.models import Sales
from products.models import Product, ProductInterest

# Map the progression of acquisition stages
NEXT_STAGE_MAP = {
    "Prospecting": "Qualifying",
    "Qualifying": "Proposal or Negotiation",
    "Proposal or Negotiation": "Closing",
    "Closing": "Payment Followup",
    "Payment Followup": None,
}

class VisitUpdateSerializer(serializers.ModelSerializer):
    # Accept product IDs from Product table
    product_interests = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        many=True,
        write_only=True,
        required=False
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
            'item_discussed',
            'meeting_type',
            'visit_image',
            'latitude',
            'longitude',
            'product_interests',
            'client_budget',
        ]

    def update(self, instance, validated_data):
            customer = instance.company
            if not customer:
                raise serializers.ValidationError("Visit must be linked to a company to update sales.")

            current_stage = customer.acquisition_stage
            next_stage = NEXT_STAGE_MAP.get(current_stage)

            # Always allow updating client_budget and products if stage is Qualifying
            client_budget = validated_data.pop('client_budget', None)
            products = validated_data.pop('product_interests', None)

            if current_stage == "Prospecting":
                # Moving from Prospecting → Qualifying requires both
                if client_budget is None:
                    raise serializers.ValidationError({"client_budget": "Client budget is required to move to Qualifying."})
                if not products:
                    raise serializers.ValidationError({"product_interests": "At least one product must be selected to move to Qualifying."})

                # Update stage
                customer.acquisition_stage = "Qualifying"

            # If already Qualifying, just update client_budget/products if provided
            if client_budget is not None:
                customer.client_budget = client_budget
            customer.save()

            if products:
                sales, created = Sales.objects.get_or_create(customer=customer)
                interest_objs = []
                for product in products:
                    pi, created = ProductInterest.objects.get_or_create(product=product)
                    interest_objs.append(pi)
                sales.product_interests.set(interest_objs)
                sales.save()

            # Update Visit fields normally
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            return instance
