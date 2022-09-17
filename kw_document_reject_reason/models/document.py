import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Document(models.Model):
    _inherit = 'kw.document'

    reject_reason_id = fields.Many2one(
        comodel_name='kw.document.reject.reason', )
    is_need_reject_reason = fields.Boolean(
        related='type_id.is_need_reject_reason')

    def action_processed(self):
        obj = self.filtered(lambda x: x.is_processable)
        obj.write({'reject_reason_id': False})
        return super().action_processed()

    def action_confirm(self):
        self.filtered(
            lambda x: x.state in ['process', 'draft']).write(
            {'reject_reason_id': False})
        return super().action_confirm()

    def action_reject(self):
        obj = self.filtered(lambda x: x.state in ['process', 'draft'])
        if obj.is_need_reject_reason:
            action = self.env.ref(
                'kw_document_reject_reason.'
                'kw_document_reject_reason_kw_document_reject_reason_wizard_'
                'action_window').read()[0]
            action['context'] = {
                'default_wizard_document_ids': [self.id, ], }
            return action
        return super().action_reject()


class DocumentType(models.Model):
    _inherit = 'kw.document.type'

    is_need_reject_reason = fields.Boolean()
