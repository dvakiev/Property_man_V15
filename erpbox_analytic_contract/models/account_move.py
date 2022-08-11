from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    contract_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Contract'
    )

    def action_register_payment(self):
        result = super(AccountMove, self).action_register_payment()
        result['context']['default_contract_id'] = self.contract_id.id
        return result

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        for rec in self:
            journal_item = rec.line_ids.filtered(lambda li: li.account_id.user_type_id.type in ['receivable', 'payable'])
            if journal_item:
                journal_item.update({
                    'contract_id': rec.contract_id.id
                })

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        result = super(AccountMove, self)._onchange_invoice_line_ids()
        journal_item = self.line_ids.filtered(lambda li: li.account_id.user_type_id.type in ['receivable', 'payable'])
        if journal_item:
            journal_item.update({
                'contract_id': self.contract_id.id
            })
        return result

    @api.model_create_multi
    def create(self, vals_list):
        moves = super(AccountMove, self).create(vals_list)
        for move in moves:
            if move.origin_id:
                move.onchange_contract_id()
        return moves


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    contract_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Contract'
    )
