import logging
import base64
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Document(models.Model):
    _inherit = 'kw.document'

    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order', string='Purchase Order')

    def write(self, vals):
        for obj in self:
            if vals.get('purchase_order_id'):
                if obj.is_generated:
                    try:
                        file = obj.print_pdf()
                    except Exception as e:
                        _logger.info(e)
                    obj.file = base64.b64encode(file)
                    obj.filename = '{}.pdf'.format(obj.name)
        return super(Document, self).write(vals)

    @api.onchange("purchase_order_id")
    def compile_body_sale(self):
        for obj in self:
            if obj.purchase_order_id:
                template = self.env['sms.template']._render_template(
                    template_src=obj.body,
                    model=obj.model_name, res_ids=[obj.purchase_order_id.id])
                obj.body = template[obj.purchase_order_id.id]

    @api.model
    def create(self, vals_list):
        obj = super().create(vals_list)
        if obj.type_id and obj.is_generated and obj.purchase_order_id:
            try:
                obj.name = f'{obj.type_id.name}, {obj.purchase_order_id.name}'
                obj.body = obj.render_message(
                    obj.type_id.template_id.body_html,
                    obj.model_name,
                    obj.purchase_order_id.id)[obj.purchase_order_id.id]
                obj.header = obj.render_message(
                    obj.type_id.template_id.kw_document_header,
                    obj.model_name,
                    obj.purchase_order_id.id)[obj.purchase_order_id.id]
                obj.footer = obj.render_message(
                    obj.type_id.template_id.kw_document_footer,
                    obj.model_name,
                    obj.purchase_order_id.id)[obj.purchase_order_id.id]
            except Exception as e:
                _logger.info(e)
                obj.name = f'{obj.type_id.name}, {obj.purchase_order_id.name}'
                obj.body = obj.type_id.template_id.body_html
                obj.header = obj.type_id.template_id.kw_document_header
                obj.footer = obj.type_id.template_id.kw_document_footer
        return obj
