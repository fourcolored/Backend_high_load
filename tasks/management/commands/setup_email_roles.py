from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Create user roles and assign permissions'

    def handle(self, *args, **kwargs):
        # Create roles
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        user_group, _ = Group.objects.get_or_create(name='User')
        
        # Assign permissions
        view_permission = Permission.objects.get(codename='can_view_email')
        create_permission = Permission.objects.get(codename='can_create_email')
        send_email_permission = Permission.objects.get(codename='can_send_email')
        delete_email_permission = Permission.objects.get(codename='can_delete_email')

        
        # Add permissions to groups
        admin_group.permissions.add(view_permission, create_permission, send_email_permission, delete_email_permission)
        user_group.permissions.add(view_permission, create_permission, send_email_permission)

        self.stdout.write(self.style.SUCCESS('Roles and permissions have been set up successfully!'))