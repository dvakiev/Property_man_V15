# Copyright 2022 DotTek
# @author: Dmytro Pavlov (<dottek.ukraine@gmail.com>)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).
from odoo import models, fields, api


class District(models.Model):
    _name = 'catuttc.district'
    _description = 'CATUTTC Region district'
    _inherit=["catuttc.mixin"]

    region_id = fields.Many2one('catuttc.region', 'Region', readonly=True, required=True)

    community_ids = fields.One2many(
        "catuttc.community",
        inverse_name="district_id",
        string="Communities",
        readonly=True,
    )
    locality_ids = fields.One2many(
        "catuttc.locality",
        inverse_name="district_id",
        string="Localities",
        readonly=True,
    )
    locality_district_ids = fields.One2many(
        "catuttc.locality.district",
        inverse_name="district_id",
        string="Locality districts",
        readonly=True,
    )

    communities_count = fields.Integer(
        "Communities count",
        compute="_compute_communities_count",
    )
    localities_count = fields.Integer(
        "Localities count",
        compute="_compute_localities_count",
    )
    locality_districts_count = fields.Integer(
        "Locality districts count",
        compute="_compute_locality_districts_count",
    )

    @api.depends("community_ids")
    def _compute_communities_count(self):
        for r in self:
            r.communities_count = len(r.community_ids)

    @api.depends("locality_ids")
    def _compute_localities_count(self):
        for r in self:
            r.localities_count = len(r.locality_ids)

    @api.depends("locality_district_ids")
    def _compute_locality_districts_count(self):
        for r in self:
            r.locality_districts_count = len(r.locality_district_ids)

    def action_open_communities(self):
        return self._open_action_for("community", "district_id")

    def action_open_localities(self):
        return self._open_action_for("locality", "district_id")

    def action_open_locality_districts(self):
        return self._open_action_for("locality_district", "district_id")