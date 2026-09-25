from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.lib.colors import HexColor

from .supabase import SupabaseClient, SupabaseError


def invoice_pdf(request, sale_id):
    if not request.session.get("jc_admin"):
        return redirect("login")
    try:
        db = SupabaseClient()
        sale = (db.select("sales", filters={"id": f"eq.{int(sale_id)}"}) or [None])[0]
        if not sale:
            return HttpResponse("Bill not found", status=404)
        items = db.select("sale_items", filters={"sale_id": f"eq.{int(sale_id)}"}, order="id.asc")
        settings = (db.select("shop_settings", filters={"id": "eq.1"}) or [{}])[0]

        buf = BytesIO()
        width, height = A5
        c = canvas.Canvas(buf, pagesize=A5)
        purple = HexColor("#8B09A2")
        c.setFillColor(purple)
        c.setFont("Helvetica-Bold", 19)
        c.drawCentredString(width / 2, height - 42, settings.get("shop_name") or "JUICE CRAFT")
        c.setFont("Helvetica", 8.5)
        y = height - 58
        if settings.get("address"):
            c.drawCentredString(width / 2, y, str(settings.get("address"))[:80])
            y -= 11
        if settings.get("phone"):
            c.drawCentredString(width / 2, y, str(settings.get("phone")))
            y -= 11
        c.setStrokeColor(purple)
        c.line(28, y - 2, width - 28, y - 2)
        y -= 18

        c.setFont("Helvetica-Bold", 9)
        c.drawString(28, y, f"Bill: {sale.get('bill_number', '')}")
        c.setFont("Helvetica", 8.5)
        y -= 13
        created = str(sale.get("created_at", "")).replace("T", " ")[:19]
        c.drawString(28, y, f"Date: {created}")
        c.drawRightString(width - 28, y, f"Payment: {sale.get('payment_method', '')}")
        y -= 20

        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(28, y, "Item")
        c.drawRightString(width - 116, y, "Qty")
        c.drawRightString(width - 72, y, "Rate")
        c.drawRightString(width - 28, y, "Amount")
        y -= 5
        c.line(28, y, width - 28, y)
        y -= 12

        c.setFont("Helvetica", 8.2)
        for item in items:
            if y < 80:
                c.showPage()
                c.setFillColor(purple)
                y = height - 42
                c.setFont("Helvetica", 8.2)
            name = str(item.get("item_name") or "")[:32]
            qty = item.get("quantity") or 0
            rate = float(item.get("unit_price") or 0)
            total = float(item.get("line_total") or 0)
            c.drawString(28, y, name)
            c.drawRightString(width - 116, y, str(qty))
            c.drawRightString(width - 72, y, f"{rate:.2f}")
            c.drawRightString(width - 28, y, f"{total:.2f}")
            y -= 14

        y -= 3
        c.line(28, y, width - 28, y)
        y -= 20
        c.setFont("Helvetica-Bold", 15)
        c.drawRightString(width - 28, y, f"TOTAL  Rs. {float(sale.get('total') or 0):.2f}")
        y -= 24
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(width / 2, y, settings.get("tagline") or "Crafting Happiness, One Sip at a Time.")
        c.save()
        buf.seek(0)

        response = HttpResponse(buf.getvalue(), content_type="application/pdf")
        filename = sale.get("bill_number") or "juice-craft-bill"
        response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
        return response
    except (SupabaseError, ValueError, TypeError) as exc:
        return HttpResponse(str(exc), status=400)
    except Exception:
        return HttpResponse("Unable to generate bill PDF", status=500)
