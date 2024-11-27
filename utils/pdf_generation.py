from datetime import date
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle, PageBreak, SimpleDocTemplate, Paragraph, Spacer, Image

def generiere_protokoll(data):
    # Dokument-Vorlage erstellen
    doc = SimpleDocTemplate("Lärmprotokoll.pdf", pagesize=A4)
    elements = []

    # Stile für das Layout
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    body_style = styles['BodyText']

    # Logo hinzufügen
    logo_path = "utils/image/Designer.png"
    try:
        logo = Image(logo_path, width=100, height=100)
        elements.append(logo)
    except FileNotFoundError:
        print(f"Logo nicht gefunden: {logo_path}")

    # Kopfzeile
    title = Paragraph("Lärmprotokoll", title_style)
    date_paragraph = Paragraph(f"<b>Erstellt am:</b> {date.today().strftime('%d.%m.%Y')}", body_style)
    elements.append(title)
    elements.append(date_paragraph)
    elements.append(Spacer(1, 20))  # Abstand hinzufügen

    # Beschreibung
    description = Paragraph(
        "Dieses Protokoll dokumentiert Lärmbelastungen im angegebenen Zeitraum. "
        "Die Auswirkungen werden nach einer Skala von 1 bis 5 bewertet. "
        "Die Dauer ist in Minuten angegeben.",
        body_style,
    )
    elements.append(description)
    elements.append(Spacer(1, 20))

    # Tabelle erstellen
    table_data = [
        ['Datum', 'Beginn', 'Ende', 'Dauer (min)', 'Art der Störung', 'Verursacher', 'Auswirkung (1-5)']  # Header
    ]
    for row in data:
        table_data.append([
            row[1], row[2], row[3], int(float(row[4])), row[5], row[6], row[7]
        ])

    # Tabellen-Stil definieren
    table = Table(table_data, colWidths=[60, 50, 50, 60, 120, 120, 60])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header row color
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)  # Header row background color
    ]))

    # Tabelle mit dynamischen Seitenumbrüchen
    elements.append(table)

    # Fußzeile (für jede Seite)
    elements.append(Spacer(1, 40))
    footer = Paragraph(
        "Lärmprotokoll - Erzeugt mit Protokoli der Protokollapp",
        ParagraphStyle(name='Footer', alignment=1, fontSize=10)
    )
    elements.append(footer)

    # Dokument generieren
    doc.build(elements)
