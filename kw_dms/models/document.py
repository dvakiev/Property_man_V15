import logging
import base64
import requests

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class KwDocument(models.Model):
    _name = 'kw.document'
    _inherit = ['mail.thread', 'mail.activity.mixin',
                'utm.mixin', 'kw.dms.security.mixin', 'portal.mixin']
    _description = 'Document'

    # pylint: disable=E8106
    def load_image_from_url(self, url):
        data = base64.b64encode(requests.get(url.strip()).content).replace(
            b'\n', b'')
        return data

    name = fields.Char(
        readonly=True, )
    active = fields.Boolean(
        default=True, track_visibility='always', )
    type_id = fields.Many2one(
        comodel_name='kw.document.type', required=True,
        track_visibility='always', )
    type_ids = fields.Many2many(
        comodel_name='kw.document.type', compute='_compute_type_ids',
        string='Types ro', )
    model = fields.Char(
        string='Model Name', default='kw.document')
    res_id = fields.Integer(
        string='Record ID', track_visibility='always', )
    # reference = fields.Char(
    #     compute='_compute_reference', store=False, )
    file = fields.Binary(
        track_visibility='always', attachment=True, )
    filename = fields.Char()

    url = fields.Char(
        compute='_compute_url', string='Direct link')
    preview = fields.Image(
        max_width=75, max_height=75, compute='_compute_preview',
        store=True, )
    page_ids = fields.One2many(
        comodel_name='kw.document.page', inverse_name='document_id', )
    # field_values = fields.Text(
    #     compute='_compute_field_values', )

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

    # @api.depends('model', 'res_id')
    # def _compute_reference(self):
    #     for obj in self:
    #         obj.reference = '%s,%s' % (obj.model, obj.res_id)

    @api.depends('file')
    def _compute_url(self):
        burl = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        for obj in self:
            # url = '/web/image/kw.document/{}/file/'.format(obj.id)
            # obj.url = os.path.join(burl, url)
            if not obj.file:
                obj.url = ''
                continue
            att = self.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'kw.document'),
                ('res_id', '=', obj.id),
                ('res_field', '=', 'file')], limit=1)
            token = att.generate_access_token()
            token = token[0] if token else ''
            obj.url = '{}/web/content/ir.attachment/{}/datas?access_token={}' \
                      ''.format(burl, att.id, token)

    @api.depends('model')
    def _compute_type_ids(self):
        for obj in self:
            if obj.model:
                type_ids = self.env['kw.document.type'].search([
                    ('model_id.model', '=', self.model)])
                obj.type_ids = [(6, 0, type_ids.ids)]
            else:
                obj.type_ids = [(5, 0)]

    # def _compute_field_values(self):
    #     for obj in self:
    #         val = []
    #         if obj.model:
    #             reference = self.env[obj.model].sudo().browse(obj.res_id)
    #             for f in obj.type_id.field_ids:
    #                 val.append('{}: {}'.format(
    #                     f.field_id.field_description,
    #                     getattr(reference, f.field_id.name)))
    #         obj.field_values = '\n'.join(val)

    @api.depends('file', 'page_ids')
    def _compute_preview(self):
        for obj in self:
            try:
                if obj.file:
                    # pages = convert_from_bytes(base64.b64decode(obj.file),
                    # dpi=100)
                    # img = io.BytesIO()
                    # pages[0].save(img, format='JPEG')
                    # img = img.getvalue()
                    # obj.preview = base64.b64encode(img)
                    pass
                elif obj.page_ids:
                    obj.preview = obj.page_ids[0].image_1920
                elif obj.file:
                    obj.preview = obj.file
                else:
                    obj.preview = False
            except Exception as e:
                _logger.info(e)
                obj.preview = False
        for obj in self:
            if not obj.preview:
                burl = self.env['ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                url = '{}/kw_dms/static/icons/file_unknown.svg'.format(burl)
                image = self.load_image_from_url(url)
                obj.write({'preview': image})

    @api.model
    def create(self, vals_list):
        type_id = self.env['kw.document.type'].browse(vals_list['type_id'])
        if vals_list.get('res_id'):
            reference = self.env[vals_list['model']].sudo().browse(
                vals_list['res_id'])
            vals_list['name'] = '{} {}'.format(
                reference.name_get()[0][1], type_id.name)
        else:
            vals_list['name'] = vals_list.get('filename') \
                or vals_list['model']
        obj = super().create(vals_list)
        if obj.type_id.is_automatic_sequence:
            code = 'kw.document'
            if obj.type_id.sequence_id:
                code = obj.type_id.sequence_id.code
            name = self.env['ir.sequence'].next_by_code(code)
            obj.write({'name': name})
        return obj

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

    # @api.model
    # def create(self, vals_list):
    #     obj = super().create(vals_list)
    #     if obj.type_id.is_automatic_sequence:
    #         code = 'kw.document'
    #         if obj.type_id.sequence_id:
    #             code = obj.type_id.sequence_id.code
    #         name = self.env['ir.sequence'].next_by_code(code)
    #         obj.write({'name': name})
    #     return obj

    # @api.depends('file', 'page_ids')
    # def _compute_preview(self):
    #     res = super()._compute_preview()
    #     for obj in self:
    #         if not obj.preview:
    #             burl = self.env['ir.config_parameter'].sudo().get_param(
    #                 'web.base.url')
    #             url = '{}/kw_dms/static/icons/file_unknown.svg'.format(burl)
    #             image = self.load_image_from_url(url)
    #             obj.write({'preview': image})
    #     return res


class DocumentPage(models.Model):
    _name = 'kw.document.page'
    _inherit = ['image.mixin', ]
    _description = 'Document page'
    _order = 'sequence'

    name = fields.Char()

    document_id = fields.Many2one(
        comodel_name='kw.document', )
    sequence = fields.Integer(
        default=1, )
    code = fields.Char()
    url = fields.Char(
        compute='_compute_url', string='Direct link')

    @api.depends('image_1920')
    def _compute_url(self):
        burl = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for obj in self:
            if not obj.image_1920:
                obj.url = ''
                continue
            att = self.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'kw.document.page'),
                ('res_id', '=', obj.id),
                ('res_field', '=', 'image_1920')], limit=1)
            token = att.generate_access_token()
            token = token[0] if token else ''
            obj.url = '{}/web/content/ir.attachment/{}/datas?access_token={}' \
                      ''.format(burl, att.id, token)


class DocumentMixin(models.AbstractModel):
    _name = 'kw.document.mixin'
    _description = 'Document Mixin'

    kw_document_ids = fields.Many2many(
        comodel_name='kw.document', compute='_compute_kw_document_ids',
        string='Documents', )

    def _compute_kw_document_ids(self):
        for obj in self:
            docs = self.env['kw.document'].search([
                ('model', '=', self._name), ('res_id', '=', obj.id)])
            if docs:
                obj.kw_document_ids = [(6, 0, docs.ids)]
            else:
                obj.kw_document_ids = False
