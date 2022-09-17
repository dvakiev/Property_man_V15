{
    'name': 'Document Management System',
    'version': '15.0.1.0.7',
    'license': 'Other proprietary',
    'category': 'Document',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'depends': ["mail",
                # 'hr',
                'portal', 'utm', 'base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu_views.xml',
        'views/directory_views.xml',
        'views/tag_views.xml',
        'views/category_views.xml',
        'views/storage_views.xml',
        'views/document_views.xml',
        'views/access_groups_views.xml',
        'views/type_views.xml',
        'data/ir_sequence_data.xml',
        # 'data/kw_dms_attachment_type.xml',
        'data/kw_access_group_default.xml',
        'data/kw_dms_storages.xml',
        'data/kw_dms_directory.xml',
        'data/document.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "kw_dms/static/src/scss/directory_kanban.scss",
            # 'kw_document/static/src/js/kw_document.js'
        ], },
    'application': True,
    'installable': True,
}
