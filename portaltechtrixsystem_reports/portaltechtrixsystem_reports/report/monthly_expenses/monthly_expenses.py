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
            "label": "<b>Expense Head</b>",
            "fieldname": "account",
            "fieldtype": "Link",
            "options": "Account",
            "width": 300
        },
        {
            "label": "<b>Debit</b>",
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": "<b>Credit</b>",
            "fieldname": "credit",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": "<b>Balance</b>",
            "fieldname": "balance",
            "fieldtype": "Currency",
            "width": 200
        }

    ]
    return columns


def get_conditions(filters, doctype):
    conditions = []
    if filters.get("from_date"):
        conditions.append(f"`tab{doctype}`.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append(f"`tab{doctype}`.posting_date <= %(to_date)s")
    return " AND ".join(conditions)


def get_data(filters):
    data = []
    expenses = """
            SELECT
                `tabGL Entry`.account,
                SUM(`tabGL Entry`.debit) AS amount,
                SUM(`tabGL Entry`.credit) AS credit,
                SUM(`tabGL Entry`.debit) - SUM(`tabGL Entry`.credit) AS balance
            FROM
                `tabGL Entry`
            WHERE
                {conditions} 
                AND `tabGL Entry`.is_cancelled = 0
                AND `tabGL Entry`.debit > 0
                AND `tabGL Entry`.account IN (SELECT `name` FROM `tabAccount` WHERE `root_type` = 'Expense')
            GROUP BY `tabGL Entry`.account
    """.format(conditions=get_conditions(filters, "GL Entry"))

    expenses_result = frappe.db.sql(expenses, filters, as_dict=1)
    data.extend(expenses_result)
    return data
