# Copyright 2022 Sergio Corato
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import date, datetime, timedelta

from odoo.tests import Form
from odoo.tools.date_utils import relativedelta

from .delivery_note_common import StockDeliveryNoteCommon

_logger = logging.getLogger(__name__)


class StockDeliveryNoteSequence(StockDeliveryNoteCommon):
    def test_complete_invoicing_sequence(self):
        company_id = self.env.company.id
        ctx = dict(self.env.context)
        ctx["company_id"] = company_id
        self.env.context = ctx
        _logger.info(f"Context: {str(ctx)}")
        sequence = self.env["ir.sequence"].search(
            [
                ("code", "=", f"stock.delivery.note.ddt.c{company_id}"),
                ("company_id", "=", company_id),
            ]
        )
        current_year = datetime.today().year
        old_year = (datetime.today() - relativedelta(years=1)).year
        for sequence_year in [current_year, old_year]:
            sequence.write(
                {
                    "use_date_range": True,
                    "date_range_ids": [
                        (
                            0,
                            0,
                            {
                                "date_from": date.today().replace(
                                    month=1, day=1, year=sequence_year
                                ),
                                "date_to": date.today().replace(
                                    month=12, day=31, year=sequence_year
                                ),
                            },
                        )
                    ],
                }
            )
        date_range_sequence = sequence.date_range_ids.filtered(
            lambda x: x.date_from == date.today().replace(month=1, day=1, year=old_year)
        )
        date_range_sequence.write({"number_next_actual": 50})
        sale_order = self.create_sales_order(
            [
                self.desk_combination_line,
            ]
        )
        _logger.info(f"SO company: {sale_order.company_id}")
        self.assertEqual(len(sale_order.order_line), 1)
        sale_order.action_confirm()
        picking = sale_order.picking_ids
        _logger.info(f"picking company: {picking.company_id}")
        self.assertEqual(len(picking), 1)
        self.assertEqual(len(picking.move_lines), 1)

        picking.move_lines[0].quantity_done = 1
        result = picking.button_validate()
        self.assertTrue(result)

        dn_form = Form(
            self.env["stock.delivery.note.create.wizard"].with_context(
                active_ids=picking.ids,
            )
        )
        wizard = dn_form.save()
        wizard.confirm()
        delivery_note = picking.delivery_note_id
        _logger.info(f"delivery_note company: {delivery_note.company_id}")
        delivery_note.transport_datetime = datetime.now() + timedelta(days=1, hours=3)
        delivery_note.date = date.today().replace(year=old_year)
        delivery_note.action_confirm()
        _logger.info(f"delivery_note type name: {delivery_note.type_id.name}")
        _logger.info(f"delivery_note type company: {delivery_note.type_id.company_id}")
        self.assertEqual(delivery_note.type_id.sequence_id, sequence)
        self.assertEqual(
            delivery_note.name, sequence.prefix + "%%0%sd" % sequence.padding % 50
        )
