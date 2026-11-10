import os
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
import jinja2
from xhtml2pdf import pisa
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from app.payroll.models.payslip_data import PayslipData

_FONTS_REGISTERED = False

def register_payslip_fonts() -> None:
    """Register Unicode-compatible fonts with ReportLab/xhtml2pdf for rupee symbol (₹)."""
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return

    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Prefer bundled fonts in app/email_service/fonts
    bundled_font_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "email_service", "fonts"))
    bundled_reg = os.path.join(bundled_font_dir, "DejaVuSans.ttf")
    bundled_bold = os.path.join(bundled_font_dir, "DejaVuSans-Bold.ttf")

    reg_font_path = None
    bold_font_path = None

    if os.path.exists(bundled_reg) and os.path.exists(bundled_bold):
        reg_font_path = bundled_reg
        bold_font_path = bundled_bold
    else:
        # Fallback to system fonts if bundled are somehow missing
        system_candidates = [
            ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
            ("C:/Windows/Fonts/calibri.ttf", "C:/Windows/Fonts/calibrib.ttf"),
        ]
        for reg_cand, bold_cand in system_candidates:
            if os.path.exists(reg_cand) and os.path.exists(bold_cand):
                reg_font_path = reg_cand
                bold_font_path = bold_cand
                break

    if reg_font_path and bold_font_path:
        try:
            # Map Helvetica to the registered Unicode TrueType font so all standard styles inherit ₹
            pdfmetrics.registerFont(TTFont("Helvetica", reg_font_path))
            pdfmetrics.registerFont(TTFont("Helvetica-Bold", bold_font_path))
            addMapping("Helvetica", 0, 0, "Helvetica")
            addMapping("Helvetica", 1, 0, "Helvetica-Bold")
            addMapping("Helvetica", 0, 1, "Helvetica")
            addMapping("Helvetica", 1, 1, "Helvetica-Bold")
            _FONTS_REGISTERED = True
        except Exception:
            pass

register_payslip_fonts()


def format_inr_currency(value) -> str:
    """
    Format numeric value as whole rupees with Indian comma grouping.
    Uses Decimal with ROUND_HALF_UP for exact presentation rounding.
    Examples:
        9103.40 -> 9,103
        9103.50 -> 9,104
        9103.94 -> 9,104
        125000  -> 1,25,000
        "-"     -> "-"
    """
    if value is None or value == "" or value == "-":
        return "-"
    try:
        # Normalize to string to avoid float binary representation artifacts
        val_str = str(value).strip().replace(",", "")
        d = Decimal(val_str)
        # Round to whole number using ROUND_HALF_UP
        rounded = d.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        sign = "-" if rounded < 0 else ""
        abs_int = abs(int(rounded))
        s = str(abs_int)

        if len(s) <= 3:
            grouped = s
        else:
            last3 = s[-3:]
            remaining = s[:-3]
            parts = []
            while len(remaining) > 2:
                parts.append(remaining[-2:])
                remaining = remaining[:-2]
            if remaining:
                parts.append(remaining)
            parts.reverse()
            grouped = ",".join(parts) + "," + last3

        return f"{sign}{grouped}"
    except Exception:
        return str(value)


class PayslipPDFCompiler:
    def __init__(self, template_dir: str = None):
        if not template_dir:
            # Default to the email_service/templates directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.join(current_dir, "..", "..", "email_service", "templates")

        self.template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
        self.template_env = jinja2.Environment(loader=self.template_loader)
        # Register custom Jinja filters
        self.template_env.filters["currency_inr"] = format_inr_currency
        self.template_env.filters["rupee"] = format_inr_currency

        # Ensure fonts are registered
        register_payslip_fonts()

    def compile(self, payslip_data: PayslipData) -> bytes:
        template = self.template_env.get_template("payslip_pdf.html")

        # Resolve path to canonical public/favicon.svg
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "..", "public", "favicon.svg"))

        html_out = template.render(logo_path=logo_path, **payslip_data.model_dump())

        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(
            src=html_out,
            dest=pdf_file
        )

        if pisa_status.err:
            raise RuntimeError(f"PDF compilation failed: {pisa_status.err}")

        return pdf_file.getvalue()
