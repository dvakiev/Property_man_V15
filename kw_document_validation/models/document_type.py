import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DocumentType(models.Model):
    _inherit = 'kw.document.type'

    is_validatable = fields.Boolean(
        default=False, string='Validatable', )
