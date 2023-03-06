from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    no_commission = fields.Boolean(string="Non considerare provvigioni")
