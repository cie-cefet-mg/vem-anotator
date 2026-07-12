from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView
from django.http import HttpResponse
import csv
from app_projeto.forms import AnnotationEvaluationForm
from app_projeto.models import Annotation, Annotator, Batch
from app_projeto.services import AnnotationDivergenceService

def home(request):
    batches = Batch.objects.with_answers()

    context = {
        "batches" : batches
    }
    return render(request, "home.html", context)


def avaliation(request, batch_id, annotator_id):
    """
    Displays the next pending answer for an annotator in a batch
    and saves the selected label.
    """
    batch = get_object_or_404(Batch, pk=batch_id)
    annotator = get_object_or_404(Annotator, pk=annotator_id)

    annotations_qs = (
        Annotation.objects.select_related("answer__question", "answer__metod")
        .filter(batch=batch, annotator=annotator)
        .order_by("id")
    )
    annotation_ids = list(annotations_qs.values_list("id", flat=True))

    # Allows opening a specific queue item via query string.
    current_annotation_id = request.GET.get("annotation_id")
    current_annotation = None
    if current_annotation_id:
        current_annotation = annotations_qs.filter(pk=current_annotation_id).first()

    # If nothing was provided, start at the first pending annotation.
    if current_annotation is None:
        current_annotation = annotations_qs.filter(labels__isnull=True).first()

    # If there are no pending items, show the last one for review.
    if current_annotation is None:
        current_annotation = annotations_qs.last()

    total_annotations = annotations_qs.count()
    done_annotations = annotations_qs.filter(completed=True).count()
    progress_percent = int((done_annotations / total_annotations) * 100) if total_annotations else 0

    previous_annotation_id = None
    next_annotation_id = None
    if current_annotation is not None and current_annotation.id in annotation_ids:
        current_index = annotation_ids.index(current_annotation.id)
        if current_index > 0:
            previous_annotation_id = annotation_ids[current_index - 1]
        if current_index < len(annotation_ids) - 1:
            next_annotation_id = annotation_ids[current_index + 1]

    if request.method == "POST":
        if current_annotation is None:
            return redirect("app_projeto:evaluation_en", batch_id=batch.id, annotator_id=annotator.id)

        action = request.POST.get("action", "save_next")
        form = AnnotationEvaluationForm(request.POST, instance=current_annotation)

        if action == "back":
            if previous_annotation_id:
                return redirect(f"{request.path}?annotation_id={previous_annotation_id}")
            return redirect(f"{request.path}?annotation_id={current_annotation.id}")

        if form.is_valid():
            annotation = form.save()
            annotation.completed = True
            annotation.save()
            if next_annotation_id:
                return redirect(f"{request.path}?annotation_id={next_annotation_id}")
            return redirect("app_projeto:evaluation_en", batch_id=batch.id, annotator_id=annotator.id)
    else:
        form = AnnotationEvaluationForm(instance=current_annotation)

    context = {
        "batch": batch,
        "annotator": annotator,
        "current_annotation": current_annotation,
        "previous_annotation_id": previous_annotation_id,
        "next_annotation_id": next_annotation_id,
        "form": form,
        "total_annotations": total_annotations,
        "done_annotations": done_annotations,
        "progress_percent": progress_percent,
    }
    return render(request, "avaliation.html", context)

def divergence_view(request, batch_id):
    batch = get_object_or_404(Batch, pk=batch_id)
    divergences = AnnotationDivergenceService.get_divergences(batch_id)
    
    context = {
        "batch": batch,
        "divergences": divergences,
    }
    return render(request, "divergences.html", context)

class BatchDetailView(DetailView):
    model = Batch
    context_object_name = 'batches'
    template_name = "batch-detail.html"
    pk_url_kwarg = 'batch_id'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        batch = self.get_object()
        
        # Use batch annotations to compute progress
        total_anotacoes = Annotation.objects.filter(batch=batch).count()
        concluidas = Annotation.objects.filter(batch=batch, labels__isnull=False).count()
        
        context['total_anotacoes'] = total_anotacoes
        context['concluidas'] = concluidas
        context['progresso'] = int((concluidas / total_anotacoes) * 100) if total_anotacoes else 0
        context['annotators'] = Annotator.objects.filter(made_annotations__batch=batch).distinct()
        
        return context


def export_annotations_csv(request):
    """
    Exports each completed annotation as one CSV row, which works well for multiple annotators.

    Short headers keep the spreadsheet readable, and the UTF-8 BOM helps Excel open the file correctly.
    """
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="annotations_export.csv"'
    # BOM: Excel on Windows recognizes UTF-8 and renders accents correctly.
    response.write("\ufeff")

    # One row per completed Annotation, with each annotator on their own line.
    annotations_qs = (
        Annotation.objects.filter(completed=True)
        .select_related(
            "answer__question",
            "answer__metod",
            "answer__project",
            "batch",
            "annotator",
        )
        .prefetch_related("labels")
        .order_by("batch_id", "annotator_id", "answer_id", "id")
    )

    writer = csv.writer(response, delimiter=';')
    # Short labels keep the spreadsheet readable.
    writer.writerow(
        [
            "Annotator",
            "E-mail",
            "Biases",
            "Question (prompt)",
            "Model answer",
            "Model",
            "Project",
            "Project acronym",
            "Annotation ID",
            "Answer ID",
            "Question ID",
            "Batch ID",
            "Updated at",
        ]
    )

    for ann in annotations_qs:
        answer = ann.answer
        project = answer.project
        # Short acronym for filters; full name for spreadsheet context.
        project_acronym = project.acronym
        project_name = project.name
        labels_str = ", ".join(label.name for label in ann.labels.all())
        batch_id = ann.batch_id if ann.batch_id is not None else ""

        writer.writerow(
            [
                ann.annotator.name,
                ann.annotator.email,
                labels_str,
                answer.question.text,
                answer.content,
                answer.metod.name,
                project_name,
                project_acronym,
                ann.id,
                answer.id,
                answer.question_id,
                batch_id,
                ann.updated_at.isoformat() if ann.updated_at else "",
            ]
        )

    return response

    