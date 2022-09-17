import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class DocumentType(models.Model):
    _name = 'kw.document.type'
    _description = 'Type of document'

    name = fields.Char(
        required=True, translate=True, )
    active = fields.Boolean(
        default=True, )
    # code = fields.Char(
    #     required=True, )
    model_id = fields.Many2one(
        comodel_name='ir.model', string='Model', required=True, index=True,
        ondelete='cascade', help='The model this document type belongs to',
        default=lambda x: x.env['ir.model'].sudo().search(
            [('model', '=', 'kw.document')]).id)
    is_for_attach_dir = fields.Boolean(
        defaul=False, readonly=True, string='For Attachment Directory')
    is_automatic_sequence = fields.Boolean(
        default=False)
    directory_id = fields.Many2one(
        comodel_name="kw.dms.directory",
        domain="[('save_type', '!=', 'attachment')]",
        string="Directory", )
    sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
        domain="[('code', '=', 'kw.document')]", )

    @api.onchange("is_automatic_sequence")
    def _onchange_is_automatic_sequence(self):
        for record in self:
            seq_id = self.env['ir.sequence'].search([
                ('code', '=', 'kw.document')])
            if seq_id:
                record.write({'sequence_id': seq_id.id})
