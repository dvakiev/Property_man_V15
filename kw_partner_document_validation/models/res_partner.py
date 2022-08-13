import logging

from odoo import models

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = ['kw.document.validation.mixin', 'res.partner', ]
