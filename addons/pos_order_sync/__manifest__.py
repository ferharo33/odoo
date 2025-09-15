{
    'name': 'POS Order Sync',
    'version': '1.0',
    'summary': 'Copy POS orders between Odoo instances',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_sync_instance_views.xml',
        'views/pos_sync_log_views.xml',
        'wizards/pos_sync_wizard_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
