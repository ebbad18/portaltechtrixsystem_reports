# my_custom_app.my_custom_app.report.daily_activity_report.daily_activity_report.py
from decimal import Decimal

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "label": "<b>Customer</b>",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 120
        },
        {
            "label": "<b>Trans. No.</b>",
            "fieldname": "trans_no",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 120
        },
        {
            "label": "<b>Trans. Date</b>",
            "fieldname": "trans_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": "<b>Ref. No.</b>",
            "fieldname": "ref_no",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>Due Date</b>",
            "fieldname": "due_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": "<b>Currency</b>",
            "fieldname": "currency",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>Invoice Amount</b>",
            "fieldname": "inv_amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "<b>Settled Amount</b>",
            "fieldname": "settled_amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "<b>Balance Amount</b>",
            "fieldname": "balance_amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "<b>Payment Days</b>",
            "fieldname": "payment_days",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>Status</b>",
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 140
        }


    ]
    return columns


def get_conditions(filters):
    conditions = []
    if filters.get("item_group"):
        conditions.append(f"AND item.item_group = %(item_group)s")
    if filters.get("import_file"):
        conditions.append(f"AND item.import_file = %(import_file)s")
    if filters.get("gsm"):
        conditions.append(f"AND item.gsm = %(gsm)s")
    return " ".join(conditions)


def get_data(filters):
    data = []
    conditions = get_conditions(filters)

    stock_balance_query = f"""
        SELECT 
            inv.customer,
            inv.name AS trans_no,
            inv.posting_date AS trans_date,
            pe.reference_no AS ref_no,
            inv.due_date,
            COALESCE(inv.currency, 0) AS currency,
            COALESCE(inv.grand_total,0) AS inv_amount,
            COALESCE(SUM(per.allocated_amount), 0) AS settled_amount,
            COALESCE((inv.grand_total - SUM(per.allocated_amount)), 0) AS balance_amount,
            COALESCE(DATEDIFF(MAX(pe.posting_date), inv.posting_date), 0) AS payment_days,
            CASE
                WHEN inv.grand_total = COALESCE(SUM(per.allocated_amount), 0) THEN 'Allocated'
                WHEN COALESCE(SUM(per.allocated_amount), 0) > 0 AND COALESCE(SUM(per.allocated_amount), 0) < inv.grand_total THEN 'Partially Allocated'
                WHEN COALESCE(SUM(per.allocated_amount), 0) < 1 THEN 'Not Allocated'
            END AS status
        FROM 
            `tabSales Invoice` AS inv
        LEFT JOIN 
            `tabPayment Entry Reference` AS per ON inv.name = per.reference_name
        LEFT JOIN 
            `tabPayment Entry` AS pe ON per.parent = pe.name AND pe.status != 'Cancelled'
        WHERE 
            inv.is_return = 0 AND inv.docstatus = 1
        GROUP BY 
            inv.name
        ORDER BY 
            inv.customer
    """


    stock_balance_result = frappe.db.sql(stock_balance_query, filters, as_dict=1)
    # TO REMOVE DUPLICATES
    keys_to_check = ['customer']
    seen_values = []

    for entry in stock_balance_result:
        key_values = tuple(entry[key] for key in keys_to_check)

        if key_values in seen_values:
            for key in keys_to_check:
                entry[key] = None
        else:
            seen_values.append(key_values)

    # END
    data.extend(stock_balance_result)
    return data
