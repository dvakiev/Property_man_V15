from odoo import models, fields, api
from odoo.exceptions import UserError


days = list(map(str, range(1, 32)))


class ProductTemplate(models.Model):
    _inherit = "product.template"

    auto_validation = fields.Selection(
        selection=list(zip(days, days)),
        string="Auto Validation",
    )

    @api.model
    def cron_auto_validate_tenant_invoices(self):
        today = fields.Date.today()
        current_day = str(today.day)
        products = self.env["product.product"].search([
            ("auto_validation", "=", current_day)])

        for product in products:
            tenants = self.env["tenant.details"].search([
                ("state", "=", "in_progress"),
                ("product_id", "=", product.id)])

            for tenant in tenants:
                check_balance = sum(self.env["account.move.line"].search([
                        ("partner_id", "=", tenant.partner_id.id)
                    ]).mapped("balance")) * -1
                rds = tenant.rent_details_ids.filtered(
                    lambda r: r.date <= today and \
                    r.invoice_id.state != "posted")

                for rd in rds:
                    rd.invoice_id.action_post()
                    if check_balance > 0 and rd.payment_state != "paid":
                        wizard = self.env["account.payment.register"].create({})
                        wizard.action_create_payments()
