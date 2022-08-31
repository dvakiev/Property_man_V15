# Copyright 2022 DotTek
# @author: Dmytro Pavlov (<dottek.ukraine@gmail.com>)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).
from odoo import models, fields


class CatuttcMixin(models.AbstractModel):
    _name = 'catuttc.mixin'
    _description = 'CATUTTC'
    category_id = fields.Many2one(
        'catuttc.category',
        string='Category',
        readonly=True
    )
    name = fields.Char('Name', readonly=True, required=True)
    code = fields.Char('CATUTTC code', readonly=True)

    def _open_action_for(self, entities_name, ref_field):
        self.ensure_one()
        action = self.env.ref("dt_ua_catuttc.action_catuttc_{}".format(
            entities_name)).sudo().read()[0]
        action.update({
            "domain": [(ref_field, "=", self.id)],
        })
        return action
