import json
from odoo import models, fields, api


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
                rds = tenant.rent_details_ids.filtered(
                    lambda r: r.date <= today and \
                    r.invoice_id.state != "posted")

                for rd in rds:
                    inv = rd.invoice_id
                    inv.action_post()
                    if inv.invoice_has_outstanding and rd.payment_state != "paid":
                        widget_data = json.loads(inv.invoice_outstanding_credits_debits_widget)
                        inv.js_assign_outstanding_line(widget_data["content"][0]["id"])
