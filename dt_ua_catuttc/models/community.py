# Copyright 2022 DotTek
# @author: Dmytro Pavlov (<dottek.ukraine@gmail.com>)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).
from odoo import models, fields, api


class Community(models.Model):
    _name = 'catuttc.community'
    _description = 'CATUTTC Community'
    _inherit=["catuttc.mixin"]

    region_id = fields.Many2one('catuttc.region', 'Region', readonly=True, required=True)
    district_id = fields.Many2one('catuttc.district', 'District', readonly=True, required=True)

    locality_ids = fields.One2many(
        "catuttc.locality",
        inverse_name="community_id",
        string="Localities",
        readonly=True,
    )
    locality_district_ids = fields.One2many(
        "catuttc.locality.district",
        inverse_name="community_id",
        string="Locality districts",
        readonly=True,
    )

    localities_count = fields.Integer(
        "Localities count",
        compute="_compute_localities_count",
    )
    locality_districts_count = fields.Integer(
        "Locality districts count",
        compute="_compute_locality_districts_count",
    )

    @api.depends("locality_ids")
    def _compute_localities_count(self):
        for r in self:
            r.localities_count = len(r.locality_ids)

    @api.depends("locality_district_ids")
    def _compute_locality_districts_count(self):
        for r in self:
            r.locality_districts_count = len(r.locality_district_ids)

    def action_open_localities(self):
        return self._open_action_for("locality", "community_id")

    def action_open_locality_districts(self):
        return self._open_action_for("locality_district", "community_id")
