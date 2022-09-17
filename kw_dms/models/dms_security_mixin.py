from logging import getLogger

from odoo import fields, models, api
from odoo.osv.expression import FALSE_DOMAIN,\
    NEGATIVE_TERM_OPERATORS, OR, TRUE_DOMAIN

_logger = getLogger(__name__)


class DmsSecurityMixin(models.AbstractModel):
    _name = "kw.dms.security.mixin"
    _description = "DMS Security Mixin"
    _directory_field = "directory_id"

    permission_read = fields.Boolean(
        compute="_compute_permissions",
        search="_search_permission_read",
        string="Read Access",
    )
    permission_create = fields.Boolean(
        compute="_compute_permissions",
        search="_search_permission_create",
        string="Create Access",
    )
    permission_write = fields.Boolean(
        compute="_compute_permissions",
        search="_search_permission_write",
        string="Write Access",
    )
    permission_unlink = fields.Boolean(
        compute="_compute_permissions",
        search="_search_permission_unlink",
        string="Delete Access",
    )

    def _compute_permissions(self):
        """Get permissions for the current record.

        ⚠ Not very performant; only display field on form views.
        """
        # Superuser unrestricted 🦸
        if self.env.su:
            self.update(
                {
                    "permission_create": True,
                    "permission_read": True,
                    "permission_unlink": True,
                    "permission_write": True,
                }
            )
            return
        # Update according to presence when applying ir.rule
        creatable = self._filter_access_rules("create")
        readable = self._filter_access_rules("read")
        unlinkable = self._filter_access_rules("unlink")
        writeable = self._filter_access_rules("write")
        for one in self:
            one.update(
                {
                    "permission_create": bool(one & creatable),
                    "permission_read": bool(one & readable),
                    "permission_unlink": bool(one & unlinkable),
                    "permission_write": bool(one & writeable),
                }
            )

    @api.model
    def _search_permission_create(self, operator, value):
        return self._get_permission_domain(operator, value, "create")

    @api.model
    def _search_permission_read(self, operator, value):
        return self._get_permission_domain(operator, value, "read")

    @api.model
    def _search_permission_unlink(self, operator, value):
        return self._get_permission_domain(operator, value, "unlink")

    @api.model
    def _search_permission_write(self, operator, value):
        return self._get_permission_domain(operator, value, "write")

    @api.model
    def _get_access_groups_query(self, operation):
        """Return the query to select access groups."""
        operation_check = {
            "create": "AND dag.perm_inclusive_create",
            "read": "",
            "unlink": "AND dag.perm_inclusive_unlink",
            "write": "AND dag.perm_inclusive_write",
        }[operation]
        select = """
            SELECT
                dir_group_rel.aid
            FROM
                dms_directory_groups_rel AS dir_group_rel
                INNER JOIN kw_dms_access_group AS dag
                    ON dir_group_rel.gid = dag.id
                INNER JOIN dms_access_group_users_rel AS users
                    ON users.gid = dag.id
            WHERE
                users.uid = %s {}
            """.format(operation_check)
        return (select, (self.env.uid,))

    @api.model
    def _get_domain_by_access_groups(self, operation):
        """Get domain for records accessible applying DMS access groups."""
        result = [
            (
                "%s.storage_id_inherit_access_from_parent_record"
                % self._directory_field,
                "=",
                False,
            ),
            (
                self._directory_field,
                "inselect",
                self._get_access_groups_query(operation),
            ),
        ]
        return result

    @api.model
    def _get_permission_domain(self, operator, value, operation):
        """Abstract logic for searching computed permission fields."""
        _self = self
        if self.env.su and value == self.env.uid:
            _self = self.sudo(False)
            value = bool(value)
        positive = (operator not in NEGATIVE_TERM_OPERATORS) == bool(value)
        if _self.env.su:
            return TRUE_DOMAIN if positive else FALSE_DOMAIN
        result = OR(
            [
                _self._get_domain_by_access_groups(operation),
            ]
        )
        if not positive:
            result.insert(0, "!")
        return result

    def _filter_access_rules_python(self, operation):
        result = super()._filter_access_rules_python(operation)
        result |= self._filter_access_rules(operation)
        return result

    @api.model_create_multi
    def create(self, vals_list):
        res = super(DmsSecurityMixin, self.sudo()).create(vals_list)
        res.flush()
        res = res.sudo(self.env.su)
        res.check_access_rights("create")
        res.check_access_rule("create")
        return res
