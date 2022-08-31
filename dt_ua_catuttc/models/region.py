# Copyright 2022 DotTek
# @author: Dmytro Pavlov (<dottek.ukraine@gmail.com>)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).
from odoo import models, fields, api


class Region(models.Model):
    _name = 'catuttc.region'
    _description = 'CATUTTC Region'
    _inherit=["catuttc.mixin"]

    special = fields.Boolean(
        "Special",
        store=True,
        compute="_compute_special",
    )

    district_ids = fields.One2many(
        "catuttc.district",
        inverse_name="region_id",
        string="Districts",
        readonly=True,
    )
    community_ids = fields.One2many(
        "catuttc.community",
        inverse_name="region_id",
        string="Communities",
        readonly=True,
    )
    locality_ids = fields.One2many(
        "catuttc.locality",
        inverse_name="region_id",
        string="Localities",
        readonly=True,
    )
    locality_district_ids = fields.One2many(
        "catuttc.locality.district",
        inverse_name="region_id",
        string="Locality districts",
        readonly=True,
    )

    districts_count = fields.Integer(
        "Districts count",
        compute="_compute_districts_count",
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

    @api.depends("category_id")
    def _compute_special(self):
        for r in self:
            if r.category_id.letter == "K":
                r.special = True
            else:
                r.special = False

    @api.depends("district_ids")
    def _compute_districts_count(self):
        for r in self:
            r.districts_count = len(r.district_ids)

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

    def action_open_districts(self):
        return self._open_action_for("district", "region_id")

    def action_open_communities(self):
        return self._open_action_for("community", "region_id")

    def action_open_localities(self):
        return self._open_action_for("locality", "region_id")

    def action_open_locality_districts(self):
        return self._open_action_for("locality_district", "region_id")
