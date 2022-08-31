# Copyright 2022 DotTek
# @author: Dmytro Pavlov (<dottek.ukraine@gmail.com>)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).
from odoo import models, fields, api


class Locality(models.Model):
    _name = 'catuttc.locality'
    _description = 'CATUTTC Locality'
    _inherit=["catuttc.mixin"]

    region_id = fields.Many2one('catuttc.region', 'Region', readonly=True,)
    district_id = fields.Many2one('catuttc.district', 'District', readonly=True)
    community_id = fields.Many2one('catuttc.community', 'Community', readonly=True)

    locality_district_ids = fields.One2many(
        "catuttc.locality.district",
        inverse_name="locality_id",
        string="Locality districts",
        readonly=True,
    )

    locality_districts_count = fields.Integer(
        "Locality districts count",
        compute="_compute_locality_districts_count",
    )

    @api.depends("locality_district_ids")
    def _compute_locality_districts_count(self):
        for r in self:
            r.locality_districts_count = len(r.locality_district_ids)

    def action_open_locality_districts(self):
        return self._open_action_for("locality_district", "locality_id")
