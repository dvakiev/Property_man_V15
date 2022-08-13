import logging

from odoo import models, fields, _, exceptions, api

_logger = logging.getLogger(__name__)


class KwDocument(models.Model):
    _inherit = 'kw.document'

    vchasno_document_id = fields.Many2one(
        comodel_name='kw.vchasno.document', readonly=True, )
    vchasno_id = fields.Many2one(
        comodel_name='kw.vchasno.key')
    is_no_attach = fields.Boolean(
        default=False, readonly=True, )

    def send_vchasno(self):
        if not self.attachment_id and not self.file:
            raise exceptions.ValidationError(
                _('The document does not contain a file to send to Vchasno'))
        if self.vchasno_document_id:
            raise exceptions.ValidationError(
                _('The document has already been'
                  ' uploaded to the Vchasno system'))
        company_id = self.env.user.company_id
        key_id = self.env['kw.vchasno.key'].search(
            [('company_id', '=', company_id.id),
             ('user_id', '=', self.env.user.id), ], limit=1)
        attachment = self.attachment_id
        if attachment:
            vchasno_doc_id = self.env['kw.vchasno.document'].search([
                ('ir_attachment_id', '=', attachment.id)], limit=1)
            if vchasno_doc_id:
                self.write({
                    'vchasno_document_id': vchasno_doc_id.id,
                    'vchasno_id': vchasno_doc_id.vchasno_id.id, })
                return True
        if not attachment:
            attachment = self.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'kw.document'),
                ('res_id', '=', self.id),
                ('res_field', '=', 'file')], limit=1)
            self.is_no_attach = True
        doc_format = attachment.mimetype.split('/')[1]
        doc_filename = self.filename if self.filename else self.name
        doc_type = self.model
        number = self.name
        return {
            'name': _('Vchasno Document'),
            'type': 'ir.actions.act_window',
            'res_model': 'vchasno.download.document.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_is_dms': True,
                'default_filename': doc_filename,
                'default_dms_document_id': self.id,
                'default_is_no_attach': self.is_no_attach,
                'default_company_id': company_id.id,
                'default_vchasno_id': key_id.id,
                'default_format': doc_format,
                'default_ir_attachment_id':
                    self.attachment_id.id if self.attachment_id else None,
                'default_type': doc_type,
                'default_file': self.file if not self.attachment_id else None,
                'default_number': number, }}

    @api.model
    def create(self, vals_list):
        records = super().create(vals_list)
        for dms_doc in records:
            vchasno_doc_id = self.env['kw.vchasno.document'].search([
                ('ir_attachment_id', '=', dms_doc.attachment_id.id)
            ], limit=1)
            if vchasno_doc_id:
                dms_doc.write({
                    'vchasno_document_id': vchasno_doc_id.id,
                    'vchasno_id': vchasno_doc_id.vchasno_id.id, })
        return records
