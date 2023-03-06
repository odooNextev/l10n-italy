# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, timedelta
from odoo import models, api, _


class SaleCommissionMakeSettle(models.TransientModel):
    _inherit = "sale.commission.make.settle"

    @api.multi
    def action_settle(self):
        """
        Esclude dal calcolo delle commissioni le fatture insolute, quelle con termini di
        pagamento Ri.Ba salvo buon fine se non sono passati almeno 5 giorni dalla data di 
        scadenza e quelle che hanno impostato manualmente il flag 'no_commission' 
        (per esempio se ormai è insoluta da anni).
        Il metodo predefinito non prevede hooks quindi è necessario riscriverlo completamente.
        """
        self.ensure_one()
        agent_line_obj = self.env['account.invoice.line.agent']
        settlement_obj = self.env['sale.commission.settlement']
        settlement_line_obj = self.env['sale.commission.settlement.line']
        settlement_ids = []
        if not self.agents:
            self.agents = self.env['res.partner'].search([('agent', '=', True)])
        date_to = self.date_to
        for agent in self.agents:
            date_to_agent = self._get_period_start(agent, date_to)
            # Get non settled invoices
            agent_lines = agent_line_obj.search([('invoice_date', '<=', date_to_agent),
                                                 ('agent', '=', agent.id), ('settled', '=', False)],
                                                order='invoice_date')
            # inizio modifica per Ri.Ba
            for line in agent_lines:
                # rimuove le righe delle fatture che hanno impostato il flag "no_commission"
                if line.invoice.no_commission:
                    agent_lines = agent_lines - line
                # filtro su Ri.Ba
                elif line.invoice.payment_term_id.riba:
                    # rimuove le righe se la ri.ba è insoluta o nel caso sia sbf non siano
                    # passati almeno 5 giorni dalla data di scadenza del pagamento per
                    # tenersi un margine e verificare che effettivamente sia stata pagata
                    if line.invoice.is_unsolved or line.invoice.date_due + timedelta(
                            days=+5) > date.today():
                        agent_lines = agent_lines - line
            # fine modifica per Ri.Ba
            for company in agent_lines.mapped('company_id'):
                agent_lines_company = agent_lines.filtered(
                    lambda r: r.object_id.company_id == company)
                if not agent_lines_company:
                    continue
                pos = 0
                sett_to = date(year=1900, month=1, day=1)
                while pos < len(agent_lines_company):
                    line = agent_lines_company[pos]
                    pos += 1
                    if line._skip_settlement():
                        continue
                    if line.invoice_date > sett_to:
                        sett_from = self._get_period_start(agent, line.invoice_date)
                        sett_to = self._get_next_period_date(
                            agent,
                            sett_from,
                        ) - timedelta(days=1)
                        settlement = self._get_settlement(agent, company, sett_from, sett_to)
                        if not settlement:
                            settlement = settlement_obj.create(
                                self._prepare_settlement_vals(agent, company, sett_from, sett_to))
                        settlement_ids.append(settlement.id)
                    settlement_line_obj.create({
                        'settlement': settlement.id,
                        'agent_line': [(6, 0, [line.id])],
                    })
        # go to results
        if len(settlement_ids):
            return {
                'name': _('Created Settlements'),
                'type': 'ir.actions.act_window',
                'views': [[False, 'list'], [False, 'form']],
                'res_model': 'sale.commission.settlement',
                'domain': [['id', 'in', settlement_ids]],
            }

        else:
            return {'type': 'ir.actions.act_window_close'}
