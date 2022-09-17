import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DmsAccessGroups(models.Model):
    _inherit = "kw.dms.access.group"

    hr_department_id = fields.Many2one(
        comodel_name='hr.department')

    @api.onchange("hr_department_id")
    def _onchange_parent_id(self):
        for obj in self:
            if obj.hr_department_id:
                for h in obj.hr_department_id.member_ids:
                    obj.users += obj.env['res.users'].search([
                        ('id', 'in', h.user_id.ids), ])
