from odoo import models, api, fields


class Property(models.Model):
    _inherit = "property.details"

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

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for r in res:
            if r.security_post_id:
                r.code = r.security_post_id.sequence_id.next_by_id()
        return res

    def name_get(self):
        if not self._context.get('code_name'):
            return super(Property, self).name_get()
        res = []
        for record in self:
            name = record.code
            res.append((record.id, name))
        return res
