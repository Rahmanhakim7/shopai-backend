from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from core.pagination import DefaultPagination
from django.db.models import Q

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_list(request):
    products = Product.objects.all()
    pagination = DefaultPagination()
    paginated_products = pagination.paginate_queryset(products, request)
    serializer = ProductSerializer(
        paginated_products,
        many=True
    )
    return pagination.get_paginated_response({
        "status": "success",
        "data": serializer.data
    }, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_detail(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk
    )
    serializer = ProductSerializer(product)
    return Response({
        "status": "success",
        "data": serializer.data
    }, status=200)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def seller_products(request):
    if request.user.role != 'seller':
        return Response({
            "message": "Hanya seller yang bisa mengakses halaman ini"
        }, status=403)
    if request.method == 'GET':
        products = Product.objects.filter(
            seller=request.user
        )
        search = request.GET.get('search')
        if search:
            products = products.filter(
                Q(name__icontains=search)
            )
        status = request.GET.get('status')
        print(request.GET)
        print(status)       
        if status:
            products = products.filter(
                status=status
            )
        pagination = DefaultPagination()
        paginated_products = pagination.paginate_queryset(
            products,
            request
        )
        serializer = ProductSerializer(
            paginated_products,
            many=True
        )
        return pagination.get_paginated_response({
            "status": "success",
            "data": serializer.data
        })
    if request.method == 'POST':
        serializer = ProductSerializer(
            data=request.data
        )
        if serializer.is_valid():
            serializer.save(
                seller=request.user
            )
            return Response({
                "message": "Data Berhasil Ditambahkan",
                "status": "success",
                "data": serializer.data
            }, status=201)
        return Response({
            "message": "Data Gagal Ditambahkan",
            "status": "error",
            "errors": serializer.errors
        }, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def seller_product_detail(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk
    )
    if request.user != product.seller:
        return Response({
            "message": "Kamu bukan pemilik produk ini"
        }, status=403)
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=200)
    if request.method == 'PUT':
        serializer = ProductSerializer(
            product,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save(
                seller=product.seller
            )
            return Response({
                "message": "Data Berhasil Di Update",
                "status": "success",
                "data": serializer.data
            }, status=200)
        return Response({
            "message": "Data Gagal Di Update",
            "status": "error",
            "errors": serializer.errors
        }, status=400)
    if request.method == 'DELETE':
        product.delete()
        return Response({
            "message": "Data Berhasil Di Hapus",
            "status": "success"
        }, status=200)