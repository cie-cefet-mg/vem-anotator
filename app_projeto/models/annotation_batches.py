from django.db import models
from ..managers import BatchManager
from .question_answer import Answer

class Label(models.Model):  # label
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name

class Annotator(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)

    def __str__(self):
        return f" {self.name} - {self.email}"

class Annotation(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="annotations") 
    annotator = models.ForeignKey(Annotator, on_delete=models.CASCADE, related_name="made_annotations")
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE, related_name="annotations", null=True)
    labels = models.ManyToManyField(Label, blank=True, related_name="annotations")
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Annotation {self.id} - {self.annotator.name}"

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    acronym = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.acronym} - {self.name}"

class Batch(models.Model):  # batch
    answers = models.ManyToManyField(Answer)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    objects = BatchManager()

    def __str__(self):
        return f"Batch {self.project.name}"

class Metod(models.Model):  # method
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
