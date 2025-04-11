from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_l10n_it_edi_doi_use(self):
        purchase_types = self.env["account.move"].get_purchase_types()
        purchase_move_ids = self.filtered(lambda m: m.move_type in purchase_types)
        other_move_ids = self - purchase_move_ids
        super(AccountMove, other_move_ids)._compute_l10n_it_edi_doi_use()
        for move in purchase_move_ids:
            move.l10n_it_edi_doi_use = (
                move.l10n_it_edi_doi_id or move.country_code == "IT"
            )
        return  # W8110

    def _compute_l10n_it_edi_doi_amount(self):
        for move in self:
            if move.l10n_it_edi_doi_id.type == "out":
                return super()._compute_l10n_it_edi_doi_amount()
            tax = move.company_id.l10n_it_edi_doi_bill_tax_id
            if not tax or not move.l10n_it_edi_doi_id:
                move.l10n_it_edi_doi_amount = 0
                continue
            declaration_lines = move.invoice_line_ids.filtered(
                # The declaration tax cannot be used with other taxes on a single line
                # (checked in `_post`)
                lambda line: line.tax_ids.ids == tax.ids
            )
            move.l10n_it_edi_doi_amount = sum(declaration_lines.mapped("price_total"))

    def _compute_l10n_it_edi_doi_id(self):
        for move in self:
            doi_type = (
                "out" if move.move_type in ("out_invoice", "out_refund") else "in"
            )
            super(AccountMove, move.with_context(doi_type=doi_type))._compute_l10n_it_edi_doi_id()
