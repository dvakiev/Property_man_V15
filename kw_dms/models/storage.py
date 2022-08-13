import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class KwStorage(models.Model):

    _name = "kw.dms.storage"
    _description = "Storage"

    name = fields.Char(required=True)
    save_type = fields.Selection(
        selection=[
            ("database", _("Database")),
            ("file", _("Filestore")),
            ("attachment", _("Attachment")), ],
        default="database", required=True,
        help="""The save type is used to determine how a file is saved by the
        system. If you change this setting, you can migrate existing files
        manually by triggering the action.""", )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        help="If set, directories and files will only be available for "
        "the selected company.", )
    root_directory_ids = fields.One2many(
        comodel_name="kw.dms.directory",
        inverse_name="storage_id",
        string="Root Directories",
        auto_join=False,
        readonly=False,
        copy=False, )
    storage_directory_ids = fields.One2many(
        comodel_name="kw.dms.directory",
        inverse_name="storage_id",
        string="Directories",
        auto_join=False,
        readonly=True,
        copy=False, )

    storage_file_ids = fields.One2many(
        comodel_name="kw.document",
        inverse_name="storage_id",
        string="Files",
        auto_join=False,
        readonly=True,
        copy=False, )

    count_storage_directories = fields.Integer(
        compute="_compute_count_storage_directories",
        string="Count Directories", )
    count_storage_files = fields.Integer(
        compute="_compute_count_storage_files", string="Count Files"
    )
    model_ids = fields.Many2many("ir.model", string="Linked Models")
    inherit_access_from_parent_record = fields.Boolean(
        string="Inherit permissions from related record",
        default=False,
        help="Indicate if directories and files access work only with "
        "related model access (for example, if some directories are related "
        "with any sale, only users with read access to these sale can acess)",
    )

    @api.onchange("save_type")
    def _onchange_save_type(self):
        for record in self:
            if record.save_type == "attachment":
                record.inherit_access_from_parent_record = True

    @api.depends("storage_directory_ids")
    def _compute_count_storage_directories(self):
        for record in self:
            record.count_storage_directories = len(
                record.storage_directory_ids)

    @api.depends("storage_file_ids")
    def _compute_count_storage_files(self):
        for record in self:
            record.count_storage_files = len(record.storage_file_ids)
