import logging

from odoo import fields, models, api, _
from odoo.osv.expression import OR

_logger = logging.getLogger(__name__)


class KwDirectory(models.Model):
    _name = 'kw.dms.directory'
    _description = 'DMS Directory'

    _inherit = [
        "kw.dms.mixins.thumbnail",
        "kw.dms.security.mixin",
    ]

    _rec_name = "complete_name"
    _order = "complete_name"

    _parent_store = True
    _parent_name = "parent_id"
    _directory_field = _parent_name

    name = fields.Char(required=True, )
    complete_name = fields.Char(
        compute="_compute_complete_name", store=True, recursive=True, )
    is_main = fields.Boolean(
        default=False, readonly=True, )
    parent_path = fields.Char(index=True)
    color = fields.Integer(default=0)
    category_id = fields.Many2one(
        comodel_name="kw.dms.category",
        string="Category", )
    file_ids = fields.One2many(
        comodel_name="kw.document",
        inverse_name="directory_id",
        string="Files",
        auto_join=False,
        copy=False, )
    tag_ids = fields.Many2many(
        comodel_name="kw.dms.tag",
        domain="[('category_id','=',category_id)]",
        string="Tags", readonly=False, )
    child_directory_ids = fields.One2many(
        comodel_name="kw.dms.directory",
        inverse_name="parent_id",
        string="Subdirectories",
        auto_join=False,
        copy=False, )
    parent_id = fields.Many2one(
        comodel_name="kw.dms.directory",
        domain="['|', ('permission_create', '=', True), "
               "('permission_write', '=', True)]",
        string="Parent Directory",
        ondelete="restrict",
        index=True, store=True, readonly=False,
        copy=True, )
    storage_id = fields.Many2one(
        comodel_name="kw.dms.storage",
        readonly=False,
        compute="_compute_storage_id",
        compute_sudo=True,
        string="Storage",
        auto_join=True,
        store=True,
        ondelete="restrict", )
    count_directories = fields.Integer(
        compute="_compute_count_directories",
        string="Count Subdirectories Title", )
    count_files = fields.Integer(
        compute="_compute_count_files", string="Count Files Title", )
    count_directories_title = fields.Char(
        compute="_compute_count_directories", string="Count Subdirectories", )
    count_files_title = fields.Char(
        compute="_compute_count_files", string="Count Files", )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        inverse="_inverse_model_id",
        string="Model", )
    res_id = fields.Integer(
        string="Linked attachments record ID", )
    res_model = fields.Char(
        string="Linked attachments model", )
    save_type = fields.Selection(
        selection=[
            ("database", _("Database")),
            ("file", _("Filestore")),
            ("attachment", _("Attachment")), ],
        related='storage_id.save_type', )
    group_ids = fields.Many2many(
        comodel_name="kw.dms.access.group",
        relation="dms_directory_groups_rel",
        column1="aid",
        column2="gid",
        string="Groups", )
    complete_group_ids = fields.Many2many(
        comodel_name="kw.dms.access.group",
        relation="dms_directory_complete_groups_rel",
        column1="aid",
        column2="gid",
        string="Complete Groups",
        compute="_compute_groups",
        readonly=True,
        store=True,
        compute_sudo=True,
        recursive=True, )
    storage_id_inherit_access_from_parent_record = fields.Boolean(
        related="storage_id.inherit_access_from_parent_record",
        related_sudo=True,
        store=True,)
    is_root_directory = fields.Boolean(
        default=False,
        help="""Indicates if the directory is a root directory.
        A root directory has a settings object, while a directory with a set
        parent inherits the settings form its parent.""",)

    def _get_domain_by_access_groups(self, operation):
        """Special rules for directories."""
        self_filter = [
            ("storage_id_inherit_access_from_parent_record", "=", False),
            ("id", "inselect", self._get_access_groups_query(operation)),
        ]
        result = super()._get_domain_by_access_groups(operation)
        if operation == "create":
            result = OR(
                [
                    [("is_root_directory", "=", False)] + result,
                    [("is_root_directory", "=", True)] + self_filter,
                ]
            )
        else:
            result = self_filter
        return result

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Category name already exists!"),
        ("name_model_id", "unique (model_id)",
         "A directory with such a model already exists!"), ]

    @api.depends("group_ids", "parent_id", )
    def _compute_groups(self):
        for one in self:
            groups = one.group_ids
            if one.parent_id:
                groups |= one.parent_id.complete_group_ids
            self.complete_group_ids = groups

    @api.onchange('storage_id', "model_id")
    def _onchange_storage_id(self):
        res = {}
        for record in self:
            if (record.storage_id.save_type == "attachment"
                    and record.storage_id.inherit_access_from_parent_record):
                record.group_ids = False
            if record.storage_id and record.storage_id.model_ids:
                model_ids = record.storage_id.model_ids
                res['domain'] = {'model_id': [('id', 'in', model_ids.ids)]}
            if record.model_id:
                self._inverse_model_id()
        return res

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = "{} / {}".format(
                    category.parent_id.complete_name,
                    category.name,
                )
            else:
                category.complete_name = category.name

    @api.depends("child_directory_ids")
    def _compute_count_directories(self):
        for record in self:
            directories = len(record.child_directory_ids)
            record.count_directories = directories
            record.count_directories_title = _(
                "%s Subdirectories") % directories

    @api.depends("file_ids")
    def _compute_count_files(self):
        for record in self:
            files = len(record.file_ids)
            record.count_files = files
            record.count_files_title = _("%s Files") % files

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        for record in self:
            if record.parent_id and record.parent_id.storage_id:
                record.write({'storage_id': record.parent_id.storage_id})

    def _inverse_model_id(self):
        for record in self:
            record.res_model = record.model_id.model

    def directories_file_action(self):
        return {
            'name': _('Documents'),
            'view_mode': 'tree,form',
            'res_model': 'kw.document',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('directory_id', '=', self.id)],
            'context': {
                'default_directory_id': self.id,
                'search_directory_id': self.id}}

    def _compute_storage_id(self):
        for record in self:
            if record.parent_id:
                record.write({'storage_id': record.parent_id.storage_id})
            else:
                record.storage_id = record.storage_id
