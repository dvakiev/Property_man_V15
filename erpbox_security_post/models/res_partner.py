from odoo import models, fields


class Partner(models.Model):
    _inherit = "res.partner"

    security_post_id = fields.Many2one(
        comodel_name="erpbox.security.post",
        string="Security Post №",
    )