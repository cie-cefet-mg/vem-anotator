from django.urls import path

from app_projeto.views.views import avaliation, divergence_view, export_annotations_csv
from app_projeto.views import views
from app_projeto.views import site_access as site_access_views

app_name = "app_projeto"

urlpatterns = [
    path("login/", site_access_views.site_access_login, name="site_access_login_en"),
    path("logout/", site_access_views.site_access_logout, name="site_access_logout_en"),
    path("batch/<int:batch_id>/evaluation/<int:annotator_id>/", avaliation, name="evaluation_en"),
    path("batch/<int:batch_id>/divergences/", divergence_view, name="divergences_en"),
    path("batch/<int:batch_id>/details/", views.BatchDetailView.as_view(), name="batch_detail_en"),
    path("export-annotations/", export_annotations_csv, name="export_annotations_en"),
    path("entrar/", site_access_views.site_access_login, name="site_access_login"),
    path("sair-anotador/", site_access_views.site_access_logout, name="site_access_logout"),
    path('', views.home, name="home"),
    path("avaliation/lote/<int:batch_id>/anotador/<int:annotator_id>/", avaliation, name="avaliation"),
    path("divergencias/lote/<int:batch_id>/", divergence_view, name="divergences"),
    path("lote-detalhes/<int:batch_id>/", views.BatchDetailView.as_view(),name="batch-detail"),
    path("export-annotations/", export_annotations_csv, name="export_annotations"),
]
