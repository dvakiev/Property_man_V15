import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class DocumentType(models.Model):
    _inherit = 'kw.document.type'

    validations_ids = fields.Many2many(
        comodel_name='kw.dms.validation', )
    is_sequence_validation = fields.Boolean(
        default=False, )
    is_only_one_validator = fields.Boolean(
        default=False, )

    @api.onchange('is_sequence_validation')
    def _onchange_storage_id(self):
        if self.is_sequence_validation:
            self.is_only_one_validator = False
