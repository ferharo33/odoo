# Copyright (C) 2024 Code Factory
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "CF Inventory Count Sheet",
    "summary": "Print inventory count sheet from stock adjustments",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Code Factory",
    "website": "https://www.codefactory.cr/",
    "depends": ["stock", "stock_inventory"],
    "category": "Inventory/Inventory",
    "data": [
        "report/inventory_count_sheet_report.xml",
        "report/inventory_count_sheet_templates.xml",
        "views/stock_inventory_views.xml",
    ],
    "installable": True,
    "application": False,
}
