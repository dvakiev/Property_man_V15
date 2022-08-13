# import base64
# import io
import logging

from odoo import fields, models, api, exceptions, _

_logger = logging.getLogger(__name__)

# try:
#     from pdf2image import convert_from_bytes
# except ImportError:
#     _logger.warning("Please, install *pdf2image* package")


class Document(models.Model):
    _name = 'kw.document'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin',
                'utm.mixin', ]
    _description = 'Document'

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
        string='Model Name', )
    res_id = fields.Integer(
        string='Record ID', track_visibility='always', )
    reference = fields.Char(
        compute='_compute_reference', store=False, )
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
    field_values = fields.Text(
        compute='_compute_field_values', )
    is_pdf = fields.Boolean(
        string='Upload PDF file', compute='_compute_is_pdf', )

    @api.depends('model', 'res_id')
    def _compute_reference(self):
        for obj in self:
            obj.reference = '%s,%s' % (obj.model, obj.res_id)

    @api.depends('type_id')
    def _compute_is_pdf(self):
        for obj in self:
            obj.is_pdf = obj.type_id.kind_id.is_pdf

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

    def _compute_field_values(self):
        for obj in self:
            reference = self.env[obj.model].sudo().browse(obj.res_id)
            val = []
            for f in obj.type_id.field_ids:
                val.append('{}: {}'.format(
                    f.field_id.field_description,
                    getattr(reference, f.field_id.name)))
            obj.field_values = '\n'.join(val)

    @api.depends('file', 'page_ids')
    def _compute_preview(self):
        for obj in self:
            try:
                if obj.is_pdf and obj.file:
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

    @api.constrains('model', 'res_id', 'type_id')
    def _constrains_is_uniq(self):
        for obj in self:
            if not obj.type_id.is_uniq:
                continue
            doc = self.search(
                [('id', '!=', obj.id),
                 ('model', '=', obj.model),
                 ('res_id', '=', obj.res_id),
                 ('type_id', '=', obj.type_id.id), ])
            if doc:
                raise exceptions.UserError(
                    _('Document of type "%s" must be unique'
                      '') % obj.type_id.name)

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
        if type_id.kind_id.is_pages_predefined:
            for p in type_id.kind_id.page_ids:
                self.env['kw.document.page'].create({
                    'name': '{} [{}]'.format(vals_list['name'], p.code),
                    'document_id': obj.id,
                    'sequence': p.sequence,
                    'kind_page_id': p.id,
                    'code': p.code, })
        return obj


class DocumentPage(models.Model):
    _name = 'kw.document.page'
    _inherit = ['image.mixin', ]
    _description = 'Document page'
    _order = 'sequence'

    name = fields.Char()

    document_id = fields.Many2one(
        comodel_name='kw.document', )
    kind_page_id = fields.Many2one(
        comodel_name='kw.document.kind.page', )
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
