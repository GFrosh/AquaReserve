"""Seed the database with demo data: admin user, customer user, and watercraft."""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from watercraft.models import Watercraft

User = get_user_model()

DEMO_FLEET = [
    {
        'name': 'Sea Breeze',
        'type': 'boat',
        'description': 'Classic 22-ft pontoon boat — perfect for relaxed cruises along the coast with friends and family.',
        'price_per_hour': 65,
        'passenger_capacity': 8,
        'location': 'Marina Bay · Dock A',
        'image_url': 'https://images.unsplash.com/photo-1502901899050-26c8e5c45040?w=900&q=80',
    },
    {
        'name': 'Coral Dasher',
        'type': 'jet_ski',
        'description': 'Yamaha WaveRunner — high-performance jet ski with a thrilling top speed of 65 mph.',
        'price_per_hour': 95,
        'passenger_capacity': 2,
        'location': 'South Beach Dock',
        'image_url': 'https://images.unsplash.com/photo-1530866495561-cd8ce25b06f6?w=900&q=80',
    },
    {
        'name': 'Azure Empress',
        'type': 'yacht',
        'description': '60-ft luxury yacht with sundeck, bar and skipper. Built for sunset charters and private parties.',
        'price_per_hour': 450,
        'passenger_capacity': 12,
        'location': 'Royal Marina',
        'image_url': 'https://images.unsplash.com/photo-1599582909646-2aca4a673c70?w=900&q=80',
    },
    {
        'name': 'Lightning Bolt',
        'type': 'speed_boat',
        'description': 'Sleek 28-ft speed boat with twin engines. Adrenaline guaranteed.',
        'price_per_hour': 180,
        'passenger_capacity': 6,
        'location': 'Harbor Pier',
        'image_url': 'https://images.unsplash.com/photo-1605281317010-fe5ffe798166?w=900&q=80',
    },
    {
        'name': 'Wave Rider X',
        'type': 'jet_ski',
        'description': 'Sea-Doo Spark — agile, fun and beginner-friendly. Includes safety briefing.',
        'price_per_hour': 75,
        'passenger_capacity': 2,
        'location': 'South Beach Dock',
        'image_url': 'https://images.unsplash.com/photo-1599930113854-d6d7fd521f10?w=900&q=80',
    },
    {
        'name': 'Sunset Sailor',
        'type': 'boat',
        'description': 'Cozy sailing boat for romantic sunset rides. Includes snacks and drinks.',
        'price_per_hour': 110,
        'passenger_capacity': 4,
        'location': 'Marina Bay · Dock B',
        'image_url': 'https://images.unsplash.com/photo-1473186578172-c141e6798cf4?w=900&q=80',
    },
    {
        'name': 'Ocean Majesty',
        'type': 'yacht',
        'description': '45-ft modern motor yacht with full kitchen and cabins. Ideal for day trips.',
        'price_per_hour': 320,
        'passenger_capacity': 10,
        'location': 'Royal Marina',
        'image_url': 'https://images.unsplash.com/photo-1567899378494-47b22a2ae96a?w=900&q=80',
    },
    {
        'name': 'Velocity Spark',
        'type': 'speed_boat',
        'description': 'Compact, agile speed boat perfect for water-skiing and tubing adventures.',
        'price_per_hour': 140,
        'passenger_capacity': 5,
        'location': 'Harbor Pier',
        'image_url': 'https://images.unsplash.com/photo-1527431016-3b9d685b0035?w=900&q=80',
    },
]


class Command(BaseCommand):
    help = 'Seed demo data for AquaReserve.'

    def handle(self, *args, **options):
        # --- Admin user ---
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@aquareserve.test', 'role': User.Role.ADMIN,
                      'is_staff': True, 'is_superuser': True},
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('✓ Created admin (admin / admin123)'))
        else:
            self.stdout.write('• Admin already exists')

        # --- Customer user ---
        customer, created = User.objects.get_or_create(
            username='demo',
            defaults={'email': 'demo@aquareserve.test', 'first_name': 'Demo', 'last_name': 'Sailor'},
        )
        if created:
            customer.set_password('demo1234')
            customer.save()
            self.stdout.write(self.style.SUCCESS('✓ Created customer (demo / demo1234)'))
        else:
            self.stdout.write('• Customer already exists')

        # --- Watercraft ---
        created_count = 0
        for entry in DEMO_FLEET:
            obj, was_created = Watercraft.objects.get_or_create(
                name=entry['name'], defaults=entry
            )
            if was_created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_count} watercraft (total now {Watercraft.objects.count()})'))
        self.stdout.write(self.style.SUCCESS('\n🌊  Seed complete — login as admin/admin123 or demo/demo1234'))
