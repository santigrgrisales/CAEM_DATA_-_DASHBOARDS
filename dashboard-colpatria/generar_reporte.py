"""
Generar Reporte PDF con Lista de Entidades y Ciudades Normalizadas
====================================================================
Este script genera un PDF con las listas de entidades y ciudades normalizadas
junto con sus variantes.

Ejecutar: python generar_reporte.py
Resultado: reporte_normalizacion.pdf
"""

import json
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors

# Rutas
DATA_DIR = os.path.join(os.path.dirname(__file__), "dist", "data")
OUTPUT_PDF = os.path.join(os.path.dirname(__file__), "reporte_normalizacion.pdf")

def cargar_datos():
    """Carga los datos de variantes"""
    with open(os.path.join(DATA_DIR, "variantes_entidad.json"), "r", encoding="utf-8") as f:
        entidades = json.load(f)
    
    with open(os.path.join(DATA_DIR, "variantes_ciudad.json"), "r", encoding="utf-8") as f:
        ciudades = json.load(f)
    
    return entidades, ciudades

def crear_tabla_variantes(data, titulo, max_variantes=15):
    """Crea una tabla con las variantes de un elemento"""
    elements = []
    
    # Título de la sección
    elements.append(Paragraph(titulo, styles['Heading2']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Encabezado de tabla
    table_data = [['#', 'Nombre Normalizado', 'Variante Original', 'Cantidad']]
    
    count = 1
    for normalized_name, variants in sorted(data.items()):
        # Ordenar variantes por cantidad (mayor a menor)
        sorted_variants = sorted(variants, key=lambda x: x.get('cantidad', 0), reverse=True)
        
        for variant in sorted_variants[:max_variantes]:
            original = variant.get('original', '')[:50]  # Limitar longitud
            qty = variant.get('cantidad', 0)
            
            table_data.append([
                str(count),
                normalized_name[:30],
                original[:40],
                f"{qty:,}"
            ])
            count += 1
            
            # Limitar total de filas para no hacer el PDF demasiado grande
            if count > 200:
                break
        
        if count > 200:
            break
    
    # Crear tabla
    table = Table(table_data, colWidths=[0.3*inch, 2.2*inch, 2.5*inch, 0.8*inch])
    
    # Estilo de tabla
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1d23')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#4fc3f7')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    
    return elements

def crear_resumen(entidades, ciudades):
    """Crea una página de resumen"""
    elements = []
    
    elements.append(Paragraph("RESUMEN DE NORMALIZACIÓN", styles['ReporteTitle']))
    elements.append(Spacer(1, 0.5*inch))
    
    # Estadísticas
    total_entidades = len(entidades)
    total_ciudades = len(ciudades)
    
    # Contar total de variantes
    total_var_entidades = sum(len(v) for v in entidades.values())
    total_var_ciudades = sum(len(v) for v in ciudades.values())
    
    # Crear tabla de resumen
    resumen_data = [
        ['Elemento', 'Normalizados', 'Variantes Total'],
        ['Entidades', f"{total_entidades:,}", f"{total_var_entidades:,}"],
        ['Ciudades', f"{total_ciudades:,}", f"{total_var_ciudades:,}"],
        ['TOTAL', f"{total_entidades + total_ciudades:,}", f"{total_var_entidades + total_var_ciudades:,}"],
    ]
    
    table = Table(resumen_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1d23')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#4fc3f7')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e8f5e9'), colors.white]),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Descripción
    descripcion = """
    <b>Descripción del Reporte:</b><br/><br/>
    Este documento presenta las listas de entidades y ciudades normalizadas utilizadas en el 
    Dashboard de Oficios Colpatria. Cada elemento normalizado incluye sus variantes originales 
    encontradas en los datos, junto con la cantidad de registros asociados.<br/><br/>
    <b>Metodología:</b> Se aplicaron reglas de normalización para estandarizar nombres de 
    entidades y ciudades, consolidando variantes ortográficas, acentos, mayúsculas/minúsculas y 
    formatos diferentes.
    """
    
    elements.append(Paragraph(descripcion, styles['Normal']))
    
    return elements

def crear_top_variantes(entidades, ciudades, top_n=30):
    """Crea tablas con los elementos más variantes"""
    elements = []
    
    elements.append(Paragraph("TOP ENTIDADES CON MÁS VARIANTES", styles['Heading2']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Top entidades por cantidad de variantes
    top_ent = sorted(entidades.items(), key=lambda x: len(x[1]), reverse=True)[:top_n]
    
    table_data = [['#', 'Entidad Normalizada', 'Nº Variantes']]
    for i, (name, variants) in enumerate(top_ent, 1):
        table_data.append([str(i), name[:50], str(len(variants))])
    
    table = Table(table_data, colWidths=[0.3*inch, 4*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1d23')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#4fc3f7')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.4*inch))
    
    elements.append(Paragraph("TOP CIUDADES CON MÁS VARIANTES", styles['Heading2']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Top ciudades por cantidad de variantes
    top_ciu = sorted(ciudades.items(), key=lambda x: len(x[1]), reverse=True)[:top_n]
    
    table_data = [['#', 'Ciudad Normalizada', 'Nº Variantes']]
    for i, (name, variants) in enumerate(top_ciu, 1):
        table_data.append([str(i), name[:50], str(len(variants))])
    
    table = Table(table_data, colWidths=[0.3*inch, 4*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1d23')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#4fc3f7')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(table)
    
    return elements

def generar_pdf(entidades, ciudades):
    """Genera el PDF completo con TODAS las ciudades y entidades"""
    print("📄 Generando PDF (versión completa)...")
    
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        rightMargin=0.4*inch,
        leftMargin=0.4*inch,
        topMargin=0.4*inch,
        bottomMargin=0.4*inch
    )
    
    story = []
    
    # Página 1: Resumen
    print("   - Agregando resumen...")
    story.extend(crear_resumen(entidades, ciudades))
    story.append(PageBreak())
    
    # ============================================
    # TODAS LAS CIUDADES (ordenadas por cantidad)
    # ============================================
    print("   - Agregando TODAS las ciudades...")
    story.append(Paragraph("DIRECTORIO COMPLETO DE CIUDADES NORMALIZADAS", styles['ReporteHeading1']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Total: {len(ciudades):,} ciudades con {sum(len(v) for v in ciudades.values()):,} variantes", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Ciudades ordenadas por cantidad total
    ciudades_ordenadas = sorted(
        ciudades.items(),
        key=lambda x: sum(v.get('cantidad', 0) for v in x[1]),
        reverse=True
    )
    
    # Procesar en grupos para no exceder memoria
    ciudades_por_pagina = 3  # 3 ciudades por página para mantener legible
    
    for i, (normalized_name, variants) in enumerate(ciudades_ordenadas):
        # Ordenar variantes por cantidad
        variants_sorted = sorted(variants, key=lambda x: x.get('cantidad', 0), reverse=True)
        
        # Título de la ciudad
        total_reg = sum(v.get('cantidad', 0) for v in variants)
        story.append(Paragraph(
            f"<b>{normalized_name}</b> ({total_reg:,} registros, {len(variants)} variantes)",
            styles['ReporteHeading3']
        ))
        
        # Tabla compacta de variantes
        var_data = [['Variante Original', 'Cantidad']]
        for v in variants_sorted:
            var_data.append([
                v.get('original', '')[:55],
                f"{v.get('cantidad', 0):,}"
            ])
        
        # Ancho de columnas ajustado paraPDF más compacto
        t = Table(var_data, colWidths=[4.8*inch, 0.6*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e3f2fd')),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.15*inch))
        
        # Nueva página cada ciertas ciudades
        if (i + 1) % ciudades_por_pagina == 0:
            story.append(PageBreak())
    
    story.append(PageBreak())
    
    # ============================================
    # TODAS LAS ENTIDADES (ordenadas por cantidad)
    # ============================================
    print("   - Agregando TODAS las entidades...")
    story.append(Paragraph("DIRECTORIO COMPLETO DE ENTIDADES NORMALIZADAS", styles['ReporteHeading1']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Total: {len(entidades):,} entidades con {sum(len(v) for v in entidades.values()):,} variantes", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Entidades ordenadas por cantidad total
    entidades_ordenadas = sorted(
        entidades.items(),
        key=lambda x: sum(v.get('cantidad', 0) for v in x[1]),
        reverse=True
    )
    
    # Procesar en grupos
    entidades_por_pagina = 2  # 2 entidades por página
    
    for i, (normalized_name, variants) in enumerate(entidades_ordenadas):
        # Ordenar variantes por cantidad
        variants_sorted = sorted(variants, key=lambda x: x.get('cantidad', 0), reverse=True)
        
        # Título de la entidad
        total_reg = sum(v.get('cantidad', 0) for v in variants)
        story.append(Paragraph(
            f"<b>{normalized_name}</b> ({total_reg:,} registros, {len(variants)} variantes)",
            styles['ReporteHeading3']
        ))
        
        # Tabla compacta de variantes
        var_data = [['Variante Original', 'Cantidad', 'Ciudad']]
        for v in variants_sorted[:15]:  # Máximo 15 variantes por entidad para no exceder
            ciudades = v.get('ciudades', '')[:30]
            var_data.append([
                v.get('original', '')[:45],
                f"{v.get('cantidad', 0):,}",
                ciudades
            ])
        
        # Si hay más de 15, indicar
        if len(variants_sorted) > 15:
            var_data.append(['... y ' + str(len(variants_sorted) - 15) + ' variantes más', '', ''])
        
        t = Table(var_data, colWidths=[3.5*inch, 0.7*inch, 1.2*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fff3e0')),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.15*inch))
        
        # Nueva página cada ciertas entidades
        if (i + 1) % entidades_por_pagina == 0:
            story.append(PageBreak())
        
        # Progreso cada 500 entidades
        if (i + 1) % 500 == 0:
            print(f"      - Procesando entidad {i+1:,} de {len(entidades):,}...")
    
    # Generar documento
    doc.build(story)
    
    size = os.path.getsize(OUTPUT_PDF) / 1024
    print(f"✅ PDF generado: {OUTPUT_PDF} ({size:.1f} KB)")

if __name__ == "__main__":
    # Estilos - crear copia para evitar conflictos
    styles = getSampleStyleSheet()
    
    # Crear estilos personalizados con nombres únicos
    styles.add(ParagraphStyle(name='ReporteTitle', parent=styles['Title'], fontSize=18, spaceAfter=20, textColor=colors.HexColor('#1a1d23')))
    styles.add(ParagraphStyle(name='ReporteHeading1', parent=styles['Heading1'], fontSize=16, spaceAfter=15, textColor=colors.HexColor('#1a1d23')))
    styles.add(ParagraphStyle(name='ReporteHeading2', parent=styles['Heading2'], fontSize=14, spaceAfter=10, textColor=colors.HexColor('#1a1d23')))
    styles.add(ParagraphStyle(name='ReporteHeading3', parent=styles['Heading3'], fontSize=11, spaceAfter=5, textColor=colors.HexColor('#333333')))
    
    print("=" * 60)
    print("GENERADOR DE REPORTE DE NORMALIZACIÓN")
    print("=" * 60)
    
    # Cargar datos
    print("\n📂 Cargando datos...")
    entidades, ciudades = cargar_datos()
    
    print(f"   - Entidades: {len(entidades):,}")
    print(f"   - Ciudades: {len(ciudades):,}")
    
    # Generar PDF
    generar_pdf(entidades, ciudades)
    
    print("\n🎉 ¡Proceso completado!")
    print(f"   Archivo: {OUTPUT_PDF}")

