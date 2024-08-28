from fpdf import FPDF

def generate_pdf_report(student_name: str, recommendations: list) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Report for {student_name}", ln=True, align='C')

    pdf.cell(200, 10, txt="Recommendations:", ln=True, align='L')
    for rec in recommendations:
        pdf.cell(200, 10, txt=f"- {rec}", ln=True, align='L')

    file_name = f"{student_name}_report.pdf"
    pdf.output(file_name)
    return file_name
