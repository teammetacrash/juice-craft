import os
import json
import hmac
from datetime import date, timedelta

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .supabase import SupabaseClient, SupabaseError


def health_view(request):
    return JsonResponse({"ok": True, "service": "juice-craft"})


def _logged_in(request):
    return bool(request.session.get("jc_admin"))


def _page(request, title, active):
    if not _logged_in(request):
        return redirect("login")
    return render(request, "core/app_astra.html", {"title": title, "active": active})


def login_view(request):
    if _logged_in(request):
        return redirect("dashboard")
    error = None
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        expected_user = os.environ.get("ADMIN_USERNAME", "admin")
        expected_pass = os.environ.get("ADMIN_PASSWORD", "")
        if expected_pass and hmac.compare_digest(username, expected_user) and hmac.compare_digest(password, expected_pass):
            request.session["jc_admin"] = True
            request.session.set_expiry(60 * 60 * 12)
            return redirect("dashboard")
        error = "Incorrect username or password."
    return render(request, "core/login_astra.html", {"error": error})


def logout_view(request):
    request.session.flush()
    return redirect("login")


def dashboard(request): return _page(request, "Dashboard", "dashboard")
def billing(request): return _page(request, "Billing", "billing")
def inventory(request): return _page(request, "Items & Inventory", "inventory")
def stock(request): return _page(request, "New Stock", "stock")
def prepared(request): return _page(request, "Prepared Items", "prepared")
def wastage(request): return _page(request, "Wastage", "wastage")
def expenses(request): return _page(request, "Expenses", "expenses")
def reports(request): return _page(request, "Reports", "reports")
def settings_page(request): return _page(request, "Settings", "settings")


def _body(request):
    if not request.body:
        return {}
    return json.loads(request.body.decode("utf-8"))


def _ok(data=None, status=200):
    return JsonResponse({"ok": True, "data": data}, status=status, safe=False)


def _err(message, status=400):
    return JsonResponse({"ok": False, "error": str(message)}, status=status)


