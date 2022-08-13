import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DocumentKind(models.Model):
    _inherit = 'kw.document.kind'

    is_generated = fields.Boolean(
        default=False, )
