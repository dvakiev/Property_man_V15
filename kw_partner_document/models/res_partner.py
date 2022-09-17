import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    kw_partner_document_ids = fields.One2many(
        comodel_name='kw.document', inverse_name='partner_id', )
