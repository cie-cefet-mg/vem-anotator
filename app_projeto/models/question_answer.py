from django.db import models
from ..managers import AnswerManager

class Question(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text[:100]

class Answer(models.Model):
    content = models.TextField(blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    metod = models.ForeignKey('Metod', on_delete=models.CASCADE)  
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    it_was_revised = models.BooleanField(default=False)
    need_revision = models.BooleanField(default=False)

    objects = AnswerManager()

    def __str__(self):
        return f"Answer {self.id} - {self.metod.name} - {self.question.text[:50]}"