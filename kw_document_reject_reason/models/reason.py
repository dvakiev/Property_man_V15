import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class DocumentRejectReason(models.Model):
    _name = 'kw.document.reject.reason'
    _description = 'Document reject reason'

    name = fields.Char(
        required=True, translate=True, )
    active = fields.Boolean(
        default=True, )
