import logging

from odoo import models, fields, exceptions, _

_logger = logging.getLogger(__name__)


class DocumentConfirmationMixin(models.AbstractModel):
    _name = 'kw.document.confirmation.mixin'
    _description = 'Document confirmation Mixin'

    kw_confirmation_status_ids = fields.Many2many(
        comodel_name='kw.confirmation.status', string='Confirmation status',
        compute='_compute_kw_confirmation_status_ids', )

    def _compute_kw_confirmation_status_ids(self):
        for obj in self:
            docs = self.env['kw.confirmation.status'].search([
                ('model', '=', self._name), ('res_id', '=', obj.id)])
            if docs:
                obj.kw_confirmation_status_ids = [(6, 0, docs.ids)]
            else:
                obj.kw_confirmation_status_ids = False

    def get_kw_confirmation_status_value_by_code(self, code):
        self.ensure_one()
        doc_status = self.env['kw.document.confirmation.status'].search([
            ('code', '=', code)], limit=1)
        if not doc_status:
            raise exceptions.UserError(
                _('Wrong confirmation status "%s"') % code)
        status = self.env['kw.confirmation.status'].search([
            ('status_id', '=', doc_status.id), ('res_id', '=', self.id)
        ], limit=1)
        if not status:
            status = self.env['kw.confirmation.status'].create({
                'model': self._name, 'res_id': self.id,
                'status_id': doc_status.id, })
        status._compute_state()
        return status.state_stored or 'draft'

    def fill_kw_confirmation_status(self):
        model_id = self.env['ir.model'].sudo().search([
            ('model', '=', self._name)], limit=1)
        status = self.env['kw.document.confirmation.status'].search([
            ('model_id', '=', model_id.id), ])
        for obj in self:
            for code in [x.code for x in status]:
                obj.get_kw_confirmation_status_value_by_code(code)
