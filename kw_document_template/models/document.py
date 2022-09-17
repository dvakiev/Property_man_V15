import logging
import os
import subprocess
import tempfile
from contextlib import closing
import base64
from markupsafe import Markup

import lxml.html
from lxml import etree
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools.misc import find_in_path

_logger = logging.getLogger(__name__)


def _get_wkhtmltopdf_bin():
    return find_in_path('wkhtmltopdf')


class Document(models.Model):
    _inherit = 'kw.document'

    body = fields.Html()

    header = fields.Html()

    footer = fields.Html()

    paperformat_id = fields.Many2one(
        comodel_name='report.paperformat',
        default=lambda self: self.env.user.company_id.paperformat_id)
    is_generated = fields.Boolean(
        related='type_id.is_generated')
    model_id = fields.Many2one(
        comodel_name='ir.model',
        related='type_id.template_id.model_id')

    @api.onchange('type_id')
    def onchange_type_id(self):
        for obj in self:
            if obj.type_id and obj.is_generated:
                obj.body = obj.type_id.template_id.body_html
                obj.header = obj.type_id.template_id.kw_document_header
                obj.footer = obj.type_id.template_id.kw_document_footer
                obj.compile_body()

    def compile_body(self):
        for obj in self:
            f = ['subject', 'body_html', 'kw_document_header',
                 'kw_document_footer']
            t = self.type_id.template_id.generate_email(
                [obj.res_id], fields=f)[obj.res_id]
            obj.body = t.get('body_html')

    def route_print_pdf(self):
        url = '{}/kw_document_template/{}'.format(
            self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            self.id)
        return {'type': 'ir.actions.act_url', 'url': url, 'target': 'new'}

    # pylint: disable=too-many-branches
    @api.model
    def build_wkhtmltopdf_args(
            self, paperformat_id, landscape, specific_paperformat_args=None,
            set_viewport_size=False):
        if landscape is None and specific_paperformat_args and \
                specific_paperformat_args.get('data-report-landscape'):
            landscape = specific_paperformat_args.get('data-report-landscape')
        command_args = ['--disable-local-file-access']
        if set_viewport_size:
            command_args.extend(
                ['--viewport-size', landscape and '1024x1280' or '1280x1024'])
        try:
            if request:
                command_args.extend(
                    ['--cookie', 'session_id', request.session.sid])
        except AttributeError as e:
            _logger.info(e)
        command_args.extend(['--quiet'])
        if paperformat_id:
            if paperformat_id.format and paperformat_id.format != 'custom':
                command_args.extend(['--page-size', paperformat_id.format])

            if paperformat_id.page_height and paperformat_id.page_width and \
                    paperformat_id.format == 'custom':
                command_args.extend(
                    ['--page-width', str(paperformat_id.page_width) + 'mm'])
                command_args.extend(
                    ['--page-height', str(paperformat_id.page_height) + 'mm'])

            if specific_paperformat_args and specific_paperformat_args.get(
                    'data-report-margin-top'):
                command_args.extend(['--margin-top', str(
                    specific_paperformat_args['data-report-margin-top'])])
            else:
                command_args.extend(
                    ['--margin-top', str(paperformat_id.margin_top)])
            if specific_paperformat_args and specific_paperformat_args.get(
                    'data-report-dpi'):
                command_args.extend(['--dpi', str(
                    specific_paperformat_args['data-report-dpi'])])
            elif paperformat_id.dpi:
                if os.name == 'nt' and int(paperformat_id.dpi) <= 95:
                    _logger.info(
                        "Generating PDF on Windows platform require DPI >= 96."
                        " Using 96 instead.")
                    command_args.extend(['--dpi', '96'])
                else:
                    command_args.extend(['--dpi', str(paperformat_id.dpi)])
            if specific_paperformat_args and specific_paperformat_args.get(
                    'data-report-header-spacing'):
                command_args.extend(['--header-spacing', str(
                    specific_paperformat_args['data-report-header-spacing'])])
            elif paperformat_id.header_spacing:
                command_args.extend(
                    ['--header-spacing', str(paperformat_id.header_spacing)])
            command_args.extend(
                ['--margin-left', str(paperformat_id.margin_left)])
            command_args.extend(
                ['--margin-bottom', str(paperformat_id.margin_bottom)])
            command_args.extend(
                ['--margin-right', str(paperformat_id.margin_right)])
            if not landscape and paperformat_id.orientation:
                command_args.extend(
                    ['--orientation', str(paperformat_id.orientation)])
            if paperformat_id.header_line:
                command_args.extend(['--header-line'])
        if landscape:
            command_args.extend(['--orientation', 'landscape'])
        return command_args

    def prepare_html(self, html):
        IrConfig = self.env['ir.config_parameter'].sudo()
        layout = self.env.ref(
            'kw_document_template.kw_document_template_minimal_layout', False)
        if not layout:
            return {}
        base_url = IrConfig.get_param('report.url') or layout.get_base_url()

        root = lxml.html.fromstring(html)
        match_klass = "//div[contains(concat(' ', normalize-space(@class), " \
                      "' '), ' {} ')]"

        header_node = etree.Element('div', id='minimal_layout_report_headers')
        footer_node = etree.Element('div', id='minimal_layout_report_footers')
        bodies = []

        for node in root.xpath(match_klass.format('header')):
            node.getparent().remove(node)
            header_node.append(node)

        for node in root.xpath(match_klass.format('footer')):
            node.getparent().remove(node)
            footer_node.append(node)

        for node in root.xpath(match_klass.format('article')):
            layout_with_lang = layout
            # set context language to body language
            if node.get('data-oe-lang'):
                layout_with_lang = layout_with_lang.with_context(
                    lang=node.get('data-oe-lang'))
            body = layout_with_lang._render({
                'subst': False,
                'body': Markup(lxml.html.tostring(node, encoding='unicode')),
                'base_url': base_url
            })
            bodies.append(body)
        header = layout._render({
            'subst': True,
            'body': Markup(lxml.html.tostring(
                header_node, encoding='unicode')),
            'base_url': base_url})
        footer = layout._render({
            'subst': True,
            'body': Markup(lxml.html.tostring(
                footer_node, encoding='unicode')),
            'base_url': base_url})
        return bodies, header, footer

    # pylint: disable=too-many-locals
    @api.model
    def run_wkhtmltopdf(
            self, bodies, header=None, footer=None, landscape=False,
            specific_paperformat_args=None, set_viewport_size=False):

        paperformat_id = self.paperformat_id
        command_args = self.build_wkhtmltopdf_args(
            paperformat_id,
            landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size)
        files_command_args = []
        temporary_files = []
        if header:
            head_file_fd, head_file_path = tempfile.mkstemp(
                suffix='.html', prefix='report.header.tmp.')
            with closing(os.fdopen(head_file_fd, 'wb')) as head_file:
                head_file.write(header.encode())
            temporary_files.append(head_file_path)
            files_command_args.extend(['--header-html', head_file_path])
        if footer:
            foot_file_fd, foot_file_path = tempfile.mkstemp(
                suffix='.html', prefix='report.footer.tmp.')
            with closing(os.fdopen(foot_file_fd, 'wb')) as foot_file:
                foot_file.write(footer.encode())
            temporary_files.append(foot_file_path)
            files_command_args.extend(['--footer-html', foot_file_path])
        paths = []
        for i, body in enumerate(bodies):
            prefix = '%s%d.' % ('report.body.tmp.', i)
            body_file_fd, body_file_path = tempfile.mkstemp(
                suffix='.html', prefix=prefix)
            with closing(os.fdopen(body_file_fd, 'wb')) as body_file:
                body_file.write(body.encode())
            paths.append(body_file_path)
            temporary_files.append(body_file_path)
        pdf_report_fd, pdf_report_path = tempfile.mkstemp(
            suffix='.pdf', prefix='report.tmp.')
        os.close(pdf_report_fd)
        temporary_files.append(pdf_report_path)

        wkhtmltopdf = [_get_wkhtmltopdf_bin()] + command_args + \
            files_command_args + paths + [pdf_report_path]
        process = subprocess.Popen(wkhtmltopdf, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        out, err = process.communicate()
        _logger.debug(out)
        if process.returncode not in [0, 1]:
            if process.returncode == -11:
                message = _('Wkhtmltopdf failed '
                            'Memory limit too low or maximum '
                            'file number of subprocess reached.')
            else:
                message = _(
                    'Wkhtmltopdf failed.')
            raise UserError(
                message % (str(process.returncode), err[-1000:]))
        if err:
            _logger.warning('wkhtmltopdf: %s', err)
        with open(pdf_report_path, 'rb') as pdf_document:
            pdf_content = pdf_document.read()
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                _logger.error(
                    'Error when trying to remove file %s', temporary_file)
        return pdf_content

    def print_pdf(self):
        body = _('<span class="text-danger">Document printed by '
                 '{}</span>').format(self.env.user.name)
        self.message_post(body=body, message_type='comment', )
        html = '''

        <div class="header">
          <div class="row">
            {}
          </div>
        </div>
        <div class="article">
          <div class="page">
            {}
          </div>
        </div>
        <div class="footer">
          <div class="row">
            {}
          </div>
        </div>

        '''.format(self.header or '', self.body or '', self.footer or '')

        bodies, header, footer = self.prepare_html(html)

        pdf_content = self.run_wkhtmltopdf(
            bodies,
            header=header,
            footer=footer,
            landscape=False,
            specific_paperformat_args=False,
            set_viewport_size=False,
        )
        if pdf_content and self.file:
            self.file = base64.b64encode(pdf_content)
            self.filename = '{}.pdf'.format(self.name)
        return pdf_content

    @api.model
    def create(self, vals_list):
        obj = super().create(vals_list)
        if obj.type_id and obj.is_generated:
            try:
                obj.body = obj.render_message(
                    obj.type_id.template_id.body_html,
                    obj.type_id.model_id.model, obj.res_id)[obj.res_id]
                obj.header = obj.render_message(
                    obj.type_id.template_id.kw_document_header,
                    obj.type_id.model_id.model, obj.res_id)[obj.res_id]
                obj.footer = obj.render_message(
                    obj.type_id.template_id.kw_document_footer,
                    obj.type_id.model_id.model, obj.res_id)[obj.res_id]
            except Exception as e:
                _logger.info(e)
                obj.body = obj.type_id.template_id.body_html
                obj.header = obj.type_id.template_id.kw_document_header
                obj.footer = obj.type_id.template_id.kw_document_footer
                obj.compile_body()
        if obj.is_generated:
            try:
                file = obj.print_pdf()
            except Exception as e:
                _logger.info(e)
            obj.file = base64.b64encode(file)
            obj.filename = '{}.pdf'.format(obj.name)
        return obj

    def render_message(self, body, model, ids):
        template = self.env['sms.template']._render_template(
            template_src=body,
            model=model, res_ids=[ids])
        return template
