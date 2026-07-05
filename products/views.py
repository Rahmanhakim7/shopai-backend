from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from core.pagination import DefaultPagination
from utils.api_response import success_response
from shopai.permissions import IsBuyer,IsSeller


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsBuyer])
def product_list(request):
    products = Product.objects.all()
    stock_filter = request.GET.get("stock_filter")
    condition = request.GET.get("condition")

    if stock_filter == "in_stock":
        products = products.filter(stock__gt=0)
    elif stock_filter == "out_of_stock":
        products = products.filter(stock=0)
    if condition:
        products = products.filter(condition=condition)
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search)
        )
    ordering = request.GET.get("ordering", "latest")
    allowed_ordering = {
        "latest": "-created_at",
        "price_asc": "price",
        "price_desc": "-price",
        "name_asc": "name",
        "name_desc": "-name",
    }
    products = products.order_by(
        allowed_ordering.get(ordering, "-created_at")
    )
    paginator = PageNumberPagination()
    paginator.page_size = 2
    result_page = paginator.paginate_queryset(
        products,
        request
    )
    serializer = ProductSerializer(
        result_page,
        many=True
    )
    paginated_data = {
        "count": paginator.page.paginator.count,
        "next": paginator.get_next_link(),
        "previous": paginator.get_previous_link(),
        "results": serializer.data
    }
    return success_response(
        data=paginated_data,
        message="Products fetched successfully"
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsBuyer])
def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("seller"),
        pk=pk
    )
    serializer = ProductSerializer(product)
    return success_response(
        data=serializer.data,
        message="Product fetched successfully"
    )

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsSeller])
def seller_products(request):
    if request.method == 'GET':
        products = Product.objects.filter(
            seller=request.user
        )
        search = request.GET.get('search')
        if search:
            products = products.filter(
                Q(name__icontains=search)
            )
        status_filter = request.GET.get('status')       
        if status_filter:
            products = products.filter(
                status=status_filter
            )
        ordering = request.GET.get('ordering')
        allowed_ordering = ['price', '-price', 'stock', '-stock']
        if ordering in allowed_ordering:
            products = products.order_by(ordering)
        else:
            products = products.order_by('-id')
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
@permission_classes([IsAuthenticated, IsSeller])
def seller_product_detail(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        seller=request.user
    )
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