from odoo.addons.account.wizard.pos_box import CashBox


class CashBoxOut(CashBox):
    _inherit = 'cash.box.out'

    def _calculate_values_for_statement_line(self, record):
        values = super(CashBoxOut, self)._calculate_values_for_statement_line(record)
        active_model = self.env.context.get('active_model', False)
        if active_model == 'account.bank.statement':
            amount = values.get('amount', False)
            if amount:
                values['payment_type'] = 'sale' if amount > 0 else 'purchase'
                values['payment_subtype'] = '5'
                values['account_id'] = record.journal_id.suspense_account_id.id
        return values
