from odoo import models, fields, _, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    analytic_account_contract_ids = fields.One2many(
        comodel_name='account.analytic.account',
        inverse_name='partner_id',
        string='Contracts',
    )

    analytic_account_contract_count = fields.Integer(
        string='Contracts count',
        compute="_compute_contract_count",
        store=True,
    )

    @api.depends('analytic_account_contract_ids')
    def _compute_contract_count(self):
        for rec in self:
            rec.analytic_account_contract_count = len(rec.analytic_account_contract_ids)

    def analytic_account_contracts_action(self):
        return {
            'name': _('Contracts'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.analytic.account',
            'domain': [('id', 'in', self.analytic_account_contract_ids.ids)],
        }