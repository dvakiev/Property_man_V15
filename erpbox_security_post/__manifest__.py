{
    'name': 'ERPBOX - Security Post',
    'version': '15.0.0.0',
    'depends': [
        'erpbox_property_management',
        'dt_ua_catuttc',
    ],
    'author': 'Dmytro Pavlov <dmitriy.paulov@gmail.com>',
    'data': [
        'security/ir.model.access.csv',
        'views/erpbox_security_post_views.xml',
        'views/res_partner_views.xml',
        'views/menu.xml',
    ],
    'qweb': [

    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
