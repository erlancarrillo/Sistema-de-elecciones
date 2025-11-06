from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.views.decorators.http import require_http_methods
from .models import Ciudadano, Candidato, Voto
from .forms import RegistroForm

from django.http import HttpResponse
from .utils import generar_reporte_resultados, generar_reporte_auditoria
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Ahora puedes votar.')
            return redirect('votar')
        else:
            messages.error(request, 'Error en el registro. Por favor verifica los datos.')
    else:
        form = RegistroForm()
    return render(request, 'votacion/registro.html', {'form': form})

@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('votar')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'votacion/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def votar_view(request):
    try:
        ciudadano = request.user.ciudadano
    except Ciudadano.DoesNotExist:
        messages.error(request, 'No estás registrado como ciudadano.')
        return redirect('login')
    
    if ciudadano.ha_votado:
        messages.warning(request, 'Ya has ejercido tu derecho al voto.')
        return redirect('resultados')
    
    candidatos = Candidato.objects.all()
    
    if request.method == 'POST':
        candidato_id = request.POST.get('candidato_id')
        if candidato_id:
            candidato = get_object_or_404(Candidato, id=candidato_id)
            
            with transaction.atomic():
                # Crear el voto
                Voto.objects.create(ciudadano=ciudadano, candidato=candidato)
                # Incrementar contador
                candidato.votos += 1
                candidato.save()
                # Marcar como votado
                ciudadano.ha_votado = True
                ciudadano.save()
            
            messages.success(request, '¡Tu voto ha sido registrado exitosamente!')
            return redirect('resultados')
        else:
            messages.error(request, 'Debes seleccionar un candidato.')
    
    return render(request, 'votacion/votar.html', {
        'candidatos': candidatos,
        'ciudadano': ciudadano
    })

@login_required
def resultados_view(request):
    try:
        ciudadano = request.user.ciudadano
    except Ciudadano.DoesNotExist:
        messages.error(request, 'No estás registrado como ciudadano.')
        return redirect('login')
    
    candidatos = Candidato.objects.all().order_by('-votos', 'numero')
    total_votos = sum(c.votos for c in candidatos)
    
    # Calcular porcentajes y agregar a cada candidato
    candidatos_con_stats = []
    for candidato in candidatos:
        candidato.porcentaje = round((candidato.votos / total_votos * 100), 1) if total_votos > 0 else 0
        candidatos_con_stats.append(candidato)
    
    return render(request, 'votacion/resultados.html', {
        'candidatos': candidatos_con_stats,
        'total_votos': total_votos,
        'ha_votado': ciudadano.ha_votado
    })

@login_required
def descargar_reporte_resultados(request):
    """
    Genera y descarga el reporte de resultados en PDF
    """
    candidatos = Candidato.objects.all().order_by('-votos', 'numero')
    total_votos = sum(c.votos for c in candidatos)
    
    # Generar PDF
    buffer = generar_reporte_resultados(candidatos, total_votos)
    
    # Preparar respuesta
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Resultados_Electorales_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    response.write(buffer.getvalue())
    
    return response

@staff_member_required  # Solo administradores
def descargar_reporte_auditoria(request):
    """
    Genera y descarga el reporte de auditoría detallado en PDF
    Solo accesible para administradores
    """
    votos = Voto.objects.all().select_related('ciudadano', 'candidato').order_by('fecha_hora')
    ciudadanos_votaron = Ciudadano.objects.filter(ha_votado=True).count()
    total_ciudadanos = Ciudadano.objects.count()
    
    # Generar PDF
    buffer = generar_reporte_auditoria(votos, ciudadanos_votaron, total_ciudadanos)
    
    # Preparar respuesta
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Auditoria_Electoral_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    response.write(buffer.getvalue())
    
    return response