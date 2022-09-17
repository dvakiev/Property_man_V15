import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    kw_document_is_doc_template = fields.Boolean(
        string='Is Doc template', )
    kw_document_header = fields.Html(
        string='Doc header', )
    kw_document_footer = fields.Html(
        string='Doc footer', )
    kw_document_paperformat_id = fields.Many2one(
        comodel_name='report.paperformat', string='Doc paper format',
        default=lambda self: self.env.user.company_id.paperformat_id)
    model_ids = fields.Many2many(
        comodel_name='ir.model', compute='_compute_model')

    def _compute_model(self):
        for obj in self:
            model = self.env['ir.model'].search([(
                'model', '=', 'res.partner')])
            obj.model_ids = [(6, 0, model.ids)]
