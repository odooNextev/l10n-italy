# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models

from odoo.addons.l10n_it_edi.models.account_move import get_text


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_it_edi_intermediary_id = fields.Many2one("res.partner", string="Intermediary")

    def _l10n_it_edi_import_invoice(self, invoice, data, is_new):
        res = super()._l10n_it_edi_import_invoice(invoice, data, is_new)
        Partner = self.env["res.partner"]
        tree = data["xml_tree"]
        intermediary = tree.xpath("//TerzoIntermediarioOSoggettoEmittente")[0]
        vat = get_text(intermediary, ".//IdCodice")
        intermediary_id = Partner.search([("vat", "ilike", vat)], limit=1)
        if intermediary_id:
            invoice.l10n_it_edi_intermediary_id = intermediary_id
        return res
