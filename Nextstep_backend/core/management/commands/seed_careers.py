import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from core.models import Career, Skill, Tag

# Default path: the frontend's static career bank JSON
DEFAULT_JSON_PATH = (
    Path(__file__).resolve().parents[4]
    / "Nextstep-frontend"
    / "nextstep-navigator"
    / "src"
    / "data"
    / "careerData.json"
)


def parse_salary(salary_str):
    """
    Extract a Decimal salary from human-readable strings.

    "$95,000" -> Decimal("95000")
    "$80,000 - $120,000" -> Decimal("100000")  (average of the range)
    Returns None when no number can be parsed.
    """
    if not salary_str:
        return None
    numbers = re.findall(r"[\d][\d,]*(?:\.\d+)?", str(salary_str))
    if not numbers:
        return None
    try:
        values = [float(n.replace(",", "")) for n in numbers]
    except ValueError:
        return None
    try:
        return Decimal(str(sum(values) / len(values))).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


class Command(BaseCommand):
    help = (
        'Seed core.Career objects from careerData.json. '
        'Usage: python manage.py seed_careers [optional_json_file]'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            nargs='?',
            type=str,
            help=f'Optional path to a careerData.json file (default: {DEFAULT_JSON_PATH})',
        )

    def handle(self, *args, **kwargs):
        json_file = Path(kwargs.get('json_file') or DEFAULT_JSON_PATH)

        if not json_file.exists():
            self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
            return

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Invalid JSON file: {e}'))
            return

        careers_data = data.get('careerBank', []) if isinstance(data, dict) else data
        if not careers_data:
            self.stdout.write(self.style.WARNING('No career entries found in JSON.'))
            return

        created = 0
        updated = 0
        for entry in careers_data:
            title = (entry.get('careerName') or '').strip()
            if not title:
                self.stdout.write(self.style.WARNING('Skipping entry without careerName.'))
                continue

            defaults = {
                'domain': entry.get('industry') or '',
                'description': entry.get('description') or '',
                'education_path': entry.get('educationPath') or '',
                'expected_salary': parse_salary(entry.get('averageSalary')),
            }

            career, was_created = Career.objects.get_or_create(title=title, defaults=defaults)
            if not was_created:
                for field, value in defaults.items():
                    setattr(career, field, value)

            # Skills (M2M)
            skills = entry.get('skillsRequired') or []
            skill_objs = []
            for skill_name in skills:
                name = str(skill_name).strip()
                if not name:
                    continue
                skill, _ = Skill.objects.get_or_create(name=name)
                skill_objs.append(skill)

            # Tags (M2M): industry + audience tags
            tag_names = []
            if entry.get('industry'):
                tag_names.append(entry['industry'])
            tag_names.extend(entry.get('audiences') or [])
            tag_objs = []
            for tag_name in tag_names:
                name = str(tag_name).strip()
                if not name:
                    continue
                tag, _ = Tag.objects.get_or_create(
                    slug=slugify(name),
                    defaults={'name': name},
                )
                tag_objs.append(tag)

            career.save()
            career.required_skills.set(skill_objs)
            career.tags.set(tag_objs)

            # Rebuild denormalized search text now that M2M relations are set
            career.build_content_text()
            career.save(update_fields=['content_text'])

            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(f'Seeded careers: {created} created, {updated} updated.')
        )
