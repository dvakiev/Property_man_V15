import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Document(models.Model):
    _inherit = 'kw.document'

    reject_reason_id = fields.Many2one(
        comodel_name='kw.document.reject.reason', )

    def action_processed(self):
        obj = self.filtered(lambda x: x.is_processable)
        obj.write({'reject_reason_id': False})
        return super().action_processed()

    def action_confirm(self):
        self.filtered(
            lambda x: x.state == 'process').write({'reject_reason_id': False})
        return super().action_confirm()

    def action_reject(self):
        obj = self.filtered(lambda x: x.state == 'process')
        if obj.filtered(lambda x: not x.reject_reason_id):
            action = self.env.ref(
                'kw_document_reject_reason.'
                'kw_document_reject_reason_kw_document_reject_reason_wizard_'
                'action_window').read()[0]
            action['context'] = {
                'default_wizard_document_ids': [self.id, ], }
            return action
        return super().action_reject()
