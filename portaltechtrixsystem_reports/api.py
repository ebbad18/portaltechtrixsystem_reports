import frappe


@frappe.whitelist()
def get_items():
    return frappe.get_all("Item", fields=["item_name", "item_group", "last_purchase_rate","image"])
