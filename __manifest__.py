# -*- encoding: utf-8 -*-

{
    'name': 'Sale Import',
    'author': 'Kareem Abuzaid',
    'version': '12.0.1.0',
    'depends': ['base', 'sale'],
    'data': [
        'data/ir.cron.xml'
    ],
    'application': True,
    'external_dependencies': {
                    'python': ['io'],
                }
}