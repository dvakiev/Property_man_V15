from odoo import models, api


class Property(models.Model):
    _inherit = "property.details"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for r in res:
            if r.partner_id:
                r.code = r.partner_id.security_post_id.sequence_id.next_by_id()
        return res