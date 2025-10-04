# Copyright (C) 2024 Code Factory
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    def action_print_count_sheet(self):
        self.ensure_one()
        return self.env.ref(
            "cf_inventory_count_sheet.action_report_inventory_count_sheet"
        ).report_action(self)
