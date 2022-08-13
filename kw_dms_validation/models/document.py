import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class KwDocument(models.Model):
    _inherit = 'kw.document'

    validations_ids = fields.Many2many(
        comodel_name='kw.dms.validation',
        related='type_id.validations_ids', )
    is_sequence_validation = fields.Boolean(
        default=False, readonly=True, )
    validations_document_ids = fields.One2many(
        comodel_name='kw.dms.document.validation',
        inverse_name="document_id", )
    is_validate = fields.Boolean(
        default=False,
        compute="_compute_is_validate", )
    is_only_one_validator = fields.Boolean(
        default=False, readonly=True, )

    @api.model
    def create(self, vals_list):
        obj = super().create(vals_list)
        if obj.type_id.validations_ids:
            obj.is_sequence_validation = \
                obj.type_id.is_sequence_validation
            obj.is_only_one_validator = \
                obj.type_id.is_only_one_validator
            for validation in obj.validations_ids:
                self.env['kw.dms.document.validation'].sudo().create({
                    'users_id': validation.users_id.id,
                    'sequence': validation.sequence,
                    'document_id': obj.id, })
        return obj

    # pylint: disable=R1710
    def _compute_is_validate(self):
        self.is_validate = False
        rejected = self.validations_document_ids.filtered(
            lambda x: x.state == 'rejected')
        if rejected:
            self.write({'state': 'rejected'})
            self.is_validate = True
            return True
        validated = self.validations_document_ids.filtered(
            lambda x: x.state == 'validated')
        pending = self.validations_document_ids.filtered(
            lambda x: x.state == 'pending')
        if self.is_only_one_validator:
            if validated:
                self.write({'state': 'confirmed'})
                self.is_validate = True
                return True
        else:
            if not validated and pending:
                self.write({'state': 'draft'})
            if validated and pending:
                self.write({'state': 'process'})
            if not pending and validated:
                self.write({'state': 'confirmed'})
                self.is_validate = True
            return True
