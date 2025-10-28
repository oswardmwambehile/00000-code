from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer

# ----------------------
# List all products
# ----------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_list(request):
    """
    GET: List all products.
    Only accessible to authenticated users.
    """
    products = Product.objects.all().order_by('-created_at')
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# ----------------------
# Create a product
# ----------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def product_create(request):
    """
    POST: Create a new product.
    Only accessible to authenticated users.
    """
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ----------------------
# Retrieve a single product
# ----------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_detail(request, pk):
    """
    GET: Retrieve a single product.
    Only accessible to authenticated users.
    """
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product)
    return Response(serializer.data)

# ----------------------
# Update a product
# ----------------------
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def product_update(request, pk):
    """
    PUT/PATCH: Update a product.
    Only accessible to authenticated users.
    """
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ----------------------
# Delete a product
# ----------------------
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def product_delete(request, pk):
    """
    DELETE: Delete a product.
    Only accessible to authenticated users.
    """
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
