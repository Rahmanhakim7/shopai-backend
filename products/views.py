from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        if request.user.role != 'seller':
            return Response({
                "message": "Hanya seller yang boleh menambahkan product"
            }, status=403)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Response({
                "message": "Data Berhasil Di Tambahkan",
                "data": serializer.data,
                "status": "success"
            }, status=201)
        return Response({
            "status": "error",
            "error": serializer.errors
        }, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    if request.method == 'PUT':
        if request.user != product.seller:
            return Response({
                "message": "Kamu bukan pemilik produk ini"
            }, status=403)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save(seller=product.seller)
            return Response({
                "message": "Data Berhasil di Update",
                "status": "Success",
                "data": serializer.data
            }, status=200)
        return Response({
            "message": "Data Gagal Di Update",
            "errors": serializer.errors
        }, status=400)
    if request.method == 'DELETE':
        if request.user != product.seller:
            return Response({
                "message": "Kamu bukan pemilik produk ini"
            }, status=403)
        product.delete()
        return Response({
            "message": "Data Berhasil Di Hapus",
            "status": "Succes"
        }, status=201)
