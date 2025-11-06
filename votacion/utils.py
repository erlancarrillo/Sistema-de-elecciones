from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from django.conf import settings
import os

def generar_reporte_resultados(candidatos, total_votos):
    """
    Genera un PDF con los resultados electorales
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, 
                           topMargin=50, bottomMargin=50)
    
    # Contenedor de elementos
    elementos = []
    
    # Estilos
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        'CustomTitle',
        parent=estilos['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    estilo_subtitulo = ParagraphStyle(
        'CustomSubtitle',
        parent=estilos['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    estilo_normal = ParagraphStyle(
        'CustomNormal',
        parent=estilos['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#4a5568')
    )
    
    # Encabezado
    elementos.append(Paragraph("🗳️ REPORTE OFICIAL DE RESULTADOS ELECTORALES", estilo_titulo))
    elementos.append(Paragraph("Sistema de Votación Electoral - Auditoría", estilo_subtitulo))
    elementos.append(Spacer(1, 0.3*inch))
    
    # Información del reporte
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    info_data = [
        ['Fecha de generación:', fecha_actual],
        ['Total de votos emitidos:', str(total_votos)],
        ['Estado del proceso:', 'FINALIZADO' if total_votos > 0 else 'EN PROCESO'],
    ]
    
    info_table = Table(info_data, colWidths=[2.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2d3748')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0'))
    ]))
    
    elementos.append(info_table)
    elementos.append(Spacer(1, 0.4*inch))
    
    # Título de resultados
    elementos.append(Paragraph("RESULTADOS POR CANDIDATO", estilo_subtitulo))
    elementos.append(Spacer(1, 0.2*inch))
    
    # Tabla de resultados
    datos_tabla = [['Pos.', 'Candidato', 'Partido', 'Votos', 'Porcentaje']]
    
    for i, candidato in enumerate(candidatos, 1):
        porcentaje = round((candidato.votos / total_votos * 100), 2) if total_votos > 0 else 0
        datos_tabla.append([
            str(i),
            candidato.nombre_completo,
            candidato.partido_politico,
            str(candidato.votos),
            f"{porcentaje}%"
        ])
    
    tabla_resultados = Table(datos_tabla, colWidths=[0.6*inch, 2.2*inch, 1.8*inch, 0.8*inch, 1*inch])
    
    # Estilos de la tabla
    tabla_style = TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Contenido
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (3, 1), (4, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2c5282')),
    ])
    
    # Resaltar ganador
    if len(candidatos) > 0 and candidatos[0].votos > 0:
        tabla_style.add('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#fef3c7'))
        tabla_style.add('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold')
    
    # Alternar colores de filas
    for i in range(2, len(datos_tabla)):
        if i % 2 == 0:
            tabla_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f7fafc'))
    
    tabla_resultados.setStyle(tabla_style)
    elementos.append(tabla_resultados)
    
    # Pie de página con firma
    elementos.append(Spacer(1, 0.6*inch))
    elementos.append(Paragraph("_" * 80, estilo_normal))
    elementos.append(Spacer(1, 0.2*inch))
    
    firma_data = [
        ['', ''],
        ['_________________________', '_________________________'],
        ['Presidente de Mesa', 'Secretario Electoral'],
    ]
    
    firma_table = Table(firma_data, colWidths=[3*inch, 3*inch])
    firma_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, 1), 20),
    ]))
    
    elementos.append(firma_table)
    
    # Nota de autenticidad
    elementos.append(Spacer(1, 0.3*inch))
    nota = Paragraph(
        "<i>Este documento fue generado automáticamente por el Sistema de Votación Electoral. "
        "Cualquier alteración invalida su autenticidad.</i>",
        ParagraphStyle('Nota', parent=estilos['Normal'], fontSize=8, 
                      textColor=colors.HexColor('#718096'), alignment=TA_CENTER)
    )
    elementos.append(nota)
    
    # Construir PDF
    doc.build(elementos)
    buffer.seek(0)
    return buffer

def generar_reporte_auditoria(votos, ciudadanos_votaron, total_ciudadanos):
    """
    Genera un PDF detallado para auditoría con todos los votos registrados
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, 
                           topMargin=40, bottomMargin=40)
    
    elementos = []
    estilos = getSampleStyleSheet()
    
    estilo_titulo = ParagraphStyle(
        'AuditTitle',
        parent=estilos['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#742a2a'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    estilo_seccion = ParagraphStyle(
        'Section',
        parent=estilos['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    # Encabezado de auditoría
    elementos.append(Paragraph("🔍 REPORTE DE AUDITORÍA ELECTORAL", estilo_titulo))
    elementos.append(Paragraph("Registro Detallado de Votos - Uso Interno", 
                              ParagraphStyle('Sub', parent=estilos['Normal'], 
                                           fontSize=11, alignment=TA_CENTER, 
                                           textColor=colors.HexColor('#718096'))))
    elementos.append(Spacer(1, 0.3*inch))
    
    # Información de auditoría
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    info_auditoria = [
        ['Fecha de auditoría:', fecha_actual],
        ['Total de ciudadanos registrados:', str(total_ciudadanos)],
        ['Ciudadanos que votaron:', str(ciudadanos_votaron)],
        ['Porcentaje de participación:', f"{round((ciudadanos_votaron/total_ciudadanos*100), 2)}%" if total_ciudadanos > 0 else "0%"],
        ['Total de votos registrados:', str(votos.count())],
    ]
    
    info_table = Table(info_auditoria, colWidths=[3*inch, 2.5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fed7d7')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2d3748')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#fc8181'))
    ]))
    
    elementos.append(info_table)
    elementos.append(Spacer(1, 0.3*inch))
    
    # Tabla de votos detallados
    elementos.append(Paragraph("REGISTRO DETALLADO DE VOTOS", estilo_seccion))
    elementos.append(Spacer(1, 0.1*inch))
    
    datos_votos = [['#', 'Ciudadano', 'Cédula', 'Candidato Elegido', 'Fecha y Hora']]
    
    for i, voto in enumerate(votos, 1):
        datos_votos.append([
            str(i),
            voto.ciudadano.nombre_completo[:25],
            voto.ciudadano.cedula,
            voto.candidato.nombre_completo[:25],
            voto.fecha_hora.strftime("%d/%m/%Y %H:%M:%S")
        ])
    
    tabla_votos = Table(datos_votos, colWidths=[0.4*inch, 1.8*inch, 1*inch, 1.8*inch, 1.3*inch])
    
    tabla_votos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#742a2a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#742a2a')),
    ]))
    
    # Alternar colores
    for i in range(1, len(datos_votos)):
        if i % 2 == 0:
            tabla_votos.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f7fafc'))
            ]))
    
    elementos.append(tabla_votos)
    
    # Advertencia de confidencialidad
    elementos.append(Spacer(1, 0.4*inch))
    advertencia = Paragraph(
        "<b>⚠️ DOCUMENTO CONFIDENCIAL</b><br/>"
        "<i>Este reporte contiene información sensible y está destinado exclusivamente "
        "para fines de auditoría electoral. Su distribución no autorizada está prohibida "
        "por la ley electoral.</i>",
        ParagraphStyle('Warning', parent=estilos['Normal'], fontSize=8, 
                      textColor=colors.HexColor('#c53030'), alignment=TA_CENTER,
                      borderColor=colors.HexColor('#fc8181'), borderWidth=1,
                      borderPadding=10, backColor=colors.HexColor('#fff5f5'))
    )
    elementos.append(advertencia)
    
    # Construir PDF
    doc.build(elementos)
    buffer.seek(0)
    return buffer