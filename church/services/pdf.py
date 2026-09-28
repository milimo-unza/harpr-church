from reportlab.lib import colors
import io
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ACCENT = HexColor("#a85430")
DARK = HexColor("#2b2823")
MUTED = HexColor("#6f6a60")
HAIRLINE = HexColor("#d9d4c6")
CREAM = HexColor("#f7f3ea")


def generate_bulletin_pdf(service):
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        title=f"{service.church.name} - {service.name}",
        author=service.church.name,
    )

    styles = getSampleStyleSheet()

    church_name = ParagraphStyle(
        "ChurchName", parent=styles["Heading1"],
        fontName="Helvetica-Bold", fontSize=20,
        textColor=DARK, alignment=TA_CENTER, spaceAfter=2,
    )
    bulletin_sub = ParagraphStyle(
        "BulletinSub", parent=styles["Normal"],
        fontName="Helvetica-Oblique", fontSize=10,
        textColor=MUTED, alignment=TA_CENTER, spaceAfter=10,
    )
    service_name = ParagraphStyle(
        "ServiceName", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=15,
        textColor=DARK, alignment=TA_CENTER, spaceAfter=2,
    )
    service_date = ParagraphStyle(
        "ServiceDate", parent=styles["Normal"],
        fontName="Helvetica", fontSize=11,
        textColor=MUTED, alignment=TA_CENTER, spaceAfter=12,
    )
    section_head = ParagraphStyle(
        "SectionHead", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=11,
        textColor=ACCENT, spaceBefore=10, spaceAfter=6,
    )
    item_title = ParagraphStyle(
        "ItemTitle", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=10,
        textColor=DARK,
    )
    item_meta = ParagraphStyle(
        "ItemMeta", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9,
        textColor=MUTED,
    )
    announcement_style = ParagraphStyle(
        "Announcement", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10,
        textColor=DARK, spaceAfter=6, leading=14,
    )
    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9,
        textColor=MUTED, alignment=TA_CENTER, spaceBefore=6,
    )
    verse_style = ParagraphStyle(
        "Verse", parent=styles["Normal"],
        fontName="Helvetica-Oblique", fontSize=10,
        textColor=MUTED, alignment=TA_CENTER, spaceBefore=4,
    )

    elements = [
        Paragraph(escape(service.church.name), church_name),
        Paragraph("Sunday Worship Bulletin", bulletin_sub),
        HRFlowable(width="100%", thickness=0.5, color=HAIRLINE, spaceAfter=10),
        Paragraph(escape(service.name), service_name),
        Paragraph(service.date.strftime("%A, %d %B %Y"), service_date),
    ]

    elements.append(Paragraph("Order of Service", section_head))

    data = [["Time", "Item", "Department", "Assigned To"]]
    items = (
        service.items
        .select_related("responsible_department")
        .prefetch_related("assignments")
        .order_by("order")
    )
    for item in items:
        department = item.responsible_department.name if item.responsible_department else "-"
        assignments = ", ".join(
            f"{a.person_name} ({a.role})" for a in item.assignments.all()
        ) or "-"
        data.append([
            Paragraph(item.planned_start.strftime("%H:%M"), item_title),
            Paragraph(escape(item.title), item_title),
            Paragraph(escape(department), item_meta),
            Paragraph(escape(assignments), item_meta),
        ])

    if len(data) > 1:
        table = Table(data, colWidths=[18 * mm, 62 * mm, 38 * mm, 52 * mm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), CREAM),
            ("TEXTCOLOR", (0, 0), (-1, 0), DARK),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("GRID", (0, 0), (-1, -1), 0.4, HAIRLINE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
    else:
        elements.append(
            Paragraph("No items scheduled for this service.", item_meta))

    from django.utils import timezone
    today = timezone.localdate()

    announcements = service.church.announcements.filter(
        is_paused=False, show_on_public=True,
        start_date__lte=today, end_date__gte=today,
    ).order_by("start_date")

    if announcements.exists():
        elements.append(PageBreak())
        elements.append(Paragraph(escape(service.church.name), church_name))
        elements.append(Paragraph("Announcements", bulletin_sub))
        elements.append(HRFlowable(width="100%", thickness=0.5,
                        color=HAIRLINE, spaceAfter=10))
        for announcement in announcements:
            elements.append(
                Paragraph(
                    f"&bull; {escape(announcement.body)}", announcement_style)
            )

    elements.append(Spacer(1, 12 * mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=HAIRLINE))

    if service.church.footer_verse:
        elements.append(
            Paragraph(escape(service.church.footer_verse), verse_style))

    contacts = []
    if service.church.contact_phone:
        contacts.append(f"Tel: {service.church.contact_phone}")
    if service.church.contact_email:
        contacts.append(f"Email: {service.church.contact_email}")
    if service.church.contact_whatsapp:
        contacts.append(f"WhatsApp: +{service.church.contact_whatsapp}")
    if contacts:
        elements.append(Paragraph(
            " &bull; ".join(escape(c) for c in contacts), footer_style
        ))

    elements.append(Paragraph(
        f"Generated by Harpr - {escape(service.church.name)}", footer_style
    ))

    document.build(elements)
    buffer.seek(0)
    return buffer
