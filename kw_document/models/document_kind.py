import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DocumentKind(models.Model):
    _name = 'kw.document.kind'
    _description = 'Kind of document'

    name = fields.Char(
        required=True, translate=True, )
    active = fields.Boolean(
        default=True, )
    is_multi_page = fields.Boolean(
        default=False, string='Many pages', )
    is_page_qty_fixed = fields.Boolean(
        default=False, string='Fixed page qty', )
    page_qty = fields.Integer(
        default=1, )
    min_page_qty = fields.Integer(
        default=1, )
    is_pages_predefined = fields.Boolean(
        default=False, string='Predefined pages', )
    page_ids = fields.One2many(
        comodel_name='kw.document.kind.page', inverse_name='kind_id', )
    is_pdf = fields.Boolean(
        default=False, string='Upload PDF file', )


class DocumentKindPage(models.Model):
    _name = 'kw.document.kind.page'
    _description = 'Predefined page'
    _order = 'sequence'

    name = fields.Char(
        required=True, translate=True, )
    sequence = fields.Integer(
        default=1, )
    kind_id = fields.Many2one(
        comodel_name='kw.document.kind', required=True, )
    code = fields.Char(
        required=True, )
