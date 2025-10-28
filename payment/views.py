from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from sales.models import Sales
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from sales.models import Sales

@login_required
def sales_list(request):
    if request.user.is_authenticated:
        """
        Display all sales created by the logged-in user,
        including company details and sales items.
        """
        sales = Sales.objects.filter(added_by=request.user).select_related(
            'company', 'added_by'
        ).prefetch_related(
            'items', 'items__product', 'items__payments'
        )

        # Calculate total paid and remaining per sale item
        for sale in sales:
            for item in sale.items.all():
                item.total_paid = item.payments.aggregate(total=Sum('amount'))['total'] or 0
                item.remaining = (item.price or 0) - item.total_paid

        context = {'sales': sales}
        return render(request, 'users/sales_list.html', context)
    else:
        messages.error(request, "You must login first to access the page")
        return redirect("login")




def sales_detail(request, sale_id):
    if request.user.is_authenticated:
            """
            Show details of a single sale including products, price, paid, remaining, and totals.
            """

            sale = Sales.objects.filter(id=sale_id, added_by=request.user).prefetch_related(
                'items', 'items__product', 'items__payments'
            ).select_related('company').first()

            if not sale:
                messages.error(request, "Sale not found or you don't have access.")
                return redirect('sales_list')

            total_amount = 0
            total_paid = 0
            for item in sale.items.all():
                item.total_paid = item.payments.aggregate(total=Sum('amount'))['total'] or 0
                item.remaining = (item.price or 0) - item.total_paid
                total_amount += item.price or 0
                total_paid += item.total_paid

            remaining_total = total_amount - total_paid

            context = {
                'sale': sale,
                'total_amount': total_amount,
                'total_paid': total_paid,
                'remaining_total': remaining_total,
            }
            return render(request, 'users/sales_detail.html', context)
    else:
        messages.error(request, "You must login first to access the page")
        return redirect("login")

