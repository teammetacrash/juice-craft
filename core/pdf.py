from django.http import HttpResponse
from django.shortcuts import redirect

from .supabase import SupabaseClient, SupabaseError


def _pdf_escape(value):
    return str(value or "").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_pdf(lines):
    stream = ["BT", "/F1 10 Tf", "36 555 Td"]
    first = True
    for text, size, bold in lines:
        if not first:
            stream.append("0 -16 Td")
        first = False
        stream.append(f"/{'F2' if bold else 'F1'} {size} Tf")
        stream.append(f"({_pdf_escape(text)}) Tj")
    stream.append("ET")
    content = "\n".join(stream).encode("latin-1", "replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 420 595] /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(out))
        out.extend(f"{i} 0 obj\n".encode())
        out.extend(obj)
        out.extend(b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects)+1}\n".encode())
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode())
    out.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    return bytes(out)


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

        lines = [
            (settings.get("shop_name") or "JUICE CRAFT", 18, True),
            (settings.get("address") or "", 9, False),
            (settings.get("phone") or "", 9, False),
            (f"Bill: {sale.get('bill_number','')}", 10, True),
            (f"Date: {str(sale.get('created_at','')).replace('T',' ')[:19]}", 9, False),
            (f"Payment: {sale.get('payment_method','')}", 9, False),
            ("", 7, False),
            ("Item                              Qty     Rate     Amount", 9, True),
        ]
        for item in items[:24]:
            name = str(item.get("item_name") or "")[:28]
            qty = int(item.get("quantity") or 0)
            rate = float(item.get("unit_price") or 0)
            total = float(item.get("line_total") or 0)
            lines.append((f"{name:<28} {qty:>3}   {rate:>7.2f}   {total:>8.2f}", 8, False))
        lines.extend([
            ("", 7, False),
            (f"TOTAL  Rs. {float(sale.get('total') or 0):.2f}", 14, True),
            (settings.get("tagline") or "Crafting Happiness, One Sip at a Time.", 9, True),
        ])

        response = HttpResponse(_build_pdf(lines), content_type="application/pdf")
        filename = sale.get("bill_number") or "juice-craft-bill"
        response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
        return response
    except (SupabaseError, ValueError, TypeError) as exc:
        return HttpResponse(str(exc), status=400)
    except Exception:
        return HttpResponse("Unable to generate bill PDF", status=500)
