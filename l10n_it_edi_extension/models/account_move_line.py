# Copyright 2025 Giuseppe Borruso - Dinamiche Aziendali srl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"

    l10n_it_edi_admin_ref = fields.Char(string="Admin. ref.", size=20, copy=False)
    l10n_it_edi_other_data_ids = fields.One2many(
        "l10n_it_edi.move.line.other.data",
        "move_line_id",
        string="Other Management Data",
        copy=True,
        help="Additional management data (AltriDatiGestionali) to be exported "
        "in the FatturaPA XML.",
    )
