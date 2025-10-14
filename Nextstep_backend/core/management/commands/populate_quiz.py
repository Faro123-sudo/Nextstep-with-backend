import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Quiz, QuizQuestion


class Command(BaseCommand):
    help = "Populate Quiz and QuizQuestion models from careerData.json"

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            dest='json_file',
            help='Path to careerData.json (defaults to frontend data file)',
            default=None,
        )

    def handle(self, *args, **options):
        # Determine default path if not provided
        json_path = options.get('json_file')
        if not json_path:
            # default relative path into the frontend folder
            repo_root = settings.BASE_DIR if hasattr(settings, 'BASE_DIR') else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_path = os.path.join(repo_root, '..', 'Nextstep-frontend', 'nextstep-navigator', 'src', 'data', 'careerData.json')
            # C:\Users\ibito\Documents\GitHub\Nextstep-with-backend\Nextstep-frontend\nextstep-navigator\src\data\careerData.json
            json_path = os.path.normpath(json_path)

        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f'JSON file not found: {json_path}'))
            return

        with open(json_path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)

        # We expect quizQuestions keyed by audience groups in the JSON
        quiz_questions = data.get('quizQuestions', {})
        created_quizzes = 0
        created_questions = 0

        for audience, questions in quiz_questions.items():
            title = f"Career quiz - {audience.capitalize()}"
            quiz, created = Quiz.objects.get_or_create(title=title, defaults={'description': f'Auto-generated quiz for {audience} audience'})
            if created:
                created_quizzes += 1

            for q in questions:
                # Map JSON fields to model fields; handle options and missing keys safely
                question_text = q.get('question') or q.get('question_text') or q.get('questionText')
                if not question_text:
                    continue

                options = q.get('options')
                # If options are present but not JSON serializable in our DB shape, keep as-is
                qtype = q.get('type') or q.get('difficulty') or 'mcq'

                # For MCQ, ensure options is a list; otherwise leave null
                if isinstance(options, list):
                    options_field = options
                else:
                    options_field = None

                # try to extract a plausible correct answer from answersMapping if present
                correct_answer = None
                answers_map = q.get('answersMapping') or {}
                if answers_map and isinstance(answers_map, dict):
                    # choose the first mapping that contains a non-empty mapping with a key like 'recommended'
                    for opt_text, mapping in answers_map.items():
                        if mapping and isinstance(mapping, dict):
                            # If mapping contains followUpResources or industries, we won't treat as correct, but keep the option text
                            correct_answer = opt_text
                            break

                # Create or update question
                try:
                    qq, qc = QuizQuestion.objects.get_or_create(
                        quiz=quiz,
                        question_text=question_text,
                        defaults={
                            'type': 'mcq' if options_field else 'text',
                            'options': options_field,
                            'correct_answer': correct_answer,
                            'weightage': 1.0,
                        },
                    )
                    if qc:
                        created_questions += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Could not create question "{question_text[:40]}...": {e}'))

            # Add two extra generic questions per audience to expand the quiz
            extras = [
                {
                    'question': f'What is your main goal as a {audience}?',
                    'options': ['Learn skills', 'Get a job', 'Career change', 'Explore options'],
                },
                {
                    'question': f'How much time can you commit weekly to learning/career activities?',
                    'options': ['<5 hours', '5-10 hours', '10-20 hours', '>20 hours'],
                },
            ]

            for ex in extras:
                try:
                    qq, qc = QuizQuestion.objects.get_or_create(
                        quiz=quiz,
                        question_text=ex['question'],
                        defaults={
                            'type': 'mcq',
                            'options': ex['options'],
                            'weightage': 1.0,
                        },
                    )
                    if qc:
                        created_questions += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Could not create extra question "{ex["question"][:40]}...": {e}'))

        self.stdout.write(self.style.SUCCESS(f'Created/updated {created_quizzes} quizzes and {created_questions} questions.'))
