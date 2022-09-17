import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Document(models.Model):
    _inherit = 'kw.document'

    partner_id = fields.Many2one(
        comodel_name='res.partner', )
