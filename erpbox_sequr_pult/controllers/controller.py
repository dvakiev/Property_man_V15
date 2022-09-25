# pylint: skip-file
# flake8: noqa
import logging
import json
from odoo import http

_logger = logging.getLogger(__name__)


class Details(http.Controller):

    @http.route(['''/details''',
                 '''/details/invoice/<int:ids>/<int:res_v1>''',
                 '''/details/departure/<int:gbr>/<int:res_v2>''',
                 '''/details/status/<int:status>/<int:res_v3>''',
                 ], auth='public', type='http', website=True, csrf=False)
    def details(self, ids=None, gbr=None, search=None, status=None,
                res_v1=None, res_v2=None, res_v3=None, **post):
        if status:
            stat, status_invoice = self.status(status)
            par_v3 = http.request.env['details.partner'].search(
                [('id', '=', res_v3)], limit=1)
            if par_v3:
                return http.request.render(
                    'erpbox_sequr_pult.details',
                    {'partners': par_v3.partner,
                     'invisible_status': status,
                     'status_invoice': status_invoice,
                     'stat': stat, 'id_save': par_v3.id})
        if gbr:
            self.departure(gbr)
            par_v2 = http.request.env['details.partner'].search(
                [('id', '=', res_v2)], limit=1)
            if par_v2:
                return http.request.render(
                    'erpbox_sequr_pult.details',
                    {'partners': par_v2.partner,
                     'invisible_status': gbr, 'id_save': par_v2.id})
        if ids:
            invoice, status_invoice = self.invoice(ids)
            par = http.request.env['details.partner'].search(
                [('id', '=', res_v1)], limit=1)
            if par:
                return http.request.render(
                    'erpbox_sequr_pult.details',
                    {'partners': par.partner,
                     'invisible': invoice,
                     'invisible_status': invoice,
                     'status_invoice': status_invoice,
                     'id_save': par.id})
        if search:
            detail = []
            try:
                detail = http.request.env['tenant.details'].search(
                    [('code', 'ilike', search)])
            except Exception as e:
                _logger.info(e)
            if not detail:
                try:
                    detail = http.request.env['tenant.details'].search(
                        [('property_id.name', 'ilike', search)])
                except Exception as e:
                    _logger.info(e)
                if not detail:
                    try:
                        detail = http.request.env['res.partner'].search(
                            ['|', ('phone', 'ilike', search),
                             ('mobile', 'ilike', search)])
                    except Exception as e:
                        _logger.info(e)
                    if not detail:
                        try:
                            detail = http.request.env['res.partner'].search(
                                [('name', 'ilike', search)])
                        except Exception as e:
                            _logger.info(e)
                        if detail:
                            part = http.request.env['details.partner'].create({
                                'name': 'partners'
                            })
                            part.write({
                                'partner': [[4, tax.id, 0] for tax in
                                            detail],
                            })
                            return http.request.render(
                                'erpbox_sequr_pult.details',
                                {'partners': part.partner, 'search': search,
                                 'id_save': part.id})
                        return http.request.render(
                            'erpbox_sequr_pult.details', {
                                'search': search})
                    if detail:
                        part = http.request.env['details.partner'].create({
                            'name': 'partners'
                        })
                        part.write({
                            'partner': [[4, tax.id, 0] for tax in
                                        detail],
                        })
                        return http.request.render(
                            'erpbox_sequr_pult.details',
                            {'partners': part.partner, 'search': search,
                             'id_save': part.id})
                if detail:
                    part = http.request.env['details.partner'].create({
                        'name': 'partners'
                    })
                    part.write({
                        'partner': [[4, tax.partner_id.id, 0] for tax in
                                    detail],
                    })
                    return http.request.render('erpbox_sequr_pult.details', {
                        'partners': part.partner, 'search': search,
                        'id_save': part.id})
            if detail:
                part = http.request.env['details.partner'].create({
                   'name': 'partners'
                })
                part.write({
                    'partner': [[4, tax.partner_id.id, 0] for tax in
                                detail],
                })
                return http.request.render('erpbox_sequr_pult.details', {
                    'partners': part.partner, 'search': search,
                    'id_save': part.id})
        if not search:
            return http.request.render('erpbox_sequr_pult.details', {
                'partners': [], 'search': search})

    def invoice(self, ids):
        detail = http.request.env['tenant.details'].search(
            [('id', '=', ids)], limit=1)
        sale = http.request.env['sale.order'].create(
            {'tenant_id': detail.id,
             'partner_id': detail.partner_id.id,
             'analytic_contract_id': detail.analytic_account_id.id,
             'analytic_account_id': detail.analytic_account_id.id,
             })
        sale.order_line.create({'product_id': 3302, 'order_id': sale.id})
        sale.compute_analytic_tags()
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
                return detail.id, inv.payment_state
        return detail.id, 'Error invoice'

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
                        return inv.transaction_ids[-1].state, inv.payment_state
                    else:
                        return 'No Transactions', inv.payment_state
        else:
            return 'No Transactions', 'No Invoice'
