from odoo import models, fields


days = list(map(str, range(1, 32)))


class ProductTemplate(models.Model):
    _inherit = "product.template"

    auto_validation = fields.Selection(
        selection=list(zip(days, days)),
        string="Auto Validation",
    )
