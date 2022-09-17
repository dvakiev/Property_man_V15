import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class DocumentType(models.Model):
    _name = 'kw.document.type'
    _description = 'Type of document'

    name = fields.Char(
        required=True, translate=True, )
    active = fields.Boolean(
        default=True, )
    code = fields.Char(
        required=True, )
    kind_id = fields.Many2one(
        comodel_name='kw.document.kind')
    model_id = fields.Many2one(
        comodel_name='ir.model', string='Model', required=True, index=True,
        ondelete='cascade', help='The model this document type belongs to',
        default=lambda x: x.env['ir.model'].sudo().search(
            [('model', '=', 'kw.document')]).id)
    field_ids = fields.One2many(
        comodel_name='kw.document.type.field', inverse_name='type_id', )
    is_uniq = fields.Boolean(
        default=False, )


class DocumentTypeField(models.Model):
    _name = 'kw.document.type.field'
    _description = 'Document fields'

    name = fields.Char(
        required=True, translate=True, )
    sequence = fields.Integer(
        default=1, )
    type_id = fields.Many2one(
        comodel_name='kw.document.type', required=True, )
    field_id = fields.Many2one(
        comodel_name='ir.model.fields', string='Field', ondelete='cascade',
        required=True, index=True, )
    field_ids = fields.Many2many(
        comodel_name='ir.model.fields', string='Field ro',
        compute='_compute_field_ids', )

    @api.depends('type_id')
    def _compute_field_ids(self):
        for obj in self:
            if obj.type_id:
                obj.field_ids = [(6, 0, obj.type_id.model_id.field_id.ids)]
            else:
                obj.field_ids = False
