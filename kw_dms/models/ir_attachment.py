from odoo import api, models, fields, exceptions, _


class IrAttachment(models.Model):

    _inherit = "ir.attachment"

    kw_document = fields.Many2one(
        comodel_name='kw.document', )

    def _get_main_dms_directories(self):
        directory = self.env['kw.dms.directory']
        if self.res_model:
            ir_model = self.env["ir.model"].sudo().search(
                [("model", "=", self.res_model)])
            directory = directory.sudo().search(
                [("model_id", "=", ir_model.id)], limit=1)
        return directory

    def _get_child_dms_directories(self, directory):
        child = self.env["kw.dms.directory"].sudo().search(
            [("res_model", "=", self.res_model),
             ("res_id", "=", self.res_id), ])
        if not child:
            model_item = self.env[self.res_model].browse(
                self.res_id)
            child = self.env["kw.dms.directory"].sudo().create(
                {"name": model_item.display_name,
                 "res_model": self.res_model,
                 "res_id": self.res_id,
                 "parent_id": directory.id,
                 "tag_ids": [(6, 0, directory.tag_ids.ids)],
                 "category_id": directory.category_id.id,
                 "storage_id": directory.storage_id.id, })
        return child

    def create_document(self, directory):
        type_id = self.env['kw.document.type'].search(
            [("is_for_attach_dir", "=", True)], limit=1)

        if not type_id:
            raise exceptions.ValidationError(
                _('Wrong! Type for attachment was absent'))

        data = {'model': self.res_model,
                'res_id': self.res_id,
                'type_id': type_id.id,
                'attachment_id': self.id,
                'category_id': directory.category_id.id,
                'storage_id': directory.storage_id.id,
                'directory_id': directory.id, }
        document = self.env['kw.document'].sudo().create(data)
        if not document.type_id.is_automatic_sequence:
            document.write({'name': self.name, })
        if self.mimetype == 'image/png':
            document.preview = self.datas
        return document

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for attachment in records:
            if attachment and attachment.res_model:
                directory = attachment._get_main_dms_directories()
                if directory:
                    child_directory = attachment._get_child_dms_directories(
                        directory)
                    document = attachment.create_document(child_directory)
                    attachment.write({'kw_document': document.id})
        return records

    def unlink(self):
        for record in self:
            if record.res_model and record.res_id:
                document = self.env['kw.document'].sudo().search(
                    [("attachment_id", "=", record.id),
                     ("model", "=", record.res_model),
                     ("res_id", "=", record.res_id), ], limit=1)
                if document:
                    document.sudo().unlink()
        return super(IrAttachment, self).unlink()

    def write(self, vals):
        res = super().write(vals)
        if vals.get("res_model") and vals.get("res_id"):
            document = self.env['kw.document'].search([
                ('attachment_id', '=', self.id),
                ('model', '=', self.res_model),
                ('res_id', '=', self.res_id), ])
            if document:
                if self.mimetype == 'image/png':
                    document.preview = self.datas
            else:
                directory = self._get_main_dms_directories()
                if directory:
                    child_dir = self._get_child_dms_directories(
                        directory)
                    document = self.create_document(child_dir)
                    self.write({'kw_document': document.id})
        return res
