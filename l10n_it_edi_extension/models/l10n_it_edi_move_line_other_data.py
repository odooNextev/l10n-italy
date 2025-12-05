# Copyright 2025 Nextev Srl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MoveLineOtherData(models.Model):
    """Model for storing AltriDatiGestionali (2.2.1.16) on invoice lines for export.

    This model stores additional management data that can be manually entered
    on account.move.line records and exported into the FatturaPA XML.
    """

    _name = "l10n_it_edi.move.line.other.data"
    _description = "Invoice Line Other Data for Export"
    _rec_name = "display_name"

    move_line_id = fields.Many2one(
        "account.move.line",
        string="Invoice Line",
        required=True,
        ondelete="cascade",
        index=True,
    )
    name = fields.Char(
        string="Data Type",
        required=True,
        help="TipoDato: Type of additional data (max 10 characters)",
    )
    text_ref = fields.Char(
        string="Text Reference",
        help="RiferimentoTesto: Text reference (max 60 characters)",
    )
    num_ref = fields.Float(
        string="Number Reference",
        digits=(16, 8),
        help="RiferimentoNumero: Numeric reference (up to 8 decimal places)",
    )
    date_ref = fields.Date(
        string="Date Reference",
        help="RiferimentoData: Date reference",
    )

    @api.depends("name", "text_ref", "num_ref", "date_ref")
    def _compute_display_name(self):
        for record in self:
            parts = [record.name]
            if record.text_ref:
                parts.append(record.text_ref)
            if record.num_ref:
                parts.append(str(record.num_ref))
            if record.date_ref:
                parts.append(str(record.date_ref))
            record.display_name = ": ".join(parts)

    @api.constrains("name")
    def _check_name_length(self):
        for record in self:
            if record.name and len(record.name) > 10:
                raise ValidationError(
                    _("Data Type (TipoDato) must not exceed 10 characters.")
                )

    @api.constrains("text_ref")
    def _check_text_ref_length(self):
        for record in self:
            if record.text_ref and len(record.text_ref) > 60:
                raise ValidationError(
                    _(
                        "Text Reference (RiferimentoTesto) "
                        "must not exceed 60 characters."
                    )
                )

    @api.constrains("name", "text_ref", "num_ref", "date_ref")
    def _check_at_least_one_ref(self):
        for record in self:
            has_text = bool(record.text_ref)
            # For Float fields, check if value was explicitly set (not default 0.0)
            has_num = bool(record.num_ref)
            has_date = bool(record.date_ref)
            if not has_text and not has_num and not has_date:
                raise ValidationError(
                    _(
                        "At least one of Text Reference, Number Reference, "
                        "or Date Reference must be provided."
                    )
                )
