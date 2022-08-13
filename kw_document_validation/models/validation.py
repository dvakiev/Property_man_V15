import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class DocumentMixin(models.AbstractModel):
    _name = 'kw.document.validation.mixin'
    _description = 'Document Mixin'

    kw_document_validation_state = fields.Boolean(
        compute='_compute_kw_document_validation_state', )

    def write(self, vals):
        fs = {}
        for obj in self:
            docs = self.env['kw.document'].search([
                ('model', '=', self._name), ('res_id', '=', obj.id),
                ('state', 'in', ['confirmed', 'rejected']),
                ('type_id.is_validatable', '=', True), ])
            for doc in docs:
                for f in doc.type_id.field_ids:
                    if f.field_id.name not in fs.keys():
                        fs[f.field_id.name] = []
                    fs[f.field_id.name].append(doc.id)

        need_invalidation = any([x in vals for x in fs.keys()])

        if need_invalidation:
            val = vals.copy()

        result = super().write(vals)

        if not need_invalidation:
            return result

        for f in fs.keys():
            if f in val:
                self.env['kw.document'].browse(fs[f]).action_processed()

        return result

    def _compute_kw_document_validation_state(self):
        for obj in self:
            obj.kw_document_validation_state = \
                any([x.id for x in obj.kw_document_ids.filtered(
                    lambda x: x.state == 'process')])

    def action_confirm_requested(self):
        return self.kw_document_ids.action_confirm()

    def action_reject_requested(self):
        return self.kw_document_ids.action_reject
