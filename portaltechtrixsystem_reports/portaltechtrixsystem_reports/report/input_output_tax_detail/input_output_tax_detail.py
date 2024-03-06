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
            "fieldname": "company_tax_id",
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


def get_conditions(filters, doctype):
    conditions = []
    if filters.get("from_date"):
        conditions.append(f"{doctype}.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append(f"{doctype}.posting_date <= %(to_date)s")
    return " AND ".join(conditions)


def get_data(filters):
    data = []

    tax_query = """
            SELECT 
                inv.posting_date AS trans_date,
                inv.name AS trans_no,
                '' AS ref_no,
                inv.customer,
                inv.company_tax_id,
                inv.tax_id AS srb_gst_no,
                inv.total_qty AS qty,
                inv.total,
                inv.total_taxes_and_charges AS tax,
                inv.grand_total
            FROM 
                `tabSales Invoice` AS inv
            WHERE 
                {conditions} 
                AND 
                inv.docstatus = 1
            GROUP BY 
                inv.name
            ORDER BY 
                inv.posting_date
    """.format(conditions=get_conditions(filters, "inv"))

    tax_query_result = frappe.db.sql(tax_query, filters, as_dict=1)
    # TO REMOVE DUPLICATES
    # keys_to_check = ['trans_date']
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
