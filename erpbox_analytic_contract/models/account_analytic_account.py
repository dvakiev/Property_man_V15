from odoo import models, fields, api, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    is_contract = fields.Boolean(
        string='Contract',
        help='Is contract'
    )
    contract_type = fields.Selection(
        selection=[('sale', 'With customer'), ('purchase', 'With purchase')]
    )
    contract_date_start = fields.Date(
        string='Contract date start'
    )
    contract_date_end = fields.Date(
        string='Contract date end'
    )
    is_indefinite = fields.Boolean(
        string='Indefinite'
    )
    contract_sign_date = fields.Date(
        string='Contract sign date'
    )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term'
    )
    parent_contract_id = fields.Many2one(
        comodel_name='account.analytic.line',
        string='Parent contract'
    )
    contract_subtype = fields.Selection(
        selection=[('main', 'Main'), ('additional', 'Additional')],
        default='main'
    )
    contract_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Contract currency',
        default=lambda self: self.env.user.company_id.currency_id
    )
    account_move_line_ids = fields.One2many(
        comodel_name='account.move.line',
        inverse_name='contract_id',
        string='Account entries',
    )
    account_move_line_count = fields.Integer(
        string='Account entries count',
        compute="_compute_account_move_line_count",
        store=True,
    )
    account_move_ids = fields.One2many(
        comodel_name='account.move',
        inverse_name='contract_id',
        string='Account Moves',
    )
    account_move_count = fields.Integer(
        string='Account Moves count',
        compute="_compute_account_move_count",
        store=True,
    )
    account_bank_statement_line_ids = fields.One2many(
        comodel_name='account.bank.statement.line',
        inverse_name='contract_id',
        string='Bank Operations'
    )
    account_bank_statement_line_count = fields.Integer(
        string='Bank Operations count',
        compute="_compute_account_bank_statement_line_count",
        store=True,
    )

    @api.depends('account_bank_statement_line_ids')
    def _compute_account_bank_statement_line_count(self):
        for rec in self:
            rec.account_bank_statement_line_count = len(rec.account_bank_statement_line_ids)

    @api.depends('account_move_line_ids')
    def _compute_account_move_line_count(self):
        for rec in self:
            rec.account_move_line_count = len(rec.account_move_line_ids)

    @api.depends('account_move_ids')
    def _compute_account_move_count(self):
        for rec in self:
            rec.account_move_count = len(rec.account_move_ids)

    def action_open_account_bank_statement_line(self):
        return {
            'name': _('Bank operations'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.bank.statement.line',
            'domain': [('contract_id', '=', self.id)],
            'context': {'default_contract_id': self.id}
        }

    def action_open_account_move(self):
        return {
            'name': _('Account moves'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('contract_id', '=', self.id)],
            'context': {'default_contract_id': self.id}
        }

    def action_open_account_move_line(self):
        return {
            'name': _('Account entries'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'domain': [('contract_id', '=', self.id)],
            'context': {'default_contract_id': self.id}
        }
