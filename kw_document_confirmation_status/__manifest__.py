{
    'name': 'Document validation',
    'version': '15.0.1.0.1',
    'license': 'Other proprietary',
    'category': 'Document validation',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'depends': ['kw_document_validation', ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/document_conf_status_views.xml',
        'views/conf_status_views.xml',

    ],
    'installable': True,
}
