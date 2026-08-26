from rest_framework.pagination import PageNumberPagination

class DefaultPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

class WishlistPagination(DefaultPagination):
    page_size = 8

class AdminUsersPagination(DefaultPagination):
    page_size = 6