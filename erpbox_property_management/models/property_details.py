from odoo import models, fields, api


DAYS_IN_MONTH = 30


class PropertyDetails(models.Model):
    _inherit = "property.details"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Related customer",
        required=True,
    )

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
                    if not last_paid and tenant.rent_details_ids:
                        last_paid = tenant.rent_details_ids[0]
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
        if not 'crm' in self._context:
            leads_to_change = self.filtered(
                lambda r: r._track_address_changes(vals))
            res = super().write(vals)
            leads_to_change._create_customer_other_contact()
            return res
        return super().write(vals)

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        if not 'crm' in self._context:
            res._create_customer_other_contact()
        return res

    def _track_address_changes(self, vals):
        self.ensure_one()
        fields_to_track = [
            "street", "city",
            "state_id", "zip", "country_id"]
        if any((
            self[field] != vals.get(field, self[field])
            for field in fields_to_track
        )):
            return True

    def _create_customer_other_contact(self):
        for r in self:
            if not r.partner_id: break
            r.partner_id.child_ids |= self.env["res.partner"].create({
                "name": r.partner_id.name,
                "zip": r.zip,
                "city": r.city,
                "street": r.street,
                "state_id": r.state_id.id,
                "country_id": r.country_id.id,
                "type": "other",
            })
