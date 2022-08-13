import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DocumentKindPage(models.Model):
    _inherit = 'kw.document.kind.page'

    is_required = fields.Boolean(
        default=True, )
