import csv
import io
import datetime as dt

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from models import JobPosition, CandidateProfile, Application

NAVY = colors.HexColor("#0B1736")
TEAL = colors.HexColor("#14B8A6")


def _base_doc(buffer, title):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    elements = [
        Paragraph(f"<b>TalentIQ</b> — {title}", styles["Title"]),
        Paragraph(dt.datetime.utcnow().strftime("Generated %Y-%m-%d %H:%M UTC"), styles["Normal"]),
        Spacer(1, 10 * mm),
    ]
    return doc, elements, styles


def _styled_table(data, col_widths=None):
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table


def generate_position_applicant_report(position: JobPosition) -> bytes:
    buffer = io.BytesIO()
    doc, elements, styles = _base_doc(buffer, f"Position Applicant Report — {position.title}")

    apps = position.applications.order_by(Application.match_score.desc()).all()
    data = [["Candidate", "Match %", "Status", "Applied On"]]
    for a in apps:
        data.append([
            a.candidate.user.name if a.candidate.user else "-",
            f"{round(a.match_score,1)}%",
            a.status,
            a.applied_at.strftime("%Y-%m-%d") if a.applied_at else "-",
        ])
    elements.append(_styled_table(data))
    doc.build(elements)
    return buffer.getvalue()


def generate_candidate_screening_report(candidate: CandidateProfile) -> bytes:
    buffer = io.BytesIO()
    name = candidate.user.name if candidate.user else f"Candidate #{candidate.id}"
    doc, elements, styles = _base_doc(buffer, f"Candidate Screening Report — {name}")

    info = [
        ["Email", candidate.user.email if candidate.user else "-"],
        ["Location", candidate.location or "-"],
        ["Experience (yrs)", str(candidate.experience_years or 0)],
        ["Predicted Category", candidate.predicted_category or "-"],
        ["Skills", ", ".join(candidate.skills_list()) or "-"],
    ]
    elements.append(_styled_table([["Field", "Value"]] + info, col_widths=[120, 320]))
    elements.append(Spacer(1, 8 * mm))

    apps = candidate.applications.all()
    if apps:
        data = [["Position", "Match %", "Status"]]
        for a in apps:
            data.append([a.position.title, f"{round(a.match_score,1)}%", a.status])
        elements.append(_styled_table(data))

    doc.build(elements)
    return buffer.getvalue()


def generate_analytics_report(stats: dict) -> bytes:
    buffer = io.BytesIO()
    doc, elements, styles = _base_doc(buffer, "Recruitment Analytics Report")

    data = [["Metric", "Value"]]
    for key, value in stats.items():
        data.append([key.replace("_", " ").title(), str(value)])
    elements.append(_styled_table(data, col_widths=[250, 150]))
    doc.build(elements)
    return buffer.getvalue()


def generate_csv_export(rows: list[dict]) -> bytes:
    if not rows:
        return b""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")
