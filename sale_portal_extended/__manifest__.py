{
    'name': 'Sale Portal Extended',
    'version': '16.0.0.0',
    'summary': 'Sale Portal Extended',
    'description': 'Sale Portal Extended',
    'category': 'sale',
    'author': '',
    'website': '',
    'support' : '',
    'maintainer': '',
    'license': 'OPL-1',
    'depends': ["sale_management"],
    'data': [
        'views/portal_template_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'sale_portal_extended/static/src/scss/main.scss',
            'sale_portal_extended/static/src/js/script.js'
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
