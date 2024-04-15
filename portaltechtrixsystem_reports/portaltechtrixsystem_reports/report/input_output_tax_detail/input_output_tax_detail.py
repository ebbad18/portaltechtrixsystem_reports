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
            "label": "<b>Trans. Date</b>",
            "fieldname": "trans_date",
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
            "label": "<b>Ref. No.</b>",
            "fieldname": "ref_no",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>Party</b>",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 120
        },
        {
            "label": "<b>NTN No.</b>",
            "fieldname": "tax_id",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>SRB(GST) NO.</b>",
            "fieldname": "srb_gst_no",
            "fieldtype": "Data",
            "width": 120
        },

        {
            "label": "<b>Qty</b>",
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": "<b>Amount w/o Tax</b>",
            "fieldname": "total",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "<b>Tax</b>",
            "fieldname": "tax",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "<b>Amount with Tax</b>",
            "fieldname": "grand_total",
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
    if filters.get("rate"):
        conditions.append(f"stc.account_head = %(rate)s")
    return " AND ".join(conditions)


def get_data(filters):
    data = []

    tax_query = """
            SELECT 
                inv.posting_date AS trans_date,
                inv.name AS trans_no,
                inv.po_no AS ref_no,
                inv.customer,
                inv.tax_id,
                inv.tax_id AS srb_gst_no,
                inv.total_qty AS qty,
                inv.total,
                COALESCE(SUM(stc.tax_amount), 0) AS tax,
                inv.grand_total
            FROM 
                `tabSales Invoice` AS inv
            JOIN 
                `tabSales Taxes and Charges` AS stc ON inv.name = stc.parent
            JOIN
                `tabAccount` AS acc ON stc.account_head = acc.name
            WHERE 
                inv.docstatus = 1
                AND ABS(inv.total_taxes_and_charges) > 0
                AND {conditions}
                AND acc.account_type = 'Tax'
            GROUP BY 
                inv.name
            ORDER BY 
                inv.posting_date
    """.format(conditions=get_conditions(filters))

    tax_query_result = frappe.db.sql(tax_query, filters, as_dict=1)
    # TO REMOVE DUPLICATES
    # keys_to_check = ['trans_no']
    # seen_values = []
    #
    # for entry in tax_query_result:
    #     key_values = tuple(entry[key] for key in keys_to_check)
    #
    #     if key_values in seen_values:
    #         for key in keys_to_check:
    #             entry[key] = None
    #     else:
    #         seen_values.append(key_values)

    # END
    data.extend(tax_query_result)
    return data
