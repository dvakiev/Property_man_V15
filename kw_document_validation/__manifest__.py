{
    'name': 'Document validation',
    'version': '15.0.1.0.0',
    'license': 'Other proprietary',
    'category': 'Document validation',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'depends': ['kw_document', 'kw_web_ir_actions_act_view_reload', ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/mail_activity_type.xml',
        'views/type_views.xml',
        'views/document_views.xml',
        'views/kind_views.xml',

    ],
    'installable': True,
}
