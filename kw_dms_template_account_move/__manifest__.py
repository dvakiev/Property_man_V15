{
    'name': 'Document Template Account Move',
    'version': '15.0.1.0.2',
    'license': 'Other proprietary',
    'category': 'Document',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'depends': ['kw_dms_template', 'account'],
    'data': [
        'data/template_types.xml',

        'views/document_views.xml',
        'views/template_views.xml',

    ],
    'installable': True,
}
