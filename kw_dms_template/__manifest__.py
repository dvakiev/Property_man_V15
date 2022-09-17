{
    'name': 'Document Template',
    'version': '15.0.1.0.4',
    'license': 'Other proprietary',
    'category': 'Document',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'depends': ['kw_dms'],
    'data': [
        'data/template_types.xml',

        'templates/report_template.xml',

        'views/type_views.xml',
        'views/document_views.xml',
        'views/template_views.xml',

    ],
    'installable': True,
}
