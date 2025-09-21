import json
from django.core.management.base import BaseCommand
from core.models import Quiz, QuizQuestion  # Adjust 'your_app' to your app's name
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Populates quiz questions from a JSON file.'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='The path to the JSON file containing quiz questions.')
        parser.add_argument('quiz_id', type=int, help='The ID of the quiz to add questions to.')

    def handle(self, *args, **kwargs):
        json_file_path = kwargs['json_file']
        quiz_id = kwargs['quiz_id']

        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Quiz with ID {quiz_id} does not exist.'))
            return

        try:
            with open(json_file_path, 'r') as f:
                questions_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found at {json_file_path}'))
            return

        created_count = 0
        for data in questions_data:
            try:
                QuizQuestion.objects.create(
                    quiz=quiz,
                    question_text=data['question_text'],
                    type=data.get('type', 'mcq'),  # Use .get() to provide a default
                    options=data.get('options'),
                    correct_answer=data.get('correct_answer'),
                    weightage=data.get('weightage', 1.0)
                )
                created_count += 1
            except KeyError as e:
                self.stdout.write(self.style.ERROR(f'Skipping question due to missing key: {e}'))
            except IntegrityError as e:
                self.stdout.write(self.style.WARNING(f'Skipping question due to database error: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully populated {created_count} questions for Quiz ID {quiz_id}.'))