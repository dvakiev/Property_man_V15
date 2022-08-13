import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ReportController(http.Controller):

    # pylint: disable=R1710
    @http.route(route='/kw_document_template/<docid>', type='http',
                auth='user', website=True, )
    def report_routes(self, docid=None):
        if docid:
            doc = request.env['kw.document'].browse(int(docid))
            pdf = doc.print_pdf()
            headers = [('Content-Type', 'application/pdf'),
                       ('Content-Length', len(pdf)), ]
            return request.make_response(pdf, headers=headers)
