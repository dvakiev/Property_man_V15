import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class Document(models.Model):
    _inherit = 'kw.document'

    partner_id = fields.Many2one(
        comodel_name='res.partner', )

    @api.model
    def create(self, vals_list):
        if vals_list.get('model') == 'res.partner':
            vals_list['partner_id'] = vals_list.get('res_id')
        return super().create(vals_list)
