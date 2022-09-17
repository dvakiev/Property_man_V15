# pylint: skip-file
import logging
import json
from odoo import http

_logger = logging.getLogger(__name__)


class Details(http.Controller):

    @http.route(['''/details''',
                 '''/details/invoice/<int:ids>''',
                 '''/details/departure/<int:gbr>''',
                 '''/details/status/<int:status>''',
                 ], auth='public', type='http', website=True, csrf=False)
    def details(self, ids=None, gbr=None, search=None, status=None, **post):
        if status:
            stat = self.status(status)
            detail = http.request.env['tenant.details'].search(
                [('id', '=', status)], limit=1)
            return http.request.render(
                'erpbox_sequr_pult.details',
                {'partners': detail.partner_id,
                 'invisible_status': detail.id,
                 'stat': stat})
        if gbr:
            self.departure(gbr)
            detail = http.request.env['tenant.details'].search(
                [('id', '=', gbr)], limit=1)
            return http.request.render(
                'erpbox_sequr_pult.details',
                {'partners': detail.partner_id,
                 'invisible_status': detail.id})
        if ids:
            invoice = self.invoice(ids)
            detail = http.request.env['tenant.details'].search(
                [('id', '=', ids)], limit=1)
            return http.request.render(
                'erpbox_sequr_pult.details',
                {'partners': detail.partner_id,
                 'invisible': invoice, 'invisible_status': invoice})
        if search:
            detail = []
            try:
                detail = http.request.env['tenant.details'].search(
                    [('code', 'ilike', search)], limit=1)
            except Exception as e:
                _logger.info(e)
            if not detail:
                try:
                    detail = http.request.env['tenant.details'].search(
                        [('property_id.name', 'ilike', search)], limit=1)
                except Exception as e:
                    _logger.info(e)
                if not detail:
                    try:
                        detail = http.request.env['res.partner'].search(
                            ['|', ('phone', 'ilike', search),
                             ('mobile', 'ilike', search)], limit=1)
                    except Exception as e:
                        _logger.info(e)
                    if not detail:
                        try:
                            detail = http.request.env['res.partner'].search(
                                [('name', 'ilike', search)], limit=1)
                        except Exception as e:
                            _logger.info(e)
                        if detail:
                            return http.request.render(
                                'erpbox_sequr_pult.details',
                                {'partners': detail, 'search': search})
                        return http.request.render(
                            'erpbox_sequr_pult.details', {
                                'search': search})
                    if detail:
                        return http.request.render(
                            'erpbox_sequr_pult.details',
                            {'partners': detail, 'search': search})
                if detail:
                    return http.request.render('erpbox_sequr_pult.details', {
                        'partners': detail.partner_id, 'search': search})
            if detail:
                return http.request.render('erpbox_sequr_pult.details', {
                    'partners': detail.partner_id, 'search': search})
        if not search:
            return http.request.render('erpbox_sequr_pult.details', {
                'partners': [], 'search': search})

    def invoice(self, ids):
        detail = http.request.env['tenant.details'].search(
            [('id', '=', ids)], limit=1)
        sale = http.request.env['sale.order'].create(
            {'tenant_id': detail.id, 'partner_id': detail.partner_id.id,
             'analytic_contract_id': detail.analytic_account_id.id})
        sale.order_line.create({'product_id': 3302, 'order_id': sale.id})
        sale.action_confirm()
        detail.sale_order_id_website = sale
        payment = http.request.env['sale.advance.payment.inv'].with_context({
            'active_model': 'sale.order',
            'active_ids': [sale.id],
            'active_id': sale.id,
        }).create({
            'advance_payment_method': 'delivered'
        })
        payment.create_invoices()
        if sale.invoice_ids:
            for inv in sale.invoice_ids:
                inv.action_post()
                if inv.invoice_has_outstanding:
                    widget_data = json.loads(
                        inv.invoice_outstanding_credits_debits_widget)
                    for con in widget_data['content']:
                        if inv.payment_state != "paid":
                            inv.js_assign_outstanding_line(
                                con["id"])
                if inv.payment_state != "paid":
                    link = http.request.env[
                        'payment.link.wizard'].with_context({
                            'active_model': 'account.move',
                            'active_id': inv.id}).create({})
                    inv.message_post(body=link.link)
                    # inv.env['account.payment.register'].with_context(
                    #     active_model='account.move',
                    #     active_ids=inv.ids).create(
                    #     {'payment_date': inv.date}).action_create_payments()
        return detail.id

    def departure(self, gbr):
        detail = http.request.env['tenant.details'].search(
            [('id', '=', gbr)], limit=1)
        if detail.sale_order_id_website:
            for s in detail.sale_order_id_website:
                for pro in s.order_line:
                    if pro.product_id.id == 3302:
                        for d in s.picking_ids:
                            if d.state != 'done':
                                for line in d.move_ids_without_package:
                                    line.quantity_done = line.product_uom_qty
                                d.button_validate()
                                return gbr

    def status(self, stat):
        detail = http.request.env['tenant.details'].search(
            [('id', '=', stat)], limit=1)
        if detail.sale_order_id_website:
            for s in detail.sale_order_id_website:
                for inv in s.invoice_ids:
                    if inv.transaction_ids:
                        inv.transaction_ids[-1].check_status_wayforpay()
                        return inv.transaction_ids[-1].state
                    else:
                        return 'No Transactions'
