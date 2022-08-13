from odoo import api, fields, models


class DmsAccessGroups(models.Model):
    _name = "kw.dms.access.group"
    _description = "Record Access Groups"

    name = fields.Char(string="Group Name", required=True)
    hr_department_id = fields.Many2one(
        comodel_name='hr.department')
    perm_create = fields.Boolean(string="Create Access")
    perm_write = fields.Boolean(string="Write Access")
    perm_unlink = fields.Boolean(string="Unlink Access")
    perm_read = fields.Boolean(string="Read Access")

    perm_inclusive_create = fields.Boolean(
        string="Inherited Create Access",
        compute="_compute_inclusive_permissions",
        store=True, )
    perm_inclusive_write = fields.Boolean(
        string="Inherited Write Access",
        compute="_compute_inclusive_permissions",
        store=True, )
    perm_inclusive_unlink = fields.Boolean(
        string="Inherited Unlink Access",
        compute="_compute_inclusive_permissions",
        store=True, )
    perm_inclusive_read = fields.Boolean(
        string="Inherited Read Access",
        compute="_compute_inclusive_permissions",
        store=True, )
    users = fields.Many2many(
        comodel_name="res.users",
        relation="dms_access_group_users_rel",
        column1="gid",
        column2="uid",
        recursive=True, )

    _sql_constraints = [
        ("name_uniq", "unique (name)",
         "The name of the group must be unique!")]

    @api.depends(
        "perm_read",
        "perm_create",
        "perm_unlink",
        "perm_write", )
    def _compute_inclusive_permissions(self):
        """Provide full permissions inheriting from parent recursively."""
        for one in self:
            one.update(
                {"perm_inclusive_%s"
                 % perm: (one["perm_%s" % perm])
                 for perm in ("create", "unlink", "write", "read", )})

    @api.onchange("hr_department_id")
    def _onchange_parent_id(self):
        if self.hr_department_id:
            ids = [x.user_id.ids for x in self.hr_department_id.member_ids]
            self.users += self.env['res.users'].search([
                ('id', 'in', ids[0]), ])
