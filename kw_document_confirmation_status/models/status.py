import logging

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class DocumentConfirmationStatus(models.Model):
    _name = 'kw.document.confirmation.status'
    _description = 'Document confirmation status'

    name = fields.Char(
        required=True, )
    active = fields.Boolean(
        default=True, )
    code = fields.Char(
        required=True, )
    model_id = fields.Many2one(
        comodel_name='ir.model', string='Model', required=True, index=True,
        ondelete='cascade', help='The model this status type belongs to', )
    type_ids = fields.Many2many(
        comodel_name='kw.document.type', string='Document type',)
    type_ro_ids = fields.Many2many(
        comodel_name='kw.document.type', string='Document type ro',
        compute='_compute_by_model_id', )
    status_ids = fields.Many2many(
        comodel_name='kw.document.confirmation.status',
        relation='sub_status_rel', column1='status_parent',
        column2='sub_status', )
    status_ro_ids = fields.Many2many(
        comodel_name='kw.document.confirmation.status', string='Status ro',
        compute='_compute_by_model_id', relation='sub_status_ro_rel', )

    @api.depends('model_id')
    def _compute_by_model_id(self):
        for obj in self:
            if obj.model_id:
                obj.type_ro_ids = [
                    (6, 0, self.env['kw.document.type'].search([
                        ('model_id', '=', obj.model_id.id)]).ids)]
                obj.status_ro_ids = [
                    (6, 0, self.env['kw.document.confirmation.status'].search([
                        ('model_id', '=', obj.model_id.id)]).ids)]
            else:
                obj.type_ro_ids = False
                obj.status_ro_ids = False


class ConfirmationStatus(models.Model):
    _name = 'kw.confirmation.status'
    _description = 'Confirmation status'
    # _rec_name = 'state'

    model = fields.Char(
        string='Model Name', required=True, )
    res_id = fields.Integer(
        string='Record ID', required=True, )
    reference = fields.Char(
        compute='_compute_reference', store=False, )
    status_id = fields.Many2one(
        comodel_name='kw.document.confirmation.status', required=True, )
    state = fields.Selection(
        compute='_compute_state', selection=[
            ('draft', _('Draft')), ('process', _('Process')),
            ('confirmed', _('Confirmed')), ('rejected', _('Rejected')), ], )
    state_stored = fields.Selection(
        default='draft', selection=[
            ('draft', _('Draft')), ('process', _('Process')),
            ('confirmed', _('Confirmed')), ('rejected', _('Rejected')), ], )

    @api.depends('model', 'res_id')
    def _compute_reference(self):
        for obj in self:
            obj.reference = '%s,%s' % (obj.model, obj.res_id)

    def _compute_state(self):
        for obj in self:
            state = obj.compute_state()
            obj.state = state
            # if obj.status_id.name == 'innVerifyStatus':
            #     _logger.info(state)
            if obj.state_stored != state:
                obj.state_stored = state
                # pylint: disable=E8102
                # request._cr.commit()

    # pylint: disable=too-many-return-statements
    def compute_state(self):
        self.ensure_one()
        if self.status_id.type_ids:
            docs = self.env['kw.document'].sudo().search([
                ('type_id', 'in', self.status_id.type_ids.ids),
                ('res_id', '=', self.res_id)])
            # if self.status_id.name == 'innVerifyStatus':
            #     _logger.info(docs)
            #     _logger.info(docs.state)
            if not docs or any([x.state == 'draft' for x in docs]):
                return 'draft'
            if any([x.state == 'process' for x in docs]):
                return 'process'
            if any([x.state == 'rejected' for x in docs]):
                return 'rejected'
        if self.status_id.status_ids:
            status = self.env['kw.confirmation.status'].sudo().search([
                ('status_id', 'in', self.status_id.status_ids.ids),
                ('res_id', '=', self.res_id)])
            if not status or \
                    any([x.compute_state() == 'draft' for x in status]):
                return 'draft'
            if any([x.compute_state() == 'process' for x in status]):
                return 'process'
            if any([x.compute_state() == 'rejected' for x in status]):
                return 'rejected'
        return 'confirmed'
