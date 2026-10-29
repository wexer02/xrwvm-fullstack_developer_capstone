import json
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from djangoapp.models import CarMake, CarModel


class Command(BaseCommand):
    help = 'Load the course vehicle catalog without deleting existing data.'

    def handle(self, *args, **options):
        records = json.loads((settings.BASE_DIR / 'database/data/car_records.json').read_text())['cars']
        for record in records:
            make, _ = CarMake.objects.get_or_create(name=record['make'], defaults={'description': record['make'] + ' vehicles'})
            CarModel.objects.get_or_create(car_make=make, name=record['model'], year=record['year'],
                                           defaults={'type': record['bodyType']})
        password = os.environ.get('ADMIN_PASSWORD')
        if password and not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', password)
        self.stdout.write(f'Catalog ready: {CarMake.objects.count()} makes, {CarModel.objects.count()} models.')
