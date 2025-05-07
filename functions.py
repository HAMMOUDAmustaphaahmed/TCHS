from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import cm
import pandas as pd
from io import BytesIO
import os
from datetime import datetime, timedelta
import locale
from sqlalchemy.sql import func
from models import db, Paiement, Adherent
import pytz

def generate_bon_de_recette_pdf(adherent, numero_cheque, banque):
    directory = 'bon_de_recette'
    if not os.path.exists(directory):
        os.makedirs(directory)

    pdf_filename = f"{directory}/{adherent.matricule}.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    c.drawString(100, 750, f"Bon de Recette - {adherent.matricule}")
    c.drawString(100, 730, f"Nom : {adherent.nom} {adherent.prenom}")
    c.drawString(100, 710, f"Type d'abonnement : {adherent.type_abonnement}")
    c.drawString(100, 690, f"Type de règlement : {adherent.type_reglement}")
    c.drawString(100, 670, f"Numéro de Chèque : {numero_cheque}")
    c.drawString(100, 650, f"Banque : {banque}")
    c.drawString(100, 630, f"Date d'échéance : {adherent.date_inscription}")

    c.save()

def get_totals_simple():
    subquery = (
        db.session.query(
            Paiement.matricule_adherent,
            func.max(Paiement.date_paiement).label("latest_payment_date")
        )
        .group_by(Paiement.matricule_adherent)
        .subquery()
    )

    results = (
        db.session.query(
            func.sum(Paiement.montant).label("total_montant"),
            func.sum(Paiement.montant_paye).label("total_montant_paye"),
            func.sum(Paiement.montant_reste).label("total_montant_reste"),
        )
        .join(subquery, (Paiement.matricule_adherent == subquery.c.matricule_adherent) &
                         (Paiement.date_paiement == subquery.c.latest_payment_date))
        .first()
    )

    return {
        "total_montant": results.total_montant,
        "total_montant_paye": results.total_montant_paye,
        "total_montant_reste": results.total_montant_reste
    }

def generate_excel(seances, days, creneaux, scope):
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, 'french')
        
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    workbook = writer.book

    header_format = workbook.add_format({
        'bold': True, 
        'bg_color': '#D3D3D3',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    time_header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'border': 1,
        'align': 'center'
    })

    cell_format = workbook.add_format({
        'text_wrap': True,
        'valign': 'top',
        'border': 1
    })

    for day in days:
        data = []
        data.append([f"{day.strftime('%A %d/%m/%Y')}"] + [''] * (len(creneaux)))
        data.append(['Terrain'] + [f"{c['start'].strftime('%H:%M')}-{c['end'].strftime('%H:%M')}" for c in creneaux])
        
        for terrain in range(1, 8):
            row = [f'Terrain {terrain}']
            for creneau in creneaux:
                sessions = [
                    f"{s.groupe}\r\n{s.entraineur}" 
                    for s in seances 
                    if s.date == day.date() 
                    and s.terrain == terrain 
                    and s.heure_debut.strftime('%H:%M') == creneau['start'].strftime('%H:%M')
                ]
                row.append('\n'.join(sessions))
            data.append(row)
        
        df = pd.DataFrame(data[2:], columns=data[1])
        df.to_excel(writer, sheet_name=day.strftime('%A'), index=False, startrow=2, header=False)
        worksheet = writer.sheets[day.strftime('%A')]
        worksheet.merge_range(0, 0, 0, len(creneaux), data[0][0], header_format)
        
        for col_num, value in enumerate(data[1]):
            worksheet.write(1, col_num, value, time_header_format)
        
        worksheet.set_column(0, len(creneaux), 25)
        for row_num in range(2, len(data)+2):
            worksheet.set_row(row_num, 50, cell_format)

    writer.close()
    output.seek(0)
    return output

def generate_pdf(seances, days, creneaux, scope):
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, 'french')

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []

    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#D3D3D3')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ])

    for day in days:
        title = day.strftime('%A %d/%m/%Y').capitalize()
        elements.append(Table([[title]], 
            style=[
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 14),
                ('BOTTOMPADDING', (0,0), (-1,-1), 15),
            ]))
        
        headers = ['Terrain'] + [f"{c['start'].strftime('%H:%M')}\n-\n{c['end'].strftime('%H:%M')}" for c in creneaux]
        data = [headers]

        for terrain in range(1, 8):
            row = [f'Terrain {terrain}']
            for creneau in creneaux:
                sessions = [
                    f"{s.groupe}\n({s.entraineur})" 
                    for s in seances 
                    if s.date == day.date() 
                    and s.terrain == terrain 
                    and s.heure_debut.strftime('%H:%M') == creneau['start'].strftime('%H:%M')
                ]
                row.append('\n\n'.join(sessions))
            data.append(row)

        table = Table(data, repeatRows=1)
        table.setStyle(style)
        
        col_widths = [3*cm] + [3.5*cm]*len(creneaux)
        table._argW = col_widths
        
        elements.append(table)
        elements.append(PageBreak())

    doc.build(elements)
    buffer.seek(0)
    return buffer