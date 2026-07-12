import csv
from django.db import transaction
from django.core.management.base import BaseCommand
from app_projeto.models import Project, Question, Answer, Metod


def _normalize_headers(row):
    prompt = row.get("Prompt") or row.get("prompt") or row.get("\ufeffPrompt")
    model = row.get("Model") or row.get("Modelo") or row.get("\ufeffModel")
    model_answer = row.get("Model Answer") or row.get("Resposta do LLM") or row.get("\ufeffModel Answer")

    return {
        "Prompt": prompt.strip() if isinstance(prompt, str) else prompt,
        "Model": model.strip() if isinstance(model, str) else model,
        "Model Answer": model_answer.strip() if isinstance(model_answer, str) else model_answer,
    }

class Command(BaseCommand):
    help = "Imports all data from the spreadsheet."

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument('--project_name', type=str, required=True, help='Project name')
        parser.add_argument('--limit', type=int, help='Maximum number of answers to import (optional)')
    
    @transaction.atomic  # rollback if anything fails midway
    def handle(self, *args, **options):
        csv_file = options['csv_file']
        project_name = options['project_name']
        limit = options.get('limit')

        try:
            with open(csv_file, "r", newline="", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)
                imported_count = 0

                for row in reader:
                    if limit and imported_count >= limit:
                        break

                    data = _normalize_headers(row)
                    if not data["Prompt"] or not data["Model"] or not data["Model Answer"]:
                        raise KeyError("Prompt, Model, or Model Answer")

                    project, _ = Project.objects.get_or_create(name=project_name)
                    question, _ = Question.objects.get_or_create(
                        text=data['Prompt']
                    )

                    metod, _ = Metod.objects.get_or_create(
                        name=data['Model']
                    )
                    
                    # Create Answer
                    answer, created = Answer.objects.get_or_create(
                        question=question,
                        metod=metod,
                        project=project,
                        defaults={'content': data['Model Answer']}
                    )
                    
                    if created:
                        imported_count += 1
                    
                    status = "created" if created else "already existed"
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Answer {status}: {metod.name} -> {question.text[:50]}"
                        )
                    )
                    
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
        except KeyError as e:
            self.stdout.write(
                self.style.ERROR(f'Missing CSV column: {e}')
            )