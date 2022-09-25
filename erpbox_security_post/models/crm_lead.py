from odoo import models, fields, api


class Lead(models.Model):
    _inherit = "crm.lead"

    security_post_id = fields.Many2one(
        'erpbox.security.post',
        store=True,
    )
    security_post_ids = fields.Many2many(
        'erpbox.security.post',
        compute='_compute_security_post_id')

    @api.onchange('partner_id')
    @api.depends('partner_id')
    def _compute_security_post_id(self):
        for obj in self:
            if obj.partner_id:
                obj.write(
                    {'security_post_ids': [
                        (6, 0, obj.partner_id.security_post_ids.ids)]}
                )
            else:
                obj.write(
                    {'security_post_ids': False}
                )
