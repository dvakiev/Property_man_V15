import logging

from odoo import fields, models, _

_logger = logging.getLogger(__name__)


class Document(models.Model):
    _inherit = 'kw.document'

    is_validatable = fields.Boolean(
        related='type_id.is_validatable', )
    state = fields.Selection(
        string='Status', readonly=True, copy=False, index=True,
        default='draft', track_visibility='always', selection=[
            ('draft', _('Draft')), ('process', _('Process')),
            ('confirmed', _('Confirmed')), ('rejected', _('Rejected')), ], )
    state_display = fields.Char(
        compute='_compute_state_display', )
    is_processable = fields.Boolean(
        compute='_compute_is_processable', )

    def action_processed(self):
        obj = self.filtered(lambda x: x.is_processable)
        obj.write({'state': 'process'})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload', }

    def action_confirm(self):
        self.filtered(
            lambda x: x.state == 'process').write({'state': 'confirmed'})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload', }

    def action_reject(self):
        self.filtered(
            lambda x: x.state == 'process').write({'state': 'rejected'})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload', }

    def check_processability(self):
        self.ensure_one()
        if not self.type_id.is_validatable or self.state == 'process':
            return False
        if self.state == 'draft':
            reference = self.env[self.model].sudo().browse(self.res_id)
            for f in self.type_id.field_ids:
                if not getattr(reference, f.field_id.name):
                    return False
            for page in self.page_ids:
                if page.kind_page_id:
                    if page.kind_page_id.is_required and not page.image_1920:
                        return False
                else:
                    if not page.image_1920:
                        return False
        return True

    def _compute_is_processable(self):
        for obj in self:
            obj.is_processable = obj.check_processability()

    def _compute_state_display(self):
        for obj in self:
            if obj.is_processable:
                obj.state_display = dict(
                    self._fields['state'].selection).get(obj.state)
            else:
                obj.state_display = ''


class DocumentPage(models.Model):
    _inherit = 'kw.document.page'

    def write(self, vals):
        need_invalidation = 'image_1920' in vals
        result = super().write(vals)
        if need_invalidation:
            for obj in self:
                if obj.document_id.state in ['draft', 'confirmed', 'rejected']:
                    obj.document_id.action_processed()
        return result
