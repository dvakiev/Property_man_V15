from odoo import models, fields, api


class Partner(models.Model):
    _inherit = "res.partner"

    security_post_id = fields.Many2one(
        comodel_name="erpbox.security.post",
        string="Security Post №",
        required=False,
    )
    code = fields.Char(
        string="Contract №",
        compute="_compute_code",
        store=True
    )

    def _compute_code(self):
        for r in self:
            code = ""
            if r.id:
                lead = self.env["crm.lead"].search([
                    ("partner_id", "=", r.id)],
                    order="create_date desc",
                    limit=1)
                if lead and lead.property_details_id:
                    code = lead.property_details_id.code
            r.code = code
