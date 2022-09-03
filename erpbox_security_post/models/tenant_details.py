from odoo import models, fields, api


class Tenant(models.Model):
    _inherit = "tenant.details"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for r in res:
            r.code = r.property_id.code
            r.analytic_account_name = r.code
            r.analytic_account_id.name = r.code
        return res