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
                inv.sales_person AS user,
                item.description,
                item.qty,
                item.uom,
                item.rate,
                item.amount,
                ROUND((IFNULL(item.incoming_rate,0)*item.qty),4) AS cost,
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

    # Brand Wise Data Summarization and Appending Summary Row
    current_brand = None
    brand_data = []  # Collects data for each brand
    brand_sum = {"qty": 0, "amount": 0, "cost": 0, "gross_profit": 0}  # Track sums for each brand

    for record in brand_query_result:
        # Convert to Decimal and handle None values
        qty = Decimal(record.get('qty', 0) or 0)
        amount = Decimal(record.get('amount', 0) or 0)
        cost = Decimal(record.get('cost', 0) or 0)

        # Calculate gross profit for the current record and round to 4 decimal places
        record['gross_profit'] = round(amount - cost, 4)

        # Check if we're still processing the same brand
        if current_brand is None:
            # First record, set the current brand
            current_brand = record['brand']
        elif record['brand'] != current_brand:
            # We've hit a new brand, time to insert the summary for the previous brand
            brand_data.append({
                "description": "Total",
                "qty": f"{brand_sum['qty']:.4f}",
                "amount": f"{brand_sum['amount']:.4f}",
                "cost": f"{brand_sum['cost']:.4f}",
                "gross_profit": f"{brand_sum['gross_profit']:.4f}"
            })
            # Reset the sums for the new brand
            current_brand = record['brand']
            brand_sum = {"qty": 0, "amount": 0, "cost": 0, "gross_profit": 0}

        # Update the sums with the current record
        brand_sum["qty"] += qty
        brand_sum["amount"] += amount
        brand_sum["cost"] += cost
        brand_sum["gross_profit"] += record['gross_profit']

        # Append the current record to brand_data
        brand_data.append(record)

    # After looping through all records, insert a summary for the last brand
    if current_brand is not None:
        brand_data.append({
            "description": "Total",
            "qty": f"{brand_sum['qty']:.4f}",
            "amount": f"{brand_sum['amount']:.4f}",
            "cost": f"{brand_sum['cost']:.4f}",
            "gross_profit": f"{brand_sum['gross_profit']:.4f}"
        })

    # Append brand_data to data
    data.extend(brand_data)

    # END

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
    return data
