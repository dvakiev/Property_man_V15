import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class DocumentType(models.Model):
    _inherit = 'kw.document.type'

    template_id = fields.Many2one(
        # domain=[('kw_document_is_doc_template', '=', True)],
        comodel_name='mail.template',)
    template_ids = fields.Many2many(
        comodel_name='mail.template', string='Template ro',
        compute='_compute_template_ids', )
    is_generated = fields.Boolean(
        related='kind_id.is_generated')

    @api.depends('model_id')
    def _compute_template_ids(self):
        for obj in self:
            if obj.model_id:
                template_ids = self.env['mail.template'].search([
                    # ('kw_document_is_doc_template', '=', True),
                    ('model_id', '=', obj.model_id.id)])
                obj.template_ids = [(6, 0, template_ids.ids)]
                if len(template_ids) == 1:
                    obj.template_id = template_ids[0].id
            else:
                obj.template_ids = [(5, 0)]
