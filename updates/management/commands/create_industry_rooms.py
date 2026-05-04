from django.core.management.base import BaseCommand
from updates.models import ChatRoom


class Command(BaseCommand):
    help = 'Creates pre-defined industry chat rooms'

    def handle(self, *args, **kwargs):
        rooms = [
            {
                'name': 'Software Engineering',
                'description': 'Discuss software development, programming languages, frameworks, and tech careers.',
                'room_type': 'software',
            },
            {
                'name': 'Banking & Finance',
                'description': 'Discuss banking, finance, accounting, and financial technology careers.',
                'room_type': 'banking',
            },
            {
                'name': 'Healthcare',
                'description': 'Discuss healthcare, medical, pharmaceutical, and health technology careers.',
                'room_type': 'healthcare',
            },
        ]

        for room_data in rooms:
            room, created = ChatRoom.objects.get_or_create(
                name=room_data['name'],
                defaults={
                    'description': room_data['description'],
                    'room_type': room_data['room_type'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created room: {room.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Room already exists: {room.name}'))