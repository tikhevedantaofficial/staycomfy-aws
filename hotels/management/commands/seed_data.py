from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from pathlib import Path
from hotels.models import Hotel, Room

MEDIA_DIR = Path(__file__).resolve().parent.parent.parent.parent / 'media' / 'hotels'
ROOMS_MEDIA_DIR = Path(__file__).resolve().parent.parent.parent.parent / 'media' / 'rooms'




HOTELS_DATA = [
    {
        'name': 'The Neon Horizon',
        'city': 'Tokyo, Japan',
        'rating': Decimal('4.8'),
        'image': 'neon_horizon.png',
        'description': (
            'A sleek tower of glass and light in the heart of Shibuya. '
            'The Neon Horizon blends traditional Japanese hospitality with '
            'futuristic design, offering panoramic views of the Tokyo skyline. '
            'Each room features smart-home controls and ambient lighting.'
        ),
        'rooms': [
            {'name': 'Sky Loft', 'price': Decimal('320.00'), 'capacity': 2, 'image': 'sky_loft.png',
             'description': 'A minimalist loft with floor-to-ceiling windows and city views.'},
            {'name': 'Zen Suite', 'price': Decimal('480.00'), 'capacity': 3, 'image': 'zen_suite.png',
             'description': 'Spacious suite with a private tatami area and rainfall shower.'},
            {'name': 'Penthouse Nova', 'price': Decimal('950.00'), 'capacity': 4, 'image': 'penthouse_nova.png',
             'description': 'The crown jewel — a rooftop penthouse with 360° views and private terrace.'},
        ],
    },
    {
        'name': 'Azure Reef Resort',
        'city': 'Maldives',
        'rating': Decimal('4.9'),
        'image': 'azure_reef.png',
        'description': (
            'Overwater villas perched above crystal-clear lagoons. Azure Reef Resort '
            'is a sanctuary of calm where the ocean meets luxury. Dive into vibrant '
            'coral reefs right from your private deck.'
        ),
        'rooms': [
            {'name': 'Lagoon Villa', 'price': Decimal('650.00'), 'capacity': 2, 'image': 'lagoon_villa.png',
             'description': 'Overwater villa with glass floor panels and direct lagoon access.'},
            {'name': 'Sunset Bungalow', 'price': Decimal('890.00'), 'capacity': 3, 'image': 'sunset_bungalow.png',
             'description': 'Beachfront bungalow with outdoor shower and sunset-facing deck.'},
            {'name': 'Royal Overwater Suite', 'price': Decimal('1500.00'), 'capacity': 4, 'image': 'royal_overwater.png',
             'description': 'Two-bedroom suite with infinity pool and butler service.'},
        ],
    },
    {
        'name': 'Nova Grand Hotel',
        'city': 'Paris, France',
        'rating': Decimal('4.6'),
        'image': 'nova_grand.png',
        'description': (
            'Where Parisian elegance meets modern innovation. Located steps from the '
            'Champs-Élysées, Nova Grand Hotel offers a timeless experience with '
            'contemporary amenities and Michelin-starred dining.'
        ),
        'rooms': [
            {'name': 'Classic Parisian', 'price': Decimal('280.00'), 'capacity': 2, 'image': 'classic_parisian.png',
             'description': 'Elegant room with Haussmann-style decor and marble bathroom.'},
            {'name': 'Deluxe Suite', 'price': Decimal('520.00'), 'capacity': 3, 'image': 'deluxe_suite_paris.png',
             'description': 'Corner suite with Eiffel Tower views and sitting area.'},
            {'name': 'Presidential Suite', 'price': Decimal('1200.00'), 'capacity': 4, 'image': 'presidential_paris.png',
             'description': 'Grand suite with private dining room and panoramic balcony.'},
        ],
    },
    {
        'name': 'Pulse Tower',
        'city': 'New York, USA',
        'rating': Decimal('4.5'),
        'image': 'pulse_tower.png',
        'description': (
            'Rising above Midtown Manhattan, Pulse Tower is a high-energy hotel '
            'designed for the modern traveler. Rooftop bar, co-working spaces, '
            'and rooms equipped with the latest smart technology.'
        ),
        'rooms': [
            {'name': 'Urban Pod', 'price': Decimal('210.00'), 'capacity': 1, 'image': 'urban_pod.png',
             'description': 'Compact smart room optimized for solo travelers with integrated tech.'},
            {'name': 'Skyline King', 'price': Decimal('380.00'), 'capacity': 2, 'image': 'skyline_king.png',
             'description': 'King bed room with stunning Manhattan skyline views.'},
            {'name': 'Empire Suite', 'price': Decimal('750.00'), 'capacity': 4, 'image': 'empire_suite.png',
             'description': 'Corner suite with wraparound views and luxury amenities.'},
        ],
    },
    {
        'name': 'Ember & Stone Lodge',
        'city': 'Reykjavik, Iceland',
        'rating': Decimal('4.7'),
        'image': 'ember_stone.png',
        'description': (
            'A boutique lodge on the edge of the Arctic. Ember & Stone combines '
            'raw volcanic landscapes with geothermal-heated interiors. Watch the '
            'Northern Lights from your private hot tub.'
        ),
        'rooms': [
            {'name': 'Aurora Room', 'price': Decimal('260.00'), 'capacity': 2, 'image': 'aurora_room.png',
             'description': 'Cozy room with skylight designed for Northern Lights viewing.'},
            {'name': 'Geothermal Suite', 'price': Decimal('440.00'), 'capacity': 2, 'image': 'geothermal_suite.png',
             'description': 'Suite with private geothermal hot tub and lava field views.'},
            {'name': 'Volcanic Lodge', 'price': Decimal('700.00'), 'capacity': 5, 'image': 'volcanic_lodge.png',
             'description': 'Standalone lodge with two bedrooms, fireplace, and panoramic windows.'},
        ],
    },
    {
        'name': 'Sahara Mirage',
        'city': 'Dubai, UAE',
        'rating': Decimal('4.8'),
        'image': 'sahara_mirage.png',
        'description': (
            'An oasis of opulence rising from the desert. Sahara Mirage features '
            'gold-accented interiors, an infinity pool overlooking the dunes, '
            'and world-class spa treatments inspired by ancient Arabian traditions.'
        ),
        'rooms': [
            {'name': 'Desert View Room', 'price': Decimal('350.00'), 'capacity': 2, 'image': 'desert_view.png',
             'description': 'Elegant room with desert panorama and luxurious furnishings.'},
            {'name': 'Oasis Suite', 'price': Decimal('600.00'), 'capacity': 3, 'image': 'oasis_suite.png',
             'description': 'Suite with private balcony, plunge pool, and butler service.'},
            {'name': 'Royal Palace', 'price': Decimal('2000.00'), 'capacity': 6, 'image': 'royal_palace_dubai.png',
             'description': 'Three-bedroom palace with private cinema, pool, and chef kitchen.'},
        ],
    },
    {
        'name': 'Canopy Boutique Hotel',
        'city': 'Bali, Indonesia',
        'rating': Decimal('4.6'),
        'image': 'canopy_bali.png',
        'description': (
            'Nestled among ancient banyan trees in Ubud, Canopy offers treehouse-style '
            'suites surrounded by lush tropical forest. Yoga pavilions, organic cuisine, '
            'and holistic wellness define the Canopy experience.'
        ),
        'rooms': [
            {'name': 'Garden Treehouse', 'price': Decimal('180.00'), 'capacity': 2, 'image': 'garden_treehouse.png',
             'description': 'Elevated room among the canopy with open-air bathroom.'},
            {'name': 'Riverside Villa', 'price': Decimal('350.00'), 'capacity': 3, 'image': 'riverside_villa.png',
             'description': 'Private villa overlooking the Ayung River with infinity pool.'},
            {'name': 'Jungle Penthouse', 'price': Decimal('550.00'), 'capacity': 4, 'image': 'jungle_penthouse.png',
             'description': 'Two-level treehouse with panoramic jungle views and private chef.'},
        ],
    },
    {
        'name': 'Crystal Spire Hotel',
        'city': 'London, UK',
        'rating': Decimal('4.4'),
        'image': 'crystal_spire.png',
        'description': (
            'A landmark of contemporary architecture on the South Bank. Crystal Spire '
            'pairs British heritage with avant-garde design, offering afternoon tea '
            'in a glass atrium and rooms with curated art collections.'
        ),
        'rooms': [
            {'name': 'Heritage Room', 'price': Decimal('240.00'), 'capacity': 2, 'image': 'heritage_room.png',
             'description': 'Classic British design with modern comforts and Thames views.'},
            {'name': 'Gallery Suite', 'price': Decimal('420.00'), 'capacity': 2, 'image': 'gallery_suite.png',
             'description': 'Art-filled suite with rotating exhibitions and private terrace.'},
            {'name': 'Crown Suite', 'price': Decimal('880.00'), 'capacity': 4, 'image': 'crown_suite.png',
             'description': 'Top-floor suite with panoramic London views and private dining.'},
        ],
    },
]


