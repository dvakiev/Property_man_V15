from odoo import models, fields, api, _


class SecurityPost(models.Model):
    _name = "erpbox.security.post"
    _description = "Security Post"

    name = fields.Char(
        string="Security Post Name",
        required=True,
    )
    # display_name = fields.Char(
    #     string="Security Post",
    #     compute="_compute_display_name",
    # )
    number = fields.Integer(
        string="Security Post №",
        required=True,
    )
    locality_district_id = fields.Many2one(
        comodel_name="catuttc.locality.district",
        string="Locality district",
        required=True,
    )
    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Sequence",
        required=True,
    )

    # @api.depends("number")
    # def _compute_display_name(self):
    #     for r in self:
    #         r.display_name = _("Security Post №%d", (r.number))

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for r in res:
            self.env["account.analytic.tag"].sudo().create({
                "name": r.name
            })
        return res
