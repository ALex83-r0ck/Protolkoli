from datetime import date
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

def generiere_protokoll(data):
    c = canvas.Canvas('Lärmprotokoll.pdf', pagesize=A4)
    c.drawString(225, 800, "Lärmprotokoll erstellt am: " + date.today().strftime("%d.%m.%Y"))

    c.drawString(50, 780,"Die Dauer ist in Minuten angeben.")
    c.drawString(50, 769,"Die Auswirkungen werden in 5 Stufen ausgewiesen:")
    c.drawString(50, 757,"1: Keine Auswirkungen")
    c.drawString(50, 747,"2: Kleine Auswirkungen")
    c.drawString(50, 737,"3: Mittlere Auswirkungen")
    c.drawString(50, 727,"4: Große Auswirkungen")
    c.drawString(50, 717,"5: Sehr große Auswirkungen")

    # Create a table with the data
    table_data = []
    table_data.append(['Datum', 'Beginn', 'Ende', 'Dauer(min)', 'Art der Störung', 'Verursacher', 'Auswirkung(1-5)'])  # Header row
    for row in data:
        table_data.append([row[1], row[2], row[3], int(float(row[4])), row[5], row[6], row[7]])

    # Create the table
    table = Table(table_data, style=TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header row color
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)  # Header row background color
    ]))

    # Add the table to the PDF
    table.wrapOn(c, 50, 50)
    table.drawOn(c, 50, 600)

    c.save()