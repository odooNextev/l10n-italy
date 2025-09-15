# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_edi_it_sender_partner = fields.Many2one(
        "res.partner",
        string="Third Party/Sender",
        help="Data of Third-Party Issuer Intermediary who emits the "
        "invoice on behalf of the seller/provider",
    )
