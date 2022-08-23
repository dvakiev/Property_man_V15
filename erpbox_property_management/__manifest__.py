{
    'name': 'ERPBOX - Property Management',
    'version': '15.0.0.0',
    'depends': [
        'crm',
        'fims_property_management_system',
        'erpbox_analytic_contract',
        'account_analytic_parent',
        'kw_document_template',
    ],
    'author': 'Dmytro Pavlov <dmitriy.paulov@gmail.com>',
    'data': [
        'data/ir_cron_data.xml',
        'data/crm_stage_data.xml',
        'views/crm_lead_views.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
        'views/tenant_details_views.xml',
        'views/property_details_views.xml',
    ],
    'qweb': [

    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
