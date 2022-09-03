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
    debit = fields.Monetary(related="analytic_account_id.debit")
    credit = fields.Monetary(related="analytic_account_id.credit")
    balance = fields.Monetary(related="analytic_account_id.balance")
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
    )
    analytic_account_name = fields.Char(
        string="Name",
        required=False,
    )
    is_contract = fields.Boolean(
        string="Is contract",
        default=True,
    )
    contract_type = fields.Selection(
        string="Contract type",
        selection=[('sale', 'With customer'), ('purchase', 'With purchase')],
        default="sale",
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

    @api.depends()
    def compute_invoice_counter(self):
        for r in self:
            invoices = r.rent_details_ids.mapped('invoice_id')
            so = self.env["sale.order"].search([
                ('tenant_id', '=', r.id)])
            for _so in so:
                invoices |= _so.invoice_ids
            r.invoice_counter = len(invoices)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for r in self:
            r.rent = r.product_id.lst_price

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not "analytic_account_id" in vals:
                product = self.env["product.product"].browse(vals.get("product_id"))
                vals["name"] = product.name
                vals["analytic_account_name"] = vals.get("code")
                vals["analytic_account_id"] = self.env["account.analytic.account"].create({
                    "name": "/",
                    "group_id": vals.get("group_id"),
                    "parent_id": vals.get("parent_id"),
                    "partner_id": vals.get("partner_id"),
                    "company_id": vals.get("company_id"),
                    "is_contract": vals.get("is_contract"),
                    "contract_type": vals.get("contract_type", 'sale'),
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
            if r.crm_lead_id:
                r.crm_lead_id.stage_id = self.env.ref(
                    "erpbox_property_management.stage_contract").id
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

    def compute_rent(self, qty=1):
        self.ensure_one()
        if self.state != "closed":
            super().compute_rent()
            self.state = "in_progress"
            self.property_id.state = "on_lease"
        rent_details = self.rent_details_ids.filtered(
            lambda r: not r.invoice_id)
        other_account = self.env['ir.property']._get('property_account_expense_categ_id', 'product.category')
        for rd in rent_details:
            rd.invoice_id = self.env["account.move"].with_context({"check_move_validity": False}).create([{
                "move_type": "out_invoice",
                "partner_id": self.partner_id.id,
                "invoice_date": fields.Date.today(),
                "contract_id": self.analytic_account_id.id,
                "invoice_line_ids": [fields.Command.create({
                    "product_id": self.product_id.id,
                    "name": rd.tenant_id.code + " Rent for : " + str(rd.date),
                    "account_id": other_account and other_account.id or False,
                    "price_unit": rd.rent_amount,
                    "quantity": qty,
                    "analytic_account_id": rd.tenant_id.analytic_account_id.id,
                    "exclude_from_invoice_tab": False,
                })]
            }]).id

    def action_add_service(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Add service",
            "res_model": "sale.order",
            "view_mode": "form",
            "context": {
                "default_tenant_id": self.id,
                "default_partner_id": self.partner_id.id,
                "default_analytic_contract_id": self.analytic_account_id.id,
            }
        }

    def view_invoice(self):
        self.ensure_one()
        invoices = self.rent_details_ids.mapped('invoice_id')
        so = self.env["sale.order"].search([
            ('tenant_id', '=', self.id)])
        for _so in so:
            invoices |= _so.invoice_ids
        action = super().view_invoice()
        action["domain"] = [('id', 'in', invoices.ids)]
        return action
