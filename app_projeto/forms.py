from django import forms

from app_projeto.models import Annotation, Label


class AnnotationEvaluationForm(forms.ModelForm):
    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.all().order_by("name"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Identified biases"
    )

    class Meta:
        model = Annotation
        fields = ["labels"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["labels"].widget.attrs.update({"class": "form-check-input"})
