# Copyright 2022 DotTek
# @author: Dmytro Pavlov (<dottek.ukraine@gmail.com>)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).
from odoo import fields, models


class Category(models.Model):
    _name = 'catuttc.category'
    _description = 'CATUTTC Category'
    _rec_name = 'display_name'

    name = fields.Char(
        'Category name',
        readonly=True,
    )
    letter = fields.Char(
        "Letter",
        readonly=True,
        size=3,
    )
    display_name = fields.Char(compute = '_compute_display_name')

    def _compute_display_name(self):
        for r in self:
            r.display_name = f"{r.name} ({r.letter})"
