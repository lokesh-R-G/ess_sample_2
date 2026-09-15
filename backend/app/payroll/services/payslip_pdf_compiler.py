import os
import jinja2
from xhtml2pdf import pisa
from io import BytesIO
from app.payroll.models.payslip_data import PayslipData

class PayslipPDFCompiler:
    def __init__(self, template_dir: str = None):
        if not template_dir:
            # Default to the email_service/templates directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.join(current_dir, "..", "..", "email_service", "templates")
            
        self.template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
        self.template_env = jinja2.Environment(loader=self.template_loader)

    def compile(self, payslip_data: PayslipData) -> bytes:
        template = self.template_env.get_template("payslip_pdf.html")
        html_out = template.render(**payslip_data.model_dump())
        
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(
            src=html_out,
            dest=pdf_file
        )
        
        if pisa_status.err:
            raise RuntimeError(f"PDF compilation failed: {pisa_status.err}")
            
        return pdf_file.getvalue()
