import hashlib

class PayslipPDFGenerator:
    @staticmethod
    def generate_pdf(payslip_data: dict) -> str:
        # In a real system, this uses reportlab or wkhtmltopdf.
        # For the engine logic, we simulate the PDF generation.
        pdf_path = f"/storage/payslips/{payslip_data['employeeId']}_{payslip_data['month']}_{payslip_data['year']}_v{payslip_data['version']}.pdf"
        return pdf_path

class ChecksumGenerator:
    @staticmethod
    def generate_checksum(data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

class EmailSender:
    @staticmethod
    def send_payslip_email(employee_email: str, employee_name: str, month: int, year: int, net_salary: float, download_link: str):
        # Simulated SMTP sending
        html_template = f'''
        <h2>Salary Payslip - {month}/{year}</h2>
        <p>Dear {employee_name},</p>
        <p>Your payslip for {month}/{year} has been published.</p>
        <p>Net Salary: {net_salary}</p>
        <a href="{download_link}">Download Payslip</a>
        '''
        return True
