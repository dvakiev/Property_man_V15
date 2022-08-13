from odoo import models, fields, api


class Tenant(models.Model):
    _inherit = "tenant.details"
    _rec_name = "product_id"

    crm_lead_id = fields.Many2one(
        comodel_name="crm.lead",
        string="Lead",
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
    )
    analytic_account_name = fields.Char(
        string="Name",
        required=True,
    )
    is_contract = fields.Boolean(
        string="Is contract",
        default=True,
    )
    contract_type = fields.Selection(
        string="Contract type",
        selection=[('sale', 'With customer'), ('purchase', 'With purchase')],
    )
    group_id = fields.Many2one(
        comodel_name="account.analytic.group",
        string="Group",
    )
    parent_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Parent analytic",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company.id,
    )
    is_indefinite = fields.Boolean(
        string='Indefinite'
    )
    contract_sign_date = fields.Date(
        string='Contract sign date'
    )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string="Payment term"
    )
    parent_contract_id = fields.Many2one(
        comodel_name='account.analytic.line',
        string='Parent contract',
    )
    contract_subtype = fields.Selection(
        string="Contract subtype",
        selection=[('main', 'Main'), ('additional', 'Additional')],
        default='main'
    )
    document_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Contract template",
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for r in self:
            r.rent = r.product_id.lst_price

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not "analytic_account_id" in vals:
                vals["analytic_account_name"] = vals.get("code")
                vals["analytic_account_id"] = self.env["account.analytic.account"].create({
                    "name": "/",
                    "group_id": vals.get("group_id"),
                    "parent_id": vals.get("parent_id"),
                    "partner_id": vals.get("partner_id"),
                    "company_id": vals.get("company_id"),
                    "is_contract": vals.get("is_contract"),
                    "contract_type": vals.get("contract_type"),
                    "is_indefinite": vals.get("is_indefinite"),
                    "contract_date_end": vals.get("end_date"),
                    "contract_date_start": vals.get("start_date"),
                    "payment_term_id": vals.get("payment_term_id"),
                    "contract_currency_id": vals.get("currency_id"),
                    "contract_subtype": vals.get("contract_subtype"),
                    "parent_contract_id": vals.get("parent_contract_id"),
                    "contract_sign_date": vals.get("contract_sign_date"),
                }).id
        res = super().create(vals_list)
        for r in res:
            r.analytic_account_name = r.code
            r.analytic_account_id.code = r.code
        leads = res.filtered(lambda r: r.crm_lead_id).mapped("crm_lead_id")
        leads.stage_id = self.env.ref("erpbox_property_management.stage_contract").id
        return res

    def write(self, vals):
        res = super().write(vals)
        for r in self:
            aa = r.analytic_account_id
            aa.write({
                "code": vals.get("code", aa.code),
                "group_id": vals.get("group_id", aa.group_id.id),
                "parent_id": vals.get("parent_id", aa.parent_id.id),
                "partner_id": vals.get("partner_id", aa.partner_id.id),
                "company_id": vals.get("company_id", aa.company_id.id),
                "is_contract": vals.get("is_contract", aa.is_contract),
                "name": vals.get("analytic_account_name", aa.name),
                "contract_type": vals.get("contract_type", aa.contract_type),
                "is_indefinite": vals.get("is_indefinite", aa.is_indefinite),
                "payment_term_id": vals.get(
                    "payment_term_id", aa.payment_term_id.id),
                "contract_currency_id": vals.get(
                    "currency_id", aa.currency_id.id),
                "contract_subtype": vals.get(
                    "contract_subtype", aa.contract_subtype),
                "contract_date_end": vals.get(
                    "end_date", aa.contract_date_end),
                "parent_contract_id": vals.get(
                    "parent_contract_id", aa.parent_contract_id.id),
                "contract_sign_date": vals.get(
                    "contract_sign_date", aa.contract_sign_date),
                "contract_date_start": vals.get(
                    "start_date", aa.contract_date_start),
            })
        return res

    def action_print_contract(self):
        self.ensure_one()
        dt = self.document_template_id
        return dt.report_template.report_action(self, None)
