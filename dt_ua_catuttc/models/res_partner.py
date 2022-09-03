# Copyright 2022 DotTek
# @author: Dmytro Pavlov (<dottek.ukraine@gmail.com>)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).
from odoo import models, fields


class Partner(models.Model):
    _inherit = "res.partner"

    region_id = fields.Many2one("catuttc.region", "Region", required=False)
    region_special = fields.Boolean("Region special", related="region_id.special")
    district_id = fields.Many2one("catuttc.district", "District")
    community_id = fields.Many2one("catuttc.community", "Community")
    locality_id = fields.Many2one("catuttc.locality", "Locality")
    locality_district_id = fields.Many2one("catuttc.locality.district",
                                    "Locality district", required=False)
