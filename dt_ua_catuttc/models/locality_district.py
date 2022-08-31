# Copyright 2022 DotTek
# @author: Dmytro Pavlov (<dottek.ukraine@gmail.com>)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).
from odoo import models, fields, api


class LocalityDistrict(models.Model):
    _name = 'catuttc.locality.district'
    _description = 'CATUTTC Locality district'
    _inherit=["catuttc.mixin"]

    region_id = fields.Many2one('catuttc.region', 'Region', readonly=True, required=True)
    district_id = fields.Many2one('catuttc.district', 'District', readonly=True)
    community_id = fields.Many2one('catuttc.community', 'Community', readonly=True)
    locality_id = fields.Many2one('catuttc.locality', 'Locality', readonly=True)
