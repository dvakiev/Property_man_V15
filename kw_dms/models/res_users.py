import logging

from odoo import models

_logger = logging.getLogger(__name__)


class User(models.Model):
    _inherit = 'res.users'

    def write(self, vals):
        res = super(User, self).write(vals)
        manager_group = self.env.ref(
            'kw_dms.group_kw_dms_manager')
        if self.id in manager_group.users.mapped('id'):
            manager = self.env['kw.dms.access.group'].search([
                ('name', '=', 'Manager'), ('perm_read', '=', True),
                ('perm_create', '=', True), ('perm_write', '=', True),
                ('perm_unlink', '=', False)], limit=1)
            manager.sudo().users = [(4, self.id, False)]
        admin_group = self.env.ref(
            'kw_dms.group_kw_dms_admin')
        if self.id in admin_group.users.mapped('id'):
            admin = self.env['kw.dms.access.group'].search([
                ('name', '=', 'Admin'), ('perm_read', '=', True),
                ('perm_create', '=', True), ('perm_write', '=', True),
                ('perm_unlink', '=', True)], limit=1)
            admin.sudo().users = [(4, self.id, False)]

        return res
