from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# Ajuste os imports de acordo com o nome do seu app
from app_projeto.models.annotation_batches import Project, Annotator
from app_projeto.services import BatchCreationService

class Command(BaseCommand):
    help = 'Creates a new annotation batch for a specific project using its acronym or name.'

    def add_arguments(self, parser):
        # Required positional argument - accepts either the project acronym or name
        parser.add_argument(
            'project_acronym', 
            type=str, 
            help='The project acronym or name (for example, LUPA.v1 or "Bias Evaluation") for which the batch will be created'
        )

        # Optional arguments with default values
        parser.add_argument(
            '--annotators', 
            nargs='+', 
            type=str, 
            required=True,
            help='Annotator email addresses to associate with this batch (space-separated)'
        )
        
        parser.add_argument(
            '--num-answers', 
            type=int, 
            default=50, 
            help='Total number of answers requested in the batch (default: 50)'
        )
        
        parser.add_argument(
            '--limit-per-question', 
            type=int, 
            default=5, 
            help='Maximum number of answers per question in this batch (default: 5)'
        )

    def handle(self, *args, **options):
        # English variable names follow a clean-code style
        project_acronym = options['project_acronym']
        annotator_emails = options['annotators']
        num_answers = options['num_answers']
        limit_per_question = options['limit_per_question']

        # 1. Validate the project by acronym or name (case-insensitive)
        project = None
        
        # Try acronym first
        if project_acronym.strip():  # If not empty
            try:
                project = Project.objects.get(acronym__iexact=project_acronym)
            except Project.DoesNotExist:
                pass
        
        # If not found by acronym, try by name
        if not project:
            try:
                project = Project.objects.get(name__iexact=project_acronym)
            except Project.DoesNotExist:
                pass
        
        # If still not found, show an error with available options
        if not project:
            available_projects = []
            for p in Project.objects.all():
                if p.acronym:
                    available_projects.append(f"'{p.acronym}'")
                available_projects.append(f"'{p.name}'")
            
            options_str = ", ".join(available_projects) if available_projects else "No projects registered."
            
            raise CommandError(
                f'Project "{project_acronym}" not found (by acronym or name).\n'
                f'Available projects: {options_str}'
            )

        # 2. Validate annotators by email
        annotators = list(Annotator.objects.filter(email__in=annotator_emails))
        if len(annotators) != len(annotator_emails):
            found_emails = [annotator.email for annotator in annotators]
            missing_emails = set(annotator_emails) - set(found_emails)
            
            available_annotators = list(Annotator.objects.values_list('email', flat=True))
            options_str = ", ".join(available_annotators) if available_annotators else "No annotators registered."
            
            raise CommandError(
                f'Annotator(s) not found in the database: {list(missing_emails)}\n'
                f'Available emails: {options_str}'
            )

        # 3. Run creation through the service
        proj_display = project.acronym if project.acronym else project.name
        self.stdout.write(self.style.WARNING(f'Starting batch creation for project "{proj_display.upper()}"...'))
        
        try:
            # Service call with English variable names
            new_batch = BatchCreationService.create_new_batch(
                project=project,
                annotators=annotators,
                num_answers=num_answers,
                limit_per_question=limit_per_question
            )
            
            # Success message
            self.stdout.write(
                self.style.SUCCESS(
                    f'Success! Batch #{new_batch.id} created with {new_batch.answers.count()} answers '
                    f'and assigned to {len(annotators)} annotator(s).'
                )
            )
            
        except ValueError as business_error:
            # Business rule errors (for example, no answers available)
            raise CommandError(str(business_error))
        except Exception as unexpected_error:
            # Unexpected errors
            raise CommandError(f'Unexpected error while creating the batch: {str(unexpected_error)}')
