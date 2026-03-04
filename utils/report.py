# utils/report.py
# Auto-generates a professional PDF civic report for municipalities

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
import uuid
from datetime import datetime

def generate_report(detections, summary, image_filename):
    """
    Generates a professional PDF road damage report.
    Returns the filename of the generated PDF.
    """

    # Create unique report filename
    report_filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
    report_path = os.path.join("static", "uploads", report_filename)

    # Setup document
    doc = SimpleDocTemplate(
        report_path,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=22,
        textColor=colors.HexColor("#1a1a2e"),
        alignment=TA_CENTER,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        alignment=TA_CENTER,
        spaceAfter=4
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#16213e"),
        spaceBefore=14,
        spaceAfter=6
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        spaceAfter=4
    )

    # Health score color
    score = summary["health_score"]
    if score >= 75:
        score_color = colors.HexColor("#27ae60")   # Green
    elif score >= 50:
        score_color = colors.HexColor("#f39c12")   # Orange
    elif score >= 25:
        score_color = colors.HexColor("#e67e22")   # Dark orange
    else:
        score_color = colors.HexColor("#e74c3c")   # Red

    # Build content
    content = []

    # Header
    content.append(Paragraph("🛣️ RoadSense AI", title_style))
    content.append(Paragraph("Road Damage Detection & Civic Report", subtitle_style))
    content.append(Paragraph(f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", subtitle_style))
    content.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a1a2e")))
    content.append(Spacer(1, 0.15*inch))

    # Road Health Score
    content.append(Paragraph("Road Health Score", section_style))
    health_data = [
        ["Health Score", "Status", "Total Damages", "Recommendation"],
        [
            f"{summary['health_score']} / 100",
            summary["health_label"],
            str(summary["total"]),
            summary["recommendation"]
        ]
    ]
    health_table = Table(health_data, colWidths=[1.2*inch, 1*inch, 1.2*inch, 3.5*inch])
    health_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 1), (0, 1), score_color),
        ("TEXTCOLOR", (0, 1), (0, 1), colors.white),
        ("FONTNAME", (0, 1), (0, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (0, 1), 14),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8f9fa")]),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("WORDWRAP", (3, 1), (3, 1), True),
        ("ALIGN", (3, 1), (3, 1), "LEFT"),
    ]))
    content.append(health_table)
    content.append(Spacer(1, 0.15*inch))

    # Severity Breakdown
    content.append(Paragraph("Damage Severity Breakdown", section_style))
    severity_data = [
        ["Severity", "Count", "Percentage", "Action Required"],
        ["🔴 Severe",   str(summary["severe"]),   f"{summary['severe_pct']}%",   "Immediate repair"],
        ["🟠 Moderate", str(summary["moderate"]), f"{summary['moderate_pct']}%", "Repair within 2 weeks"],
        ["🟢 Minor",    str(summary["minor"]),    f"{summary['minor_pct']}%",    "Monitor & schedule"],
    ]
    severity_table = Table(severity_data, colWidths=[1.5*inch, 1*inch, 1.2*inch, 3.2*inch])
    severity_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16213e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    content.append(severity_table)
    content.append(Spacer(1, 0.15*inch))

    # Damage Type Breakdown
    if summary["damage_types"]:
        content.append(Paragraph("Damage Type Breakdown", section_style))
        type_data = [["Damage Type", "Count"]]
        for dtype, count in summary["damage_types"].items():
            type_data.append([dtype, str(count)])
        type_table = Table(type_data, colWidths=[4*inch, 2*inch])
        type_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3460")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))
        content.append(type_table)
        content.append(Spacer(1, 0.15*inch))

    # Individual Detections
    if detections:
        content.append(Paragraph("Individual Damage Detections", section_style))
        det_data = [["#", "Damage Type", "Severity", "Confidence"]]
        for i, d in enumerate(detections, 1):
            det_data.append([
                str(i),
                d["type"],
                d["severity"],
                d["confidence"]
            ])
        det_table = Table(det_data, colWidths=[0.4*inch, 2.5*inch, 1.2*inch, 1.2*inch])
        det_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3460")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))
        content.append(det_table)

    # Footer
    content.append(Spacer(1, 0.3*inch))
    content.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    content.append(Paragraph(
        "Generated by RoadSense AI | ORIGIN 2026 Hackathon | SIMATS Engineering",
        subtitle_style
    ))

    # Build PDF
    doc.build(content)
    return report_filename