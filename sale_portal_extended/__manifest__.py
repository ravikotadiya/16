{
    'name': 'Sale Portal Extended',
    'version': '16.0.0.0',
    'summary': 'Sale Portal Extended',
    'description': 'Sale Portal Extended',
    'category': 'sale',
    'author': '',
    'website': '',
    'support': '',
    'maintainer': '',
    'license': 'OPL-1',
    'depends': ["sale_management"],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_template_view.xml',
        'views/product_pricelist_item_view.xml',
        'views/view_sale_order.xml',
        'wizard/view_wizard_import_sale_order.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_portal_extended/static/src/js/tree_button.js',
            'sale_portal_extended/static/src/xml/sale_template.xml',
        ],
        'web.assets_frontend': [
            'sale_portal_extended/static/src/scss/main.scss',
            'sale_portal_extended/static/src/js/script.js'
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
