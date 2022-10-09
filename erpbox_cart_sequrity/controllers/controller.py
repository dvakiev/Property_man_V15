# pylint: skip-file
# flake8: noqa
import logging
import datetime
import json

from odoo import http
from odoo.http import request, Response
from odoo.addons.portal.controllers import portal

_logger = logging.getLogger(__name__)


class CustomerPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        x = 0
        try:
            invoice = http.request.env['account.move'].search(
                [('partner_id', '=', request.env.user.partner_id.id),
                 ('state', '=', 'posted'),
                 ('payment_state', 'in', ['not_paid', 'partial'])], limit=1)
            if not invoice:
                try:
                    product = http.request.env['product.product'].search([], limit=1)
                    inv = http.request.env['account.move'].sudo().create({
                        'partner_id': request.env.user.partner_id.id,
                        'invoice_date': datetime.datetime.now(),
                        'move_type': 'out_invoice',
                        'invoice_line_ids': [
                            (0, 0, {
                                'name': 'test',
                                'product_id': product.id,
                                'quantity': 1,
                                'price_unit': 1,
                            })]
                    })
                    inv.sudo().action_post()
                    inv.sudo()._compute_payments_widget_to_reconcile_info()
                    for con in json.loads(inv.invoice_outstanding_credits_debits_widget)['content']:
                        x += con['amount']
                    inv.sudo().button_draft()
                    inv.sudo().unlink()
                    values['outstanding_credit'] = x
                    return values
                except Exception:
                    values['outstanding_credit'] = x
                    return values
            else:
                invoice.sudo()._compute_payments_widget_to_reconcile_info()
                for con in json.loads(invoice.invoice_outstanding_credits_debits_widget)['content']:
                    x += con['amount']
                values['outstanding_credit'] = x
                return values
        except Exception:
            values['outstanding_credit'] = x
            return values
