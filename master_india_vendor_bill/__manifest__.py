{
    'name': 'Vendor Bill Master India',
    'version': '16.0',
    'category': 'API',
    'author': '',
    'website': '',
    'maintainer': '',
    'depends': ['master_india_connector','account'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': ['static/description/main_screen.jpeg'],
    'assets': {
        'web.assets_backend': [
            'master_india_vendor_bill/static/src/js/**/*',
        ],
    },
    'license': 'LGPL-3',
}
