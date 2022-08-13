from odoo import models, api


class Lead(models.Model):
    _inherit = "crm.lead"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._create_customer_other_contact()
        return res

    def write(self, vals):
        leads_to_change = self.filtered(
            lambda r: r._track_address_changes(vals))
        res = super().write(vals)
        leads_to_change._create_customer_other_contact()
        return res

    def _track_address_changes(self, vals):
        self.ensure_one()
        fields_to_track = [
            "street", "street2", "city",
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
                "street2": r.street2,
                "state_id": r.state_id.id,
                "country_id": r.country_id.id,
                "type": "other",
            })
