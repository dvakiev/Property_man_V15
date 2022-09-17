{
    'name': ' Erpbox Sequr Pult',
    'category': 'Website',
    'license': 'Other proprietary',
    'version': '15.0.1.0.4',

    'depends': ['base', 'web', 'website', 'sale',
                'kw_generate_payment_link_so',
                'erpbox_property_management',
                'account', 'stock', 'portal', 'sale_stock'],

    'data': [
        'views/website_sequr_pult.xml',
        'data/data.xml'
    ],

    'installable': True,
}
