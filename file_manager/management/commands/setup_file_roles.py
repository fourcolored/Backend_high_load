from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Create user roles and assign permissions'

    def handle(self, *args, **kwargs):
        # Create roles
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        user_group, _ = Group.objects.get_or_create(name='User')
        
        # Assign permissions
        create_permission = Permission.objects.get(codename='can_add_file')
        view_permission = Permission.objects.get(codename='can_view_file')

        
        # Add permissions to groups
        admin_group.permissions.add(view_permission, create_permission)
        user_group.permissions.add(view_permission, create_permission)

        self.stdout.write(self.style.SUCCESS('Roles and permissions have been set up successfully!'))