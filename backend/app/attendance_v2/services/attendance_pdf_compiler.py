import os
from io import BytesIO
import jinja2
from xhtml2pdf import pisa
from app.payroll.services.payslip_pdf_compiler import register_payslip_fonts

class AttendancePDFCompiler:
    def __init__(self, template_dir: str = None):
        if not template_dir:
            # Default to backend/app/email_service/templates
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "email_service", "templates"))

        self.template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
        self.template_env = jinja2.Environment(loader=self.template_loader)

        # Register Unicode DejaVu fonts
        register_payslip_fonts()

    def compile(self, report_data: dict) -> bytes:
        """
        Compiles the attendance report data dict into PDF binary bytes using xhtml2pdf.
        """
        template = self.template_env.get_template("attendance_report_pdf.html")
        html_out = template.render(**report_data)

        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(
            src=html_out,
            dest=pdf_file
        )

        if pisa_status.err:
            raise RuntimeError(f"Attendance PDF compilation failed: {pisa_status.err}")

        return pdf_file.getvalue()
