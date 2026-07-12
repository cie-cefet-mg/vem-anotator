from django.contrib import admin
from .models import (
    Question, Answer, Project, Batch, Annotation, 
    Annotator, Label, Metod
)

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Project)
admin.site.register(Batch)
admin.site.register(Annotation)
admin.site.register(Annotator)
admin.site.register(Label)
admin.site.register(Metod)
