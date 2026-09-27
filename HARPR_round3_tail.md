# Harpr — Round 3 tail: Bulletin PDF and settings

**This is the continuation of `HARPR_fix_round3.md`.** Sections S1
through S4 in that file are already applied. This file covers S5
(the bulletin PDF rewrite and settings grouping) and S6 (commit and
push).

Do not re-apply S1 through S4.

---

## Before you start

**Environment:**

```
cd /root/harpr && . .venv/bin/activate
```

**Verification after each section:**

```
python manage.py check
python manage.py test church
```

---

## Section S5 — Upgrade the bulletin PDF

The current PDF is a plain table. This replaces it with a proper church
bulletin layout: header with church name, programme, announcements on
page 2, and a footer with contact details and the verse.

### S5.1 Replace `church/services/pdf.py`

Overwrite the file completely:

```
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
        elements.append(Paragraph("No items scheduled for this service.", item_meta))

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
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HAIRLINE, spaceAfter=10))
        for announcement in announcements:
            elements.append(
                Paragraph(f"&bull; {escape(announcement.body)}", announcement_style)
            )

    elements.append(Spacer(1, 12 * mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=HAIRLINE))

    if service.church.footer_verse:
        elements.append(Paragraph(escape(service.church.footer_verse), verse_style))

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
```

### S5.2 Verify

```
python manage.py check
python manage.py test church
```

Visit `/c/grace-covenant/` and click "Download PDF". The PDF should now
have: church name at the top, "Sunday Worship Bulletin" subtitle, the
service name and date, an Order of Service table, announcements on
page 2, and a footer with contacts and verse.

### S5.3 Group the settings form

The contact and verse fields currently render flat on `/settings/`.
Group them into two visible sections.

In `church/templates/church/settings.html`, find this line:

```
      {{ form.as_p }}
```

Replace it with:

```
      <fieldset class="form-section">
        <legend>Church identity</legend>
        <div class="form-row"><label for="{{ form.name.id_for_label }}">Name</label>{{ form.name }}</div>
        <div class="form-row"><label for="{{ form.slug.id_for_label }}">URL slug</label>{{ form.slug }}</div>
        <div class="form-row"><label for="{{ form.worship_day.id_for_label }}">Worship day</label>{{ form.worship_day }}</div>
        <div class="form-row"><label for="{{ form.timezone.id_for_label }}">Timezone</label>{{ form.timezone }}</div>
        <div class="form-row"><label for="{{ form.address.id_for_label }}">Address</label>{{ form.address }}</div>
        <div class="form-row"><label for="{{ form.logo.id_for_label }}">Logo</label>{{ form.logo }}</div>
      </fieldset>

      <fieldset class="form-section">
        <legend>Bulletin footer</legend>
        <p class="muted">These appear at the bottom of every bulletin PDF and on the public schedule page.</p>
        <div class="form-row"><label for="{{ form.footer_verse.id_for_label }}">Verse or message</label>{{ form.footer_verse }}</div>
        <div class="form-row"><label for="{{ form.contact_phone.id_for_label }}">Contact phone</label>{{ form.contact_phone }}</div>
        <div class="form-row"><label for="{{ form.contact_email.id_for_label }}">Contact email</label>{{ form.contact_email }}</div>
        <div class="form-row"><label for="{{ form.contact_whatsapp.id_for_label }}">Contact WhatsApp</label>{{ form.contact_whatsapp }}<small class="muted">Digits only, including country code. e.g. 260971234567</small></div>
      </fieldset>
```

### S5.4 Verify

Reload `/settings/`. The form should show two grouped sections. Fill in
the footer fields, save, then download a bulletin PDF and confirm the
new footer appears.

---

## Section S6 — Commit and push

```
cd /root/harpr
python manage.py check
python manage.py test church
python manage.py makemigrations --check --dry-run
```

The third command must print "No changes detected."

```
git add -A
git status --short
```

Review the list. It should include:

- `church/templates/church/members.html`
- `church/templates/church/announcements.html`
- `church/templates/church/dashboard.html`
- `church/templates/church/settings.html`
- `church/views/admin_views.py`
- `church/management/commands/seed_demo.py`
- `church/services/pdf.py`

If anything looks wrong, stop and report the full `git status --short`
output before committing.

Otherwise:

```
git commit -m "Fix member and announcement templates, add week navigation, rebuild seed data, upgrade bulletin PDF, group settings form"
git push origin main
```

Report the full output of `git push origin main`.

Then remove the spec files:

```
git rm HARPR_fix_round3.md HARPR_round3_tail.md 2>/dev/null || rm -f HARPR_fix_round3.md HARPR_round3_tail.md
git commit -m "Remove applied round 3 spec"
git push origin main
```

Report the output of the second push.

---

## End of round 3

Report in one message:

- Output of `python manage.py check`
- Output of `python manage.py test church`
- Confirmation that `/members/` loads without errors
- Confirmation that `/announcements/` loads without errors
- Confirmation that Previous / Today / Next work on `/dashboard/`
- Confirmation that the dashboard shows services from July through November
- Confirmation that the AI insights page shows insights
- Confirmation that the bulletin PDF has announcements on page 2 and a footer
- Both push outputs