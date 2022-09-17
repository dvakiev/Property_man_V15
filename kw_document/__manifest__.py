{
    'name': 'Document',
    'version': '15.0.1.0.4',
    'license': 'Other proprietary',
    'category': 'Document',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'depends': ['base', 'mail', 'portal', 'utm', ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/document_kind.xml',
        'data/document.xml',

        'views/menu_views.xml',
        'views/kind_views.xml',
        'views/type_views.xml',
        'views/document_views.xml',

    ],
    'demo': [
        'demo/document_type.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'kw_document/static/src/js/kw_document.js',
        ],
    },
    'application': True,
    'installable': True,
}
