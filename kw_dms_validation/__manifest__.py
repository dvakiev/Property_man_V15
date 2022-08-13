{
    'name': 'DMS Validation',
    'version': '15.0.1.0.1',
    'license': 'Other proprietary',
    'category': 'Document',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'depends': ['kw_dms',
                "kw_document_validation", ],
    'data': [
        'security/ir.model.access.csv',
        'views/type_views.xml',
        'views/document_views.xml',
    ],
    'application': True,
    'installable': True,
}
