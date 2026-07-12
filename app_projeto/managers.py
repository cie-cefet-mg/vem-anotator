from django.db import models
from django.db.models import Max, QuerySet, Count

class AnswerQuerySet(QuerySet):
    def for_project(self, project):
        return self.filter(project=project)
    
    def not_annotated(self):
        return self.filter(annotations__isnull=True)
    
    def by_model(self, metod):
        return self.filter(metod=metod)
    
    def need_review(self):
        return self.filter(need_revision=True)

class AnswerManager(models.Manager):
    def get_queryset(self):
        return AnswerQuerySet(self.model, using=self._db)
    
    def for_project(self, project):
        return self.get_queryset().for_project(project)
    
    def not_annotated(self):
        return self.get_queryset().not_annotated()
    
    def by_model(self, metod):
        return self.get_queryset().by_model(metod)
    
    def need_review(self):
        return self.get_queryset().need_review()
    
    def available_for_project(self, project):
        """
        Returns the QuerySet with answers that have not yet been assigned
        to any batch for a given project.
        """
        return self.filter(project=project).annotate(
            batch_count=Count('batch')
        ).filter(batch_count=0)

class BatchQuerySet(QuerySet):
    def for_project(self, project):
        return self.filter(project=project)
    
    def with_answers(self):
        # List all batches with their answers
        return self.prefetch_related('answers')
    
    def with_divergence_data(self):
        """Fetch all Annotations together with their Labels."""
        
        return self.prefetch_related(
            'answers__annotations',
            'answers__annotations__labels',
            'answers__annotations__annotator'
        )

class BatchManager(models.Manager):
    def get_queryset(self):
        return BatchQuerySet(self.model, using=self._db)
    
    def for_project(self, project):
        return self.get_queryset().for_project(project)
    
    def with_answers(self):
        return self.get_queryset().with_answers()
    
    def with_divergence_data(self):
        return self.get_queryset().with_divergence_data()
    
    def create_for_project(self, project):
        """
        Creates and returns a new Batch instance.
        """
        return self.create(project=project)
