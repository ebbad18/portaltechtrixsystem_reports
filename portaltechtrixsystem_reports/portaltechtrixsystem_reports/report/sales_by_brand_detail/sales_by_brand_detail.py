# my_custom_app.my_custom_app.report.daily_activity_report.daily_activity_report.py
import decimal
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
            "label": "<b>Brand</b>",
            "fieldname": "brand",
            "fieldtype": "Link",
            "options": "Brand",
            "width": 120
        },
        {
            "label": "<b>Date</b>",
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": "<b>Due Date</b>",
            "fieldname": "due_date",
            "fieldtype": "Date",
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
            "label": "<b>Trans. Type</b>",
            "fieldname": "trans_type",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>Produc/Service</b>",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": "<b>Customer</b>",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 120
        },
        {
            "label": "<b>Account Manager</b>",
            "fieldname": "user",
            "fieldtype": "Link",
            "options": "User",
            "width": 120
        },
        {
            "label": "<b>Description</b>",
            "fieldname": "description",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>Qty</b>",
            "fieldname": "qty",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>Unit</b>",
            "fieldname": "uom",
            "fieldtype": "Data",
            "width": 120
        },

        {
            "label": "<b>Rate</b>",
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "<b>Amount</b>",
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "<b>Cost</b>",
            "fieldname": "cost",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "<b>Gross Profit</b>",
            "fieldname": "gross_profit",
            "fieldtype": "Currency",
            "width": 120
        }

    ]
    return columns


def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions.append(f"inv.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append(f"inv.posting_date <= %(to_date)s")
    return " AND ".join(conditions)


def get_data(filters):
    data = []
    brand_query = """
            SELECT 
                item.brand,
                inv.posting_date,
                inv.due_date,
                inv.name AS trans_no,
                'Invoice' AS  trans_type,
                item.item_code,
                inv.customer,
                inv.owner AS user,
                item.description,
                item.qty,
                item.uom,
                item.rate,
                item.amount,
                ROUND(((SELECT valuation_rate FROM `tabStock Ledger Entry` WHERE item_code = item.item_code ORDER BY posting_date DESC, posting_time DESC LIMIT 1)*item.qty),4) AS cost,
                0 AS gross_profit
            FROM 
                `tabSales Invoice` AS inv, `tabSales Invoice Item` AS item
            WHERE 
                item.parent = inv.name 
                AND
                inv.is_return = 0 
                AND 
                inv.docstatus = 1
                AND
                {conditions} 
            ORDER BY 
                item.brand
    """.format(conditions=get_conditions(filters))

    brand_query_result = frappe.db.sql(brand_query, filters, as_dict=1)

    # TO REMOVE DUPLICATES
    keys_to_check = ['brand']
    seen_values = []

    for entry in brand_query_result:
        key_values = tuple(entry[key] for key in keys_to_check)

        if key_values in seen_values:
            for key in keys_to_check:
                entry[key] = None
        else:
            seen_values.append(key_values)

    # END
    # BRAND WISE SUMMARIZATION GROSS PROFIT CALCULATION
    # Initialize variables to track current brand and sums
    current_brand = None
    brand_sum = {"amount": 0, "cost": 0, "gross_profit": 0}

    # CALCULATE GROSS PROFIT
    for i, record in enumerate(brand_query_result):
        try:
            amount = Decimal(record.amount) if record.amount else 0
            cost = Decimal(record.cost) if record.cost else 0

            record.gross_profit = round(amount - cost, 4) if amount and cost else 0

            # Insert a row of sums before starting a new brand
            if current_brand != record.brand:
                if current_brand is not None:
                    data.append({
                        "brand": "",
                        "amount": brand_sum["amount"],
                        "cost": brand_sum["cost"],
                        "gross_profit": brand_sum["gross_profit"]
                    })
                current_brand = record.brand
                brand_sum = {"amount": 0, "cost": 0, "gross_profit": 0}

            # Update sums
            brand_sum["amount"] += amount
            brand_sum["cost"] += cost
            brand_sum["gross_profit"] += record.gross_profit

            data.append(record)
        except decimal.InvalidOperation as e:
            frappe.log_error(f"Invalid value encountered: {e}")
            continue

    # Add the last sum row
    if current_brand is not None:
        data.append({
            "brand": "",
            "amount": brand_sum["amount"],
            "cost": brand_sum["cost"],
            "gross_profit": brand_sum["gross_profit"]
        })
    # END

    # data.extend(brand_query_result)
    return data
