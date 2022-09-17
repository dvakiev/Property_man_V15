import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DocumentKind(models.Model):
    _name = 'kw.document.kind'
    _description = 'Kind of document'

    name = fields.Char(
        required=True, translate=True, )
    is_generated = fields.Boolean(
        default=False, )
