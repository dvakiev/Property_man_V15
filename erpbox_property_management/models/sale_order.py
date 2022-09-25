from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    analytic_contract_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Contract",
        required=True,
    )
    tenant_id = fields.Many2one(
        comodel_name="tenant.details",
        string="Tenant",
    )

    @api.onchange('order_line')
    @api.constrains('order_line')
    @api.constrains('partner_id')
    def compute_analytic_tags(self):
        for rec in self:
            if rec.tenant_id and rec.order_line:
                security_post_name = rec.tenant_id.security_post_id.name
                for line in rec.order_line:
                    line.analytic_tag_ids |= self.env[
                        "account.analytic.tag"].sudo().search([
                            ("name", "=", security_post_name)], limit=1)
