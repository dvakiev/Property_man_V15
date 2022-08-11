from odoo import models, fields, api, _
from odoo.exceptions import Warning


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    contract_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Contract'
    )
    payment_type = fields.Selection(
        selection=[('sale', 'Income'),
                   ('purchase', 'Outcome'),
                   ('internal', 'Internal')]
    )
    payment_subtype = fields.Selection(
        selection=[
            ('1', 'Payment from buyers/payers'),
            ('2', 'Return to buyers/payers'),
            ('3', 'Accountable person'),
            ('4', 'Salary'),
            ('5', 'Others'),
        ]
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
    )
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        domain=[('is_contract', '=', False)]
    )
    analytic_tag_ids = fields.Many2many(
        comodel_name='account.analytic.tag',
        string='Analytic tags'
    )

    @api.onchange('payment_type', 'payment_subtype', 'partner_id')
    def onchange_payment_type(self):
        def return_values_third():
            account = self.env['account.account'].search([('code', '=', '3721')])
            self.account_id = account.id
            partners = self.env['res.users'].search([]).mapped('partner_id')
            return {'domain': {'partner_id': [('id', 'in', partners.ids)]}}

        def return_values_forth():
            account = self.env['account.account'].search([('code', '=', '661')])
            self.account_id = account.id
            partners = self.env['res.users'].search([]).mapped('partner_id')
            return {'domain': {'partner_id': [('id', 'in', partners.ids)]}}

        if self.payment_type:
            if self.payment_type == 'internal':
                self.account_id = self.company_id.transfer_account_id.id
                return {}
            if self.statement_id.journal_type in ['cash', 'bank']:
                if self.payment_type in ['purchase', 'sale'] and self.payment_subtype == '3':
                    return return_values_third()
                if self.payment_type in ['purchase', 'sale'] and self.payment_subtype == '4':
                    return return_values_forth()
                if self.payment_type == 'purchase':
                    if self.payment_subtype == '1':
                        self.account_id = self.partner_id.property_account_payable_id.id
                    elif self.payment_subtype == '2':  # Return to buyers/payers
                        self.account_id = self.partner_id.property_account_receivable_id.id
                        return {'domain': {'contract_id': [('is_contract', '=', True), ('partner_id', '=', self.partner_id.id), ('contract_type', '=', 'sale')]}}
                    return {}
                if self.payment_type == 'sale':
                    if self.payment_subtype == '1':
                        self.account_id = self.partner_id.property_account_receivable_id.id
                    elif self.payment_subtype == '2':  # Return to buyers/payers
                        self.account_id = self.partner_id.property_account_payable_id.id
                        return {'domain': {'contract_id': [('is_contract', '=', True), ('partner_id', '=', self.partner_id.id), ('contract_type', '=', 'purchase')]}}
                    return {}
                if self.payment_subtype == '5':
                    self.account_id = False
                    return {}

    @api.model
    def _prepare_move_line_default_vals(self, counterpart_account_id=None):
        def update_line(move_line):
            move_line.update({
                # 'contract_id': self.contract_id.id,
                'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
                'analytic_account_id': self.analytic_account_id.id,
                'account_id': self.account_id.id
            })
            if move_line['account_id'] != self.journal_id.default_account_id.id:
                move_line.update({
                    'contract_id': self.contract_id.id,
                })
        result = super(AccountBankStatementLine, self)._prepare_move_line_default_vals(counterpart_account_id)
        for line in result:
            if line['debit'] > 0 and self.amount < 0:
                update_line(line)
            if line['credit'] > 0 and self.amount > 0:
                update_line(line)
        return result

    @api.model
    def _prepare_liquidity_move_line_vals(self):
        result = super(AccountBankStatementLine, self)._prepare_liquidity_move_line_vals()
        if result['account_id'] != self.journal_id.default_account_id.id:
            result.update({
                'contract_id': self.contract_id.id,
            })
        return result

    @api.model_create_multi
    def create(self, vals_list):
        result = super(AccountBankStatementLine, self).create(vals_list)
        for rec in result:
            rec.check_amount_sign()
        return result

    def write(self, vals):
        result = super(AccountBankStatementLine, self).write(vals)
        if 'amount' in vals:
            for rec in self:
                rec.check_amount_sign()
        return result

    def check_amount_sign(self):
        if self.payment_type == 'purchase' and self.amount > 0:
            raise Warning(_('Line "%s" amount must be less than 0.0', self.payment_ref))
        if self.payment_type == 'sale' and self.amount < 0:
            raise Warning(_('Line "%s" amount must be greater than 0.0', self.payment_ref))

    def _prepare_move_line_for_currency(self, aml_dict, date):
        result = super(AccountBankStatementLine, self)._prepare_move_line_for_currency(aml_dict=aml_dict, date=date)
        if self.contract_id:
            aml_dict.update({
                'contract_id': self.contract_id.id,
            })
        return result
