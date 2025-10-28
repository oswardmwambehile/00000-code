from rest_framework import serializers
from .models import Customer, CustomerContact


class CustomerContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerContact
        fields = ['id', 'contact_name', 'contact_detail']


class CustomerSerializer(serializers.ModelSerializer):
    contacts = CustomerContactSerializer(many=True, required=False)

    designation = serializers.ChoiceField(
        choices=[('Owner', 'Owner'), ('Engineer', 'Engineer'), ('Contractor', 'Contractor')],
        required=False,
        allow_blank=True
    )

    customer_type = serializers.ChoiceField(
        choices=[('Individual', 'Individual'), ('Company', 'Company')],
        default='Individual'
    )

    class Meta:
        model = Customer
        fields = [
            'id',
            'designation',
            'company_name',
            'location',
            'customer_type',
            'email',
            'created_at',
            'contacts',
        ]
        read_only_fields = ['created_at']

    def create(self, validated_data):
        contacts_data = validated_data.pop('contacts', [])
        customer = Customer.objects.create(**validated_data)

        for contact_data in contacts_data:
            CustomerContact.objects.create(customer=customer, **contact_data)

        return customer

    def update(self, instance, validated_data):
        contacts_data = validated_data.pop('contacts', [])

        email = validated_data.get('email', instance.email)
        if Customer.objects.exclude(id=instance.id).filter(email=email).exists():
            email = instance.email

        instance.designation = validated_data.get('designation', instance.designation)
        instance.company_name = validated_data.get('company_name', instance.company_name)
        instance.location = validated_data.get('location', instance.location)
        instance.customer_type = validated_data.get('customer_type', instance.customer_type)
        instance.email = email
        instance.save()

        existing_contacts = {c.id: c for c in instance.contacts.all()}
        phone_map = {c.contact_detail: c for c in instance.contacts.all()}

        for contact_data in contacts_data:
            contact_id = contact_data.get('id')
            contact_detail = contact_data.get('contact_detail')

            if contact_id and contact_id in existing_contacts:
                contact = existing_contacts[contact_id]
                contact.contact_name = contact_data.get('contact_name', contact.contact_name)
                contact.contact_detail = contact_detail
                contact.save()
            elif contact_detail and contact_detail in phone_map:
                contact = phone_map[contact_detail]
                contact.contact_name = contact_data.get('contact_name', contact.contact_name)
                contact.save()

        return instance
