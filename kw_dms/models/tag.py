import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class KwTag(models.Model):
    _name = "kw.dms.tag"
    _description = "Document Tag"

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(
        default=True,
        help="The active field allows you"
             " to hide the tag without removing it.", )
    category_id = fields.Many2one(
        comodel_name="kw.dms.category",
        context="{'dms_category_show_path': True}",
        string="Category",
        ondelete="set null", )
    color = fields.Integer(string="Color Index", default=10, )
    directory_ids = fields.Many2many(
        comodel_name="kw.dms.directory",
        string="Directories",
        readonly=True, )

    file_ids = fields.Many2many(
        comodel_name="kw.document",
        string="Files",
        readonly=True, )

    count_directories = fields.Integer(compute="_compute_count_directories")
    count_files = fields.Integer(compute="_compute_count_files")

    _sql_constraints = [
        ("name_uniq", "unique (name, category_id)",
         "Tag name already exists!"), ]

    @api.depends("directory_ids")
    def _compute_count_directories(self):
        for rec in self:
            rec.count_directories = len(rec.directory_ids)

    @api.depends("file_ids")
    def _compute_count_files(self):
        for rec in self:
            rec.count_files = len(rec.file_ids)
