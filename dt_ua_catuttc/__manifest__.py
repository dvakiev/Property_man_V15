# Copyright 2022 DotTek
# @author: Dmytro Pavlov (<dottek.ukraine@gmail.com>)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).
{
    'name' : 'DotTek Ukraine CATUTTC',
    'version': '15.0.0.0.0',
    'category': 'Extra Tools',
    'author': 'Dmytro Pavlov <dottek.ukraine@gmail.com>',
    'maintainer': 'DotTek Ukraine',
    'website': 'https://dottek.co',
    'depends' : [],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/catuttc_category.xml',
        'views/catuttc_category_views.xml',
        'views/catuttc_region_views.xml',
        'views/catuttc_district_views.xml',
        'views/catuttc_community_views.xml',
        'views/catuttc_locality_views.xml',
        'views/catuttc_locality_district_views.xml',
        'views/res_partner_views.xml',
        'views/menu.xml',
    ],
    'price': 50.0,
    'currency': 'USD',
    'license': 'OPL-1',
    'post_init_hook': 'post_init_hook',
    'application': True,
}
