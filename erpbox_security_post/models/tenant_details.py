from odoo import models, fields, api


class Tenant(models.Model):
    _inherit = "tenant.details"

    security_post_id = fields.Many2one(
        comodel_name="erpbox.security.post",
        string="Security Post №",
        required=False,
    )
    security_post_ids = fields.Many2many(
        comodel_name="erpbox.security.post",
        compute='_compute_security_post_onchange'
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for r in res:
            r.code = r.property_id.code
            r.analytic_account_name = r.code
            r.analytic_account_id.name = r.code
        return res

    @api.depends('partner_id')
    def _compute_security_post_onchange(self):
        for rec in self:
            if rec.partner_id:
                rec.write(
                    {'security_post_ids': [
                        (6, 0, rec.partner_id.security_post_ids.ids)]}
                )
            else:
                rec.write(
                    {'security_post_ids': False}
                )

    def compute_rent(self):
        self.ensure_one()
        super().compute_rent(1)
        rent_details = self.rent_details_ids.filtered(
            lambda r: r.invoice_id)
        security_post_name = self.partner_id.security_post_id.display_name
        for rd in rent_details:
            lines = rd.invoice_id.invoice_line_ids
            lines.analytic_tag_ids |= self.env["account.analytic.tag"].sudo().search([
                ("name", "=", security_post_name)])
