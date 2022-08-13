import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class DocumentRejectReasonWizard(models.TransientModel):
    _name = 'kw.document.reject.reason.wizard'
    _description = 'Document Reject Reason wizard'

    reject_reason_id = fields.Many2one(
        comodel_name='kw.document.reject.reason', )
    document_ids = fields.Many2many(
        comodel_name='kw.document', )

    @api.model
    def default_get(self, vals):
        res = super().default_get(vals)
        res['document_ids'] = [
            (6, 0, self.env.context.get('default_wizard_document_ids'))]
        return res

    def make_changes(self):
        self.ensure_one()
        self.document_ids.write({
            'reject_reason_id': self.reject_reason_id.id})
        self.document_ids.action_reject()
        return {'type': 'ir.actions.act_window_close'}
