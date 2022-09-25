from odoo import models, fields, api


class Partner(models.Model):
    _inherit = "res.partner"

    security_post_ids = fields.Many2many(
        comodel_name="erpbox.security.post",
        string="Security Post №",
        required=False,
    )
    security_post_id = fields.Many2one(
        comodel_name="erpbox.security.post",
        string="Security Post №",
        required=False,
    )
    contract_ids = fields.Many2many(
        string="Contract №",
        comodel_name='property.details',
        compute='_compute_contract',
    )

    def _compute_contract(self):
        for r in self:
            contract = self.env['property.details'].search(
                [('partner_id', '=', r.id)])
            if contract:
                r.write(
                    {'contract_ids': [
                        (6, 0, contract.ids)]}
                )
            else:
                r.write(
                    {'contract_ids': False}
                )
