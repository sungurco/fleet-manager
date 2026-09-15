"""
Rapor dışa aktarma yardımcıları: Excel (openpyxl) ve PDF (WeasyPrint).
Görünümlerde (views.py) şu şekilde kullanılır:

    def occupancy_report_excel(request):
        rows = [...]  # rapor verisi
        return export_to_excel("doluluk_raporu", ["Plaka", "Marka", "Doluluk %"], rows)
"""
from django.http import HttpResponse
from django.template.loader import render_to_string
import openpyxl
from openpyxl.styles import Font


def export_to_excel(filename, headers, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for row in rows:
        ws.append(row)
    for col in ws.columns:
        max_len = max(len(str(c.value)) for c in col if c.value is not None) if col else 10
        ws.column_dimensions[col[0].column_letter].width = max_len + 2

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'
    wb.save(response)
    return response


def export_to_pdf(filename, template_name, context):
    from weasyprint import HTML

    html_string = render_to_string(template_name, context)
    pdf_file = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
    return response
