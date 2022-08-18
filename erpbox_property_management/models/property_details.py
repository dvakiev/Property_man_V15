from odoo import models, fields


DAYS_IN_MONTH = 30


class PropertyDetails(models.Model):
    _inherit = "property.details"

    def write(self, vals):
        _state = vals.get("state")
        today = fields.Date.today()
        if _state == "available":
            properties = self.filtered(lambda r: r.state != _state)
            for prop in properties:
                tenants = self.env["tenant.details"].search([
                    ("property_id", "=", prop.id)])
                for tenant in tenants:
                    last_paid = self.env["rent.details"].search([
                        ("tenant_id", "=", tenant.id),
                        ("payment_state", "=", "paid")],
                        order="date desc",
                        limit=1,
                    )
                    if last_paid:
                        days = abs((last_paid.date - today).days)
                        tenant.write({
                            "state": "closed",
                            "rent_details_ids": [fields.Command.create({
                                "date": today,
                                "rent_amount": tenant.rent / DAYS_IN_MONTH,
                                "note": "Оплата за {} дней (с {})".format(
                                    days, last_paid.date.strftime("%d.%m.%Y")),
                            })]
                        })
                        tenant.compute_rent(qty=days)
        return super().write(vals)
