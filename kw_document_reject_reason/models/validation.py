import logging

from odoo import models

_logger = logging.getLogger(__name__)


class DocumentMixin(models.AbstractModel):
    _inherit = 'kw.document.validation.mixin'

    def action_reject_requested(self):
        self.ensure_one()
        obj = self.kw_document_ids.filtered(lambda x: x.state == 'process')
        if obj.filtered(lambda x: not x.reject_reason_id):
            action = self.env.ref(
                'kw_document_reject_reason.'
                'kw_document_reject_reason_kw_document_reject_reason_wizard_'
                'action_window').read()[0]
            action['context'] = {
                'default_wizard_document_ids': self.self.kw_document_ids.ids}
            return action
        return self.kw_document_ids.action_reject()
