from odoo import models, fields


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
