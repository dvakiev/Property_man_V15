{
    'name': 'Car Partner',
    'version': '15.0.0.0.1',
    'license': 'OPL-1',
    'category': 'Technical Settings',

    'summary': 'Integration catalog auto with partner',

    'author': 'Irina Roskolup',

    'depends': [
        'catalog_auto', 'contacts',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/car_state_number.xml',
        'views/car_with_state_number.xml',
        'views/res_partner.xml',

    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}