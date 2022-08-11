from odoo import models, fields, _
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _get_statement_line_vals(self, statement, receivable_account, amount, date=False, partner=False):
        res = super(PosSession, self)._get_statement_line_vals(statement, receivable_account, amount, date, partner)
        if not self.config_id.pos_account_id:
            raise UserError(
                _('You must define the default account number for the pos terminal! (Point of Sale -> Settings -> Accounting -> Account id)'))
        res['account_id'] = self.config_id.pos_account_id.id
        return res
