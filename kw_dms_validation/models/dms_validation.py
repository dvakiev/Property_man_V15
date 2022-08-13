import logging

from odoo import fields, models, exceptions, _

_logger = logging.getLogger(__name__)


class KwDmsValidation(models.Model):
    _name = "kw.dms.validation"
    _description = "kw.dms.validation"

    users_id = fields.Many2one(
        comodel_name='res.users', required=True,)
    sequence = fields.Integer(default=10, )


class KwDmsDocumentValidation(models.Model):
    _name = "kw.dms.document.validation"
    _description = "kw.dms.validation"

    users_id = fields.Many2one(
        comodel_name='res.users', required=True, )
    sequence = fields.Integer(default=10, )
    state = fields.Selection(
        [('validated', 'Validated'),
         ('rejected', 'Rejected'),
         ('pending', 'Pending'), ],
        default='pending', required=True, )
    datetime = fields.Datetime()
    is_validate = fields.Boolean(
        default=False, )
    document_id = fields.Many2one(
        comodel_name='kw.document',
        ondelete='cascade', required=True, )

    def check(self):
        if self.document_id.validations_document_ids.filtered(
                lambda x: x.state == 'rejected'):
            raise exceptions.ValidationError(
                _('This document has been rejected'))
        if self.is_validate or \
                self.document_id.state in ['rejected', 'confirmed']:
            raise exceptions.ValidationError(
                _('This document has already been validate'))
        if not self.users_id == self.env.user:
            raise exceptions.ValidationError(
                _('Wrong! This is a validation intended for another user'))

    def validate(self):
        self.check()
        if self.document_id.is_sequence_validation:
            val_ids = self.document_id.validations_document_ids.filtered(
                lambda x: x.state == 'pending')
            sequence = val_ids.filtered(lambda x: x.sequence < self.sequence)
            if sequence:
                raise exceptions.ValidationError(
                    _('Wait for other validates'))
        self.write({
            'datetime': fields.Datetime.now(),
            'is_validate': True,
            'state': 'validated', })
        self.document_id._compute_is_validate()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload', }

    def reject(self):
        self.check()
        if self.document_id.is_sequence_validation:
            val_ids = self.document_id.validations_document_ids.filtered(
                lambda x: x.state == 'pending')
            sequence = val_ids.filtered(lambda x: x.sequence < self.sequence)
            if sequence:
                raise exceptions.ValidationError(
                    _('Wait for other validates'))
        self.write({
            'datetime': fields.Datetime.now(),
            'is_validate': True,
            'state': 'rejected', })
        self.document_id._compute_is_validate()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload', }
