# Copyright 2014-2019 Dinamiche Aziendali srl
# (http://www.dinamicheaziendali.it/)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# @author: Giuseppe Borruso <gborruso@dinamicheaziendali.it>
# Copyright (c) 2020, Link IT Europe Srl
# @author: Matteo Bilotta <mbilotta@linkeurope.it>
# Copyright (c) 2023, Nextev Srl
# @author: Nextev Srl <odoo@nextev.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models

DELIVERY_NOTE_TYPE_CODES = [
    ("incoming", "Incoming"),
    ("outgoing", "Outgoing"),
    ("internal", "Internal"),
]
DOMAIN_DELIVERY_NOTE_TYPE_CODES = [s[0] for s in DELIVERY_NOTE_TYPE_CODES]


class StockDeliveryNoteType(models.Model):
    _name = "stock.delivery.note.type"
    _description = "Delivery Note Type"
    _order = "sequence, name, id"

    active = fields.Boolean(default=True)
    sequence = fields.Integer(string="Sequence", index=True, default=10)
    name = fields.Char(string="Name", index=True, required=True, translate=True)
    print_prices = fields.Boolean(string="Show prices on printed DN", default=False)
    code = fields.Selection(
        DELIVERY_NOTE_TYPE_CODES,
        string="Type of Operation",
        required=True,
        default=DOMAIN_DELIVERY_NOTE_TYPE_CODES[1],
    )

    default_transport_condition_id = fields.Many2one(
        "stock.picking.transport.condition", string="Condition of transport"
    )
    default_goods_appearance_id = fields.Many2one(
        "stock.picking.goods.appearance", string="Appearance of goods"
    )
    default_transport_reason_id = fields.Many2one(
        "stock.picking.transport.reason", string="Reason of transport"
    )
    default_transport_method_id = fields.Many2one(
        "stock.picking.transport.method", string="Method of transport"
    )

    sequence_id = fields.Many2one("ir.sequence", string="Numeration", required=True)
    next_sequence_number = fields.Integer(related="sequence_id.number_next_actual")
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    note = fields.Html(string="Internal note")

    _sql_constraints = [
        (
            "name_uniq",
            "unique(name, company_id)",
            "This delivery note type already exists!",
        )
    ]

    def goto_sequence(self, **kwargs):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "res_model": "ir.sequence",
            "res_id": self.sequence_id.id,
            "views": [(False, "form")],
            "view_mode": "form",
            "target": "current",
            **kwargs,
        }

    def _check_existing_sequence_domain(self, code, company_id):
        """
        This method sets domain to check if sequence already exists
        """
        return [("code", "=", code), ("company_id", "=", company_id.id)]

    def _get_or_create_sequence(self, name, code, prefix, company_id):
        """
        This method gets sequence id or creates a new one if it doesn't already exist
        """
        sequence = self.env["ir.sequence"].search(
            self._check_existing_sequence_domain(code, company_id)
        )
        if sequence:
            return sequence.id
        else:
            return (
                self.env["ir.sequence"]
                .create(
                    {
                        "name": f"{company_id.name} {name}",
                        "code": code,
                        "prefix": prefix,
                        "implementation": "no_gap",
                        "padding": 5,
                        "company_id": company_id.id,
                    }
                )
                .id
            )

    def _set_dn_types_sequences(self, company_id):
        """
        This method returns the sequences need by DN types
        """
        res = {}
        res["stock.delivery.note.din"] = self._get_or_create_sequence(
            _("Incoming DdT sequence"),
            f"stock.delivery.note.din.c{company_id.id}",
            f"DIN/C{company_id.id}/",
            company_id,
        )
        res["stock.delivery.note.ddt"] = self._get_or_create_sequence(
            _("Outgoing DdT sequence"),
            f"stock.delivery.note.ddt.c{company_id.id}",
            f"DDT/C{company_id.id}/",
            company_id,
        )
        res["stock.delivery.note.int"] = self._get_or_create_sequence(
            _("Internal DdT sequence"),
            f"stock.delivery.note.int.c{company_id.id}",
            f"INT/C{company_id.id}/",
            company_id,
        )
        return res

    def _check_existing_dn_type_domain(self, name, company_id):
        """
        This method sets domain to check if dn type already exists
        """
        return [("name", "=", name), ("company_id", "=", company_id.id)]

    def _set_or_create_dn_types(
        self, name, sequence_id, print_prices, code, company_id
    ):
        """
        This method sets sequence on dn type or creates a new one if it doesn't
        already exist
        """
        dn_type = self.env["stock.delivery.note.type"].search(
            self._check_existing_dn_type_domain(name, company_id)
        )
        if dn_type:
            dn_type.sequence_id = sequence_id
        else:
            self.env["stock.delivery.note.type"].create(
                {
                    "name": name,
                    "sequence_id": sequence_id,
                    "print_prices": print_prices,
                    "code": code,
                    "company_id": company_id.id,
                }
            )

    def _prepare_dn_types_vals(self, company_id, sequences_dict):
        """
        This method sets values needed to search and create dn types
        """
        self._set_or_create_dn_types(
            _("Incoming"),
            sequences_dict["stock.delivery.note.din"],
            False,
            "incoming",
            company_id,
        )
        self._set_or_create_dn_types(
            _("Outgoing"),
            sequences_dict["stock.delivery.note.ddt"],
            False,
            "outgoing",
            company_id,
        )
        self._set_or_create_dn_types(
            _("Outgoing (with prices)"),
            sequences_dict["stock.delivery.note.ddt"],
            True,
            "outgoing",
            company_id,
        )
        self._set_or_create_dn_types(
            _("Internal transfer"),
            sequences_dict["stock.delivery.note.int"],
            False,
            "internal",
            company_id,
        )

    def create_dn_types(self, company_id):
        """
        This method creates DN types for the company in the input parameters.
        It first creates or get sequences, then it can link them to the DN type
        when creating them if they don't exist.
        """
        lang = company_id.partner_id.lang
        sequences_dict = self.with_context(lang=lang)._set_dn_types_sequences(
            company_id
        )
        self.with_context(lang=lang)._prepare_dn_types_vals(company_id, sequences_dict)
