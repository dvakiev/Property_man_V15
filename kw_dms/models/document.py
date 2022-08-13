import logging
import base64
import requests

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class KwDocument(models.Model):
    _name = 'kw.document'
    _inherit = [
        'kw.document',
        'kw.dms.security.mixin', ]

    # pylint: disable=E8106
    def load_image_from_url(self, url):
        data = base64.b64encode(requests.get(url.strip()).content).replace(
            b'\n', b'')
        return data

    directory_id = fields.Many2one(
        comodel_name="kw.dms.directory",
        auto_join=True, index=True,
        string="Directory", ondelete="restrict", required=True,
        domain="['&', '|', ('permission_create', '=', True),"
               " ('permission_write', '=', True), "
               "('save_type', '!=', 'attachment')]", )
    category_id = fields.Many2one(
        comodel_name="kw.dms.category",
        string="Category", readonly=True,
        related='directory_id.category_id',)
    storage_id = fields.Many2one(
        comodel_name="kw.dms.storage", string="Storage",
        store=True, copy=True, readonly=True,
        related='directory_id.storage_id', )
    attachment_id = fields.Many2one(
        comodel_name='ir.attachment', readonly=True,)

    # Only for check_access_rule
    res_model = fields.Char(
        string="Linked attachments model", index=True, store=True, )

    @api.onchange("type_id")
    def _onchange_type_id(self):
        for record in self:
            record.directory_id = False
            if record.type_id:
                directory_id = record.type_id.directory_id
                if directory_id and directory_id.permission_create:
                    record.write({'directory_id': directory_id.id})

    def check_access_rule(self, operation):
        self.mapped("directory_id").check_access_rule(operation)
        return super().check_access_rule(operation)

    # pylint: disable=R1710
    def dms_download_document(self):
        url = ''
        if self.attachment_id:
            base_url = self.env['ir.config_parameter'].get_param(
                'web.base.url')
            download_url = '/web/content/' \
                + str(self.attachment_id.id) + '?download=true'
            url = str(base_url) + str(download_url)
        if self.url:
            url = '{}/web/content/{}?download=true'.format(
                self.url.split('/web/content/')[0],
                self.url.split('ir.attachment/')[1].split('/')[0], )
        if url:
            return {
                "type": "ir.actions.act_url",
                "url": url,
                "target": "new", }

    @api.model
    def create(self, vals_list):
        obj = super().create(vals_list)
        if obj.type_id.is_automatic_sequence:
            code = 'kw.document'
            if obj.type_id.sequence_id:
                code = obj.type_id.sequence_id.code
            name = self.env['ir.sequence'].next_by_code(code)
            obj.write({'name': name})
        return obj

    @api.depends('file', 'page_ids')
    def _compute_preview(self):
        res = super()._compute_preview()
        for obj in self:
            if not obj.preview:
                burl = self.env['ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                url = '{}/kw_dms/static/icons/file_unknown.svg'.format(burl)
                image = self.load_image_from_url(url)
                obj.write({'preview': image})
        return res
