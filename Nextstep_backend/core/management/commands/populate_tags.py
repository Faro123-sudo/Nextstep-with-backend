import json
from django.core.management.base import BaseCommand
from core.models import Tag
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Populate Tag objects for interests. Usage: python manage.py populate_tags [optional_json_file]'

    def add_arguments(self, parser):
        parser.add_argument('json_file', nargs='?', type=str, help='Optional path to a JSON file containing tags list (array of {name, slug?})')

    def handle(self, *args, **kwargs):
        json_file = kwargs.get('json_file')

        if json_file:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    tags_data = json.load(f)
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
                return
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'Invalid JSON file: {e}'))
                return
        else:
            # Default tags list to seed common interests
            tags_data = [
                {'name': 'career-discovery', 'slug': 'career-discovery'},
                {'name': 'technology', 'slug': 'technology'},
                {'name': 'science', 'slug': 'science'},
                {'name': 'arts', 'slug': 'arts'},
                {'name': 'business', 'slug': 'business'},
                {'name': 'design', 'slug': 'design'},
                {'name': 'math', 'slug': 'math'},
                {'name': 'languages', 'slug': 'languages'},
                {'name': 'health', 'slug': 'health'},
                {'name': 'education', 'slug': 'education'},
                {'name': 'engineering', 'slug': 'engineering'},
                {'name': 'humanities', 'slug': 'humanities'},
                {'name': 'law', 'slug': 'law'},
                {'name': 'finance', 'slug': 'finance'},
                {'name': 'sports', 'slug': 'sports'},
                {'name': 'media', 'slug': 'media'},
            ]

        created = 0
        skipped = 0
        for entry in tags_data:
            name = entry.get('name') if isinstance(entry, dict) else str(entry)
            slug = entry.get('slug') if isinstance(entry, dict) else None
            if not name:
                self.stdout.write(self.style.WARNING('Skipping empty tag entry'))
                continue

            # Idempotent create: skip if a tag with same name or slug exists
            try:
                tag_qs = Tag.objects.filter(name__iexact=name)
                if slug:
                    tag_qs = tag_qs | Tag.objects.filter(slug__iexact=slug)

                if tag_qs.exists():
                    skipped += 1
                    continue

                Tag.objects.create(name=name, slug=slug if slug else None)
                created += 1
            except IntegrityError as e:
                self.stdout.write(self.style.WARNING(f'Skipped {name} due to DB error: {e}'))
                skipped += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} tags, skipped {skipped} existing/failed entries.'))
