from rest_framework.permissions import BasePermission

class CanSendEmailPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('tasks.can_send_email')

class CanDeleteEmailPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('tasks.can_delete_email')

class CanViewEmailPermission(BasePermission):
    def has_permission(self, request, view):
        # Example: Allow viewing if the user has 'can_view_email' permission
        return request.user.has_perm('tasks.can_view_email')
    
class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='User').exists()

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Admin').exists()
    
class IsUserOrAdmin(BasePermission):
    def has_permission(self, request, view):
        is_user = request.user.groups.filter(name='User').exists()
        is_admin = request.user.groups.filter(name='Admin').exists()
        return is_user or is_admin