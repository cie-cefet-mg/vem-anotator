import random
from collections import defaultdict
from django.db import transaction
from app_projeto.models import Batch, Answer, Annotation

class BatchCreationService:
    
    @classmethod
    def create_new_batch(cls, project, annotators: list, num_answers: int, limit_per_question: int) -> 'Batch':
        """
        Main entry point that orchestrates batch creation and assigns annotators.
        transaction.atomic is used to ensure a rollback if anything fails.
        """
        with transaction.atomic():
            # 1. Fetch answers through the manager and group them in the service
            available_answers = Answer.objects.available_for_project(project).values_list("id", "question_id")
            questions_map = cls._group_answers(available_answers)
            
            if not questions_map:
                raise ValueError("No answers are available for annotation in this project.")

            # 2. Select answers according to the requested criteria
            selected_answer_ids = cls._select_answers(questions_map, num_answers, limit_per_question)
            
            if not selected_answer_ids:
                raise ValueError("It was not possible to select enough answers.")

            # 3. Create the batch by delegating responsibility to the manager
            new_batch = Batch.objects.create_for_project(project)
            
            # 4. Associate the answers with the batch (many-to-many relation)
            new_batch.answers.add(*selected_answer_ids)
            
            # 5. Create Annotation instances for the selected annotators
            cls._assign_annotators_to_batch(new_batch, selected_answer_ids, annotators)
            
            return new_batch

    @staticmethod
    def _group_answers(answers_queryset) -> dict:
        """
        Groups answers by question.
        The in-memory organization logic stays inside the service.
        """
        questions_per_answer = defaultdict(list)
        for answer_id, question_id in answers_queryset:
            questions_per_answer[question_id].append(answer_id)
            
        return questions_per_answer

    @staticmethod
    def _select_answers(questions_map: dict, num_answers: int, limit_per_question: int) -> list:
        """
        Selects answer IDs while respecting the per-question limit
        and reaching the requested total number of answers.
        """
        candidate_questions = list(questions_map.keys())
        random.shuffle(candidate_questions)  # Shuffle questions for randomness
        
        selected_answer_ids = []
        
        for q_id in candidate_questions:
            answers_in_question = questions_map[q_id]
            random.shuffle(answers_in_question)  # Optionally shuffle answers within the question
            
            # How many answers are still needed to complete the batch?
            remaining_needed = num_answers - len(selected_answer_ids)
            
            if remaining_needed <= 0:
                break  # Batch already reached the requested size
                
            # Take the minimum between:
            # 1. The requested per-question limit
            # 2. What is available for the question
            # 3. What is still needed to complete the batch
            to_take = min(limit_per_question, len(answers_in_question), remaining_needed)
            
            selected_answer_ids.extend(answers_in_question[:to_take])
            
        return selected_answer_ids

    @staticmethod
    def _assign_annotators_to_batch(batch, answer_ids: list, annotators: list):
        """
        Creates the tasks (Annotations) linking the batch, answer, and annotator.
        Uses bulk_create for database efficiency.
        """
        annotations_to_create = []
        
        for ans_id in answer_ids:
            for annotator in annotators:
                annotations_to_create.append(
                    Annotation(
                        batch=batch,
                        answer_id=ans_id,
                        annotator=annotator
                        # status="PENDING" (an initial status could be added here)
                    )
                )
                
        # Persist everything with a single database operation
        if annotations_to_create:
            Annotation.objects.bulk_create(annotations_to_create)

class AnnotationDivergenceService:
    
    @staticmethod
    def get_divergences(batch_id: int) -> list:
        """
        Fetches all divergences in a batch.
        Returns a list with the answers that diverged.
        """
        batch = Batch.objects.with_divergence_data().get(id=batch_id)
        divergences = []
        
        # For each answer in the batch
        for answer in batch.answers.all():
            annotations = answer.annotations.filter(batch=batch)
            
            # Skip answers with fewer than two annotations
            if annotations.count() < 2:
                continue
            
            # Collect each annotator's labels
            annotator_labels = {}
            for annotation in annotations:
                labels_info = annotation.labels.values("id", "name")
                annotator_labels[annotation.annotator.id] = {
                    "annotator_name": annotation.annotator.name,
                    "annotation_id": annotation.id,
                    "labels": list(labels_info)
                }
            
            # Compare the labels
            first_labels = list(annotator_labels.values())[0]["labels"]
            has_divergence = False
            
            for annotator_info in list(annotator_labels.values())[1:]:
                if annotator_info["labels"] != first_labels:
                    has_divergence = True
                    break
            
            # If a divergence is found, add it to the list and mark the answer
            if has_divergence:
                answer.need_revision = True
                answer.save()
                
                divergences.append({
                    "answer": answer,
                    "question": answer.question,
                    "annotator_labels": annotator_labels
                })
        
        return divergences