# -*- coding: utf-8 -*-
{
    'name': 'ERPBOX - Analytic Contract',
    'version': '15.0.1.0.3',
    'category': 'Accounting/Accounting',
    'license': 'LGPL-3',
    'author': "Leonid Kolesnichenko",
    'maintainer': 'Simbioz Holding LLC',
    'website': 'https://simbioz.ua/',
    'depends': [
        'analytic',
        'account',
        'base_account_budget',
        'erpbox_account_menu',
        'erpbox_account_move_origin',
        'base_accounting_kit',  # _prepare_move_line_for_currency
        'point_of_sale',
    ],
    'data': [
        'views/account_analytic_account_view.xml',
        'views/account_move_view.xml',
        'views/account_payment_view.xml',
        'views/res_partner_views.xml',
        'views/account_bank_statement_view.xml',
        'views/pos_config_view.xml',
    ],
    'installable': True,
    'auto_install': False
}
