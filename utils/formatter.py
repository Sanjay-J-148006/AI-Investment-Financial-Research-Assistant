import os

def export_report_as_txt(report_text: str, filename: str = "investment_report.txt") -> str:
    """
    Saves report text as a formatted plain text file.
    """
    filepath = os.path.join(".", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)
    return filepath

def export_report_as_pdf(report_text: str, filename: str = "investment_report.pdf") -> str:
    """
    Converts markdown report text into a styled PDF document using ReportLab if available,
    or plain text output if reportlab is unavailable.
    """
    filepath = os.path.join(".", filename)
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib import colors

        doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'DocTitle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#0F172A'), spaceAfter=15
        )
        heading_style = ParagraphStyle(
            'SectionHeading', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor('#1E3A8A'), spaceBefore=12, spaceAfter=6
        )
        body_style = ParagraphStyle(
            'BodyTextCustom', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#334155'), spaceAfter=8
        )

        story = []
        lines = report_text.split("\n")
        for line in lines:
            line_str = line.strip()
            if not line_str:
                story.append(Spacer(1, 6))
                continue
                
            if line_str.startswith("# "):
                clean = line_str.replace("# ", "").replace("📊", "").strip()
                story.append(Paragraph(f"<b>{clean}</b>", title_style))
                story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3B82F6'), spaceAfter=10))
            elif line_str.startswith("### ") or line_str.startswith("## "):
                clean = line_str.replace("### ", "").replace("## ", "").strip()
                story.append(Paragraph(f"<b>{clean}</b>", heading_style))
            elif line_str.startswith("---"):
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceBefore=8, spaceAfter=8))
            elif line_str.startswith("- ") or line_str.startswith("* "):
                clean = line_str[2:].strip()
                story.append(Paragraph(f"• {clean}", body_style))
            else:
                clean = line_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(clean, body_style))

        doc.build(story)
        return filepath
    except ImportError:
        # Fallback to saving plain text if reportlab is not installed
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_text)
        return filepath

