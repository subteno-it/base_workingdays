# -*- coding: utf-8 -*-
# Copyright 2012 Syleam
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Working Days',
    'version': '10.0.1.1.0',
    'category': 'Hidden/Dependency',
    'complexity': "easy",
    'summary': """
It let you to configure the working days in your company.
After set, Odoo computes the good date depending working days and days not worked (depending country)
Just France is set for the days not worked.
    """,
    'author': 'Syleam',
    'website': 'http://www.syleam.fr/',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company.xml',
    ],
    'installable': True,
    'auto_install': False,
    'active': False,
    'license': 'AGPL-3',
}
