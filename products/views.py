from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product
from .forms import ProductForm

def product_list(request):
    if request.user.is_authenticated:
        products = Product.objects.all().order_by("-created_at")

        # Handle Add
        if request.method == "POST" and "add_product" in request.POST:
            form = ProductForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Product added successfully.")
                return redirect("product-list")
        else:
            form = ProductForm()

        # Handle Update
        if request.method == "POST" and "update_product" in request.POST:
            product_id = request.POST.get("product_id")
            product = get_object_or_404(Product, pk=product_id)
            form_update = ProductForm(request.POST, instance=product)
            if form_update.is_valid():
                form_update.save()
                messages.success(request, "Product updated successfully.")
                return redirect("product-list")
        else:
            form_update = ProductForm()

        return render(
            request,
            "company/product_list.html",
            {"products": products, "form": form, "form_update": form_update}
        )
    else:
        messages.error(request, "You must login first to access the page")
        return redirect("login")


def product_detail(request, pk):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=pk)
        return render(request, "company/product_detail.html", {"product": product})
    else:
        messages.error(request, "You must login first to access the page")
        return redirect("login")


def product_delete(request, pk):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=pk)
        if request.method == "POST":
            product.delete()
            messages.success(request, "Product deleted successfully.")
            return redirect("product-list")
        return render(request, "company/product_confirm_delete.html", {"product": product})
    else:
        messages.error(request, "You must login first to access the page")
        return redirect("login")
