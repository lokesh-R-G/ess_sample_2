import hashlib

class PayslipPDFGenerator:
    @staticmethod
    def generate_pdf(payslip_data: dict) -> str:
        import os
        from app.payroll.models.payslip_data import PayslipData
        from app.payroll.services.payslip_pdf_compiler import PayslipPDFCompiler
        
        # Hydrate PayslipData
        p_data = PayslipData(**payslip_data)
        
        # Storage Path
        c_id = p_data.companyName.replace(" ", "_") # Actually, companyId is better, but it's not in PayslipData except via URL path. Wait, payslip_service already passes the right dir?
        # Let's just generate it and save it to the path specified
        pdf_path = f"storage/payslips/{p_data.periodStart[:4]}/{p_data.periodStart[5:7]}/{p_data.companyName}/{p_data.employeeCode}_{p_data.payrollMonth}_Payslip.pdf"
        
        pdf_abs_path = os.path.join(os.getcwd(), pdf_path)
        os.makedirs(os.path.dirname(pdf_abs_path), exist_ok=True)
        
        # Compile PDF
        compiler = PayslipPDFCompiler()
        pdf_bytes = compiler.compile(p_data)
        
        with open(pdf_abs_path, "wb") as f:
            f.write(pdf_bytes)
            
        return pdf_abs_path

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
