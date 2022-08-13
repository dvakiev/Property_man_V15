{
    'name': 'Document partner',
    'version': '15.0.1.0.0',
    'license': 'Other proprietary',
    'category': 'Document',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'depends': ['kw_document_validation', 'kw_partner_document', ],
    'data': [
        'views/partner_views.xml',
    ],
    'installable': True,
    'auto_install': True,
}
