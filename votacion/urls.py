from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('votar/', views.votar_view, name='votar'),
    path('resultados/', views.resultados_view, name='resultados'),
    path('reporte/resultados/', views.descargar_reporte_resultados, name='reporte_resultados'),
    path('reporte/auditoria/', views.descargar_reporte_auditoria, name='reporte_auditoria'),
]
