{
    'name': 'DMS Vchasno',
    'version': '15.0.1.0.1',
    'license': 'Other proprietary',
    'category': 'Document',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'depends': ['kw_dms', 'kw_vchasno'],
    'data': [
        'views/document_views.xml',
        'views/vchasno_document_views.xml',
        'views/dms_vchasno_document.xml',
        'wizard/vchasno_download.xml',
    ],
    'application': True,
    'installable': True,
}
