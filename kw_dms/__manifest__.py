{
    'name': 'Document Management System',
    'version': '15.0.1.0.1',
    'license': 'Other proprietary',
    'category': 'Document',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'depends': ['kw_document',
                "mail", ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/menu_views.xml',
        'views/directory_views.xml',
        'views/tag_views.xml',
        'views/category_views.xml',
        'views/storage_views.xml',
        'views/document_views.xml',
        'views/access_groups_views.xml',
        'views/type_views.xml',
        'data/ir_sequence_data.xml',
        'data/kw_dms_attachment_type.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "kw_dms/static/src/scss/directory_kanban.scss", ], },
    'application': True,
    'installable': True,
}
