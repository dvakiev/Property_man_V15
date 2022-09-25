from odoo import models, fields, api


class Lead(models.Model):
    _inherit = "crm.lead"

    property_details_id = fields.Many2one(
        comodel_name="property.details",
        string="Property",
        required=True,
    )
    property_type_id = fields.Many2one(
        comodel_name="property.type",
        string="Property type",
        required=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not "property_details_id" in vals:
                vals["property_details_id"] = \
                    self.env["property.details"].with_context(
                        crm='crm').create({
                            "zip": vals.get("zip"),
                            "city": vals.get("city"),
                            "name": vals.get("street"),
                            "street": vals.get("street"),
                            "state_id": vals.get("state_id"),
                            "country_id": vals.get("country_id"),
                            "property_type_id": vals.get("property_type_id"),
                            "currency_id": self.env.ref("base.UAH").id,
                            "date": fields.Date.context_today(self),
                            "partner_id": vals.get("partner_id"),
                            "user_id": vals.get("user_id"),
                            "security_post_id": vals.get("security_post_id"),
                        }).id
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        for r in self:
            pid = r.property_details_id
            pid.with_context(crm='crm').write({
                "zip": vals.get("zip", pid.zip),
                "city": vals.get("city", pid.city),
                "name": vals.get("street", pid.name),
                "street": vals.get("street", pid.street),
                "state_id": vals.get("state_id", pid.state_id.id),
                "country_id": vals.get("country_id", pid.country_id.id),
                "property_type_id": vals.get("property_type_id",
                                             pid.property_type_id.id),
                "currency_id": vals.get("currency_id", pid.currency_id.id),
                "partner_id": vals.get("partner_id", pid.partner_id.id),
                "user_id": vals.get("user_id", pid.user_id.id),
                "security_post_id": vals.get("security_post_id",
                                             pid.security_post_id.id),
            })
        return res

    def action_create_contract(self):
        self.ensure_one()
        pid = self.partner_id
        action = {
            "type": "ir.actions.act_window",
            "name": "Create contract",
            "res_model": "tenant.details",
            "view_mode": "form",
            "context": {
                "default_crm_lead_id": self.id,
                "default_partner_id": pid.id if pid else False,
                "default_property_id": self.property_details_id.id,
                "default_security_post_id": self.security_post_id.id,
                "default_currency_id": self.env.ref("base.UAH").id,
                "default_start_date": fields.Date.context_today(self),
            }
        }
        return action