class Command(BaseCommand):
    help = 'Populate the database with sample Staycomfy hotels and rooms.'

    def handle(self, *args, **options):
        created_hotels = 0
        created_rooms = 0

        for hotel_data in HOTELS_DATA:
            rooms_data = hotel_data.pop('rooms')
            image_filename = hotel_data.pop('image', None)
            hotel, created = Hotel.objects.get_or_create(
                name=hotel_data['name'],
                defaults={
                    'city': hotel_data['city'],
                    'rating': hotel_data['rating'],
                    'description': hotel_data['description'],
                },
            )
            if created:
                created_hotels += 1

            # Assign image if not already set
            if image_filename and not hotel.image:
                img_path = MEDIA_DIR / image_filename
                if img_path.exists():
                    with open(img_path, 'rb') as f:
                        hotel.image.save(image_filename, ContentFile(f.read()), save=True)

            for room_data in rooms_data:
                room_image_name = room_data.pop('image', None)
                room, room_created = Room.objects.get_or_create(
                    hotel=hotel,
                    name=room_data['name'],
                    defaults={
                        'price_per_night': room_data['price'],
                        'capacity': room_data['capacity'],
                        'description': room_data['description'],
                    },
                )
                if room_created:
                    created_rooms += 1

                # Always re-assign unique room image
                if room_image_name:
                    img_path = ROOMS_MEDIA_DIR / room_image_name
                    if img_path.exists():
                        with open(img_path, 'rb') as f:
                            room.image.save(room_image_name, ContentFile(f.read()), save=True)

        self.stdout.write(self.style.SUCCESS(
            f'Done! Created {created_hotels} hotels and {created_rooms} rooms.'
        ))
