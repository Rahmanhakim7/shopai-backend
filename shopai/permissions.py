from rest_framework.permissions import BasePermission

class IsBuyer(BasePermission):
    message = "Hanya buyer yang dapat mengakses endpoint ini."
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "buyer"
        )

class IsSeller(BasePermission):
    message = "Hanya seller yang dapat mengakses endpoint ini."
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "seller"
        )