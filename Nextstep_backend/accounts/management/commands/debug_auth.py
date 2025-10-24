from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create or test a debug user and try serializer-based login and refresh.'

    def add_arguments(self, parser):
        parser.add_argument('--email', default='debug@example.com')
        parser.add_argument('--password', default='password123')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']

        user, created = User.objects.get_or_create(email__iexact=email, defaults={'username': email, 'email': email})
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user {email}'))
        else:
            self.stdout.write(self.style.WARNING(f'User {email} already exists'))

        # Test authentication
        auth_user = None
        try:
            auth_user = User.objects.get(email__iexact=email)
            if auth_user.check_password(password):
                self.stdout.write(self.style.SUCCESS('Password check passed'))
            else:
                self.stdout.write(self.style.ERROR('Password check failed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during auth test: {e}'))
