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

    def compute_rent(self):
        self.ensure_one()
        super().compute_rent(1)
        rent_details = self.rent_details_ids.filtered(
            lambda r: r.invoice_id)
        security_post_name = self.partner_id.security_post_id.display_name
        for rd in rent_details:
            lines = rd.invoice_id.invoice_line_ids.filtered(
                lambda r: not r.analytic_tag_ids)
            lines.analytic_tag_ids = self.env["account.analytic.tag"].sudo().search([
                ("name", "=", security_post_name)]).ids
