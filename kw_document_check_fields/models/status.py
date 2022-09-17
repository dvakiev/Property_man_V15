import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class DocumentConfirmationStatus(models.Model):
    _inherit = 'kw.document.confirmation.status'

    field_ids = fields.Many2many(
        comodel_name='ir.model.fields', )
    field_ro_ids = fields.Many2many(
        comodel_name='ir.model.fields', string='Field ro',
        compute='_compute_by_model', )

    @api.depends('model_id')
    def _compute_by_model(self):
        for obj in self:
            if obj.model_id:
                obj.field_ro_ids = [(6, 0, obj.model_id.field_id.ids)]
            else:
                obj.field_ro_ids = False


class ConfirmationStatus(models.Model):
    _inherit = 'kw.confirmation.status'

    def compute_state(self):
        self.ensure_one()
        for f in self.status_id.field_ids:
            if not getattr(self.env[self.model].sudo().browse(
                    self.res_id), f.name):
                return 'draft'
        return super().compute_state()