@require_http_methods(["GET", "POST", "PATCH", "DELETE"])
def api_dispatch(request, action):
    if not _logged_in(request):
        return _err("Authentication required", 401)

    try:
        db = SupabaseClient()
        payload = _body(request) if request.method != "GET" else request.GET.dict()

        if action == "bootstrap" and request.method == "GET":
            return _ok({
                "brands": db.select("brands", order="name.asc"),
                "categories": db.select("product_categories", order="name.asc"),
                "prepared_categories": db.select("prepared_categories", order="name.asc"),
                "expense_categories": db.select("expense_categories", order="name.asc"),
                "settings": (db.select("shop_settings", filters={"id": "eq.1"}) or [{}])[0],
            })

        if action == "dashboard" and request.method == "GET":
            end = date.today()
            start = end - timedelta(days=6)
            metrics = db.rpc("dashboard_metrics", {"p_from": str(start), "p_to": str(end)})
            recent = db.select(
                "sales",
                select="id,bill_number,total,payment_method,status,created_at",
                order="created_at.desc",
                limit=7,
            )
            return _ok({"metrics": metrics, "recent": recent})

        if action == "products":
            if request.method == "GET":
                return _ok(db.select(
                    "products",
                    select="*,brands(name),product_categories(name)",
                    order="created_at.desc",
                ))

            if request.method == "POST":
                row = {
                    "name": (payload.get("name") or "").strip(),
                    "brand_id": int(payload["brand_id"]),
                    "category_id": int(payload["category_id"]),
                    "variant": (payload.get("variant") or "").strip(),
                    "purchase_price": payload.get("purchase_price") or 0,
                    "selling_price": payload.get("selling_price") or 0,
                    "stock_quantity": int(payload.get("stock_quantity") or 0),
                    "low_stock_level": int(payload.get("low_stock_level") or 5),
                    "is_active": bool(payload.get("is_active", True)),
                }
                if not row["name"]:
                    raise ValueError("Item name is required")
                created = db.insert("products", row)
                if row["stock_quantity"] > 0 and created:
                    db.insert("stock_transactions", {
                        "product_id": created[0]["id"],
                        "txn_type": "opening",
                        "quantity_delta": row["stock_quantity"],
                        "unit_cost": row["purchase_price"],
                        "note": "Opening stock",
                        "balance_after": row["stock_quantity"],
                    })
                return _ok(created, 201)

            if request.method == "PATCH":
                product_id = int(payload.pop("id"))
                allowed = {"name", "brand_id", "category_id", "variant", "purchase_price", "selling_price", "low_stock_level", "is_active"}
                row = {k: v for k, v in payload.items() if k in allowed}
                return _ok(db.update("products", row, {"id": f"eq.{product_id}"}))

        if action == "prepared":
            if request.method == "GET":
                return _ok(db.select(
                    "prepared_items",
                    select="*,prepared_categories(name)",
                    order="created_at.desc",
                ))

            if request.method == "POST":
                row = {
                    "name": (payload.get("name") or "").strip(),
                    "category_id": int(payload["category_id"]),
                    "selling_price": payload.get("selling_price") or 0,
                    "is_available": bool(payload.get("is_available", True)),
                    "notes": (payload.get("notes") or "").strip(),
                }
                if not row["name"]:
                    raise ValueError("Prepared item name is required")
                return _ok(db.insert("prepared_items", row), 201)

            if request.method == "PATCH":
                item_id = int(payload.pop("id"))
                allowed = {"name", "category_id", "selling_price", "is_available", "notes"}
                row = {k: v for k, v in payload.items() if k in allowed}
                return _ok(db.update("prepared_items", row, {"id": f"eq.{item_id}"}))

        if action == "stock" and request.method == "POST":
            return _ok(db.rpc("receive_stock", {
                "p_lines": payload.get("lines") or [],
                "p_date": payload.get("date") or str(date.today()),
                "p_notes": payload.get("notes") or "",
            }))

        if action == "wastage":
            if request.method == "GET":
                return _ok(db.select(
                    "wastages",
                    select="*,products(name,brands(name))",
                    order="created_at.desc",
                    limit=100,
                ))
            if request.method == "POST":
                return _ok(db.rpc("record_wastage", {
                    "p_product_id": int(payload["product_id"]),
                    "p_quantity": int(payload["quantity"]),
                    "p_reason": payload["reason"],
                    "p_date": payload.get("date") or str(date.today()),
                    "p_notes": payload.get("notes") or "",
                }))

        if action == "expenses":
            if request.method == "GET":
                return _ok(db.select(
                    "expenses",
                    select="*,expense_categories(name)",
                    order="expense_date.desc,created_at.desc",
                    limit=100,
                ))
            if request.method == "POST":
                row = {
                    "name": (payload.get("name") or "").strip(),
                    "category_id": int(payload["category_id"]),
                    "amount": payload.get("amount") or 0,
                    "expense_date": payload.get("date") or str(date.today()),
                    "notes": (payload.get("notes") or "").strip(),
                }
                if not row["name"]:
                    raise ValueError("Expense name is required")
                return _ok(db.insert("expenses", row), 201)

        if action == "billing_items" and request.method == "GET":
            products = db.select(
                "products",
                select="id,name,variant,selling_price,stock_quantity,is_active,brands(name),product_categories(name)",
                filters={"is_active": "eq.true"},
                order="name.asc",
            )
            prepared_items = db.select(
                "prepared_items",
                select="id,name,selling_price,is_available,prepared_categories(name)",
                filters={"is_available": "eq.true"},
                order="name.asc",
            )
            return _ok({"products": products, "prepared": prepared_items})

        if action == "complete_sale" and request.method == "POST":
            return _ok(db.rpc("complete_sale", {
                "p_items": payload.get("items") or [],
                "p_payment_method": payload.get("payment_method") or "Cash",
            }), 201)

        if action == "sale" and request.method == "GET":
            sale_id = int(payload["id"])
            sale = (db.select("sales", filters={"id": f"eq.{sale_id}"}) or [None])[0]
            if not sale:
                return _err("Bill not found", 404)
            items = db.select("sale_items", filters={"sale_id": f"eq.{sale_id}"}, order="id.asc")
            settings = (db.select("shop_settings", filters={"id": "eq.1"}) or [{}])[0]
            return _ok({"sale": sale, "items": items, "settings": settings})

        if action == "reports" and request.method == "GET":
            p_from = payload.get("from") or str(date.today())
            p_to = payload.get("to") or p_from
            metrics = db.rpc("report_metrics", {"p_from": p_from, "p_to": p_to})
            sales = db.select(
                "sales",
                select="id,bill_number,total,payment_method,status,created_at",
                filters={"and": f"(created_at.gte.{p_from}T00:00:00,created_at.lte.{p_to}T23:59:59)"},
                order="created_at.desc",
                limit=500,
            )
            return _ok({"metrics": metrics, "sales": sales})

        master_tables = {
            "brands": "brands",
            "categories": "product_categories",
            "prepared_categories": "prepared_categories",
            "expense_categories": "expense_categories",
        }
        if action in master_tables:
            table = master_tables[action]
            if request.method == "POST":
                name = (payload.get("name") or "").strip()
                if not name:
                    raise ValueError("Name is required")
                return _ok(db.insert(table, {"name": name}), 201)
            if request.method == "PATCH":
                item_id = int(payload["id"])
                name = (payload.get("name") or "").strip()
                if not name:
                    raise ValueError("Name is required")
                return _ok(db.update(table, {"name": name}, {"id": f"eq.{item_id}"}))

        if action == "settings" and request.method == "PATCH":
            allowed = {"shop_name", "phone", "address", "tagline", "invoice_prefix", "default_low_stock"}
            row = {k: v for k, v in payload.items() if k in allowed}
            return _ok(db.update("shop_settings", row, {"id": "eq.1"}))

        return _err("Unknown API action", 404)

    except (SupabaseError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return _err(exc, 400)
    except Exception:
        return _err("Unexpected server error", 500)
