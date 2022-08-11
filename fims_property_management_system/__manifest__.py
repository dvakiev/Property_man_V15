# -*- coding: utf-8 -*-
###############################################################################
#
# Fortutech IMS Pvt. Ltd.
# Copyright (C) 2016-TODAY Fortutech IMS Pvt. Ltd.(<http://www.fortutechims.com>).
#
###############################################################################
{
    'name': 'Property Management',
    'category': 'fleet',
    'summary': 'This module allow you to manage property, for sell, rent, buy...',
    'version': '15.0.1.0.0',
    'license': 'OPL-1',
    'description': """This module will allow to property management""",
    'depends': ['sale', 'l10n_generic_coa'],
    'author': 'Fortutech IMS Pvt. Ltd.',
    'website': 'https://www.fortutechims.com',
    'data': [
        'security/ir.model.access.csv',
        'views/property_details_view.xml',
        'views/property_type_view.xml',
        'views/form_image_preview_templates.xml',
        'views/tenant_details_view.xml',
        'views/res_partner_view.xml',
        'views/property_sales.xml',
        'data/ir_sequence_data.xml',
        'report/tenant_detail_report.xml',

    ],
    'qweb': ['static/src/xml/image.xml', ],
    "price": 49.0,
    "currency": "EUR",
    "installable": True,
    "application": True,
    "auto_install": False,
    "images": ['static/description/banner.png'],
}
