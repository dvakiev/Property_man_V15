{
    'name': 'Document template',
    'version': '15.0.1.0.0',
    'license': 'Other proprietary',
    'category': 'Document',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'depends': ['kw_document', ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'templates/report_template.xml',

        'views/type_views.xml',
        'views/document_views.xml',
        'views/template_views.xml',
        'views/kind_views.xml',

    ],
    'installable': True,
}
