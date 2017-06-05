# -*- coding: utf-8 -*-
# Copyright 2012 Syleam
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, _


class ResCompanyWorkdate(models.Model):
    _name = 'res.company.workdate'
    _description = 'Specific working date'

    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('res.company.workdate'),
                                 help='Company for this working date')
    date = fields.Date(string='Date', required=True, help='Specific working date')

    _sql_constraints = [
        ('uniq_date', 'unique(company_id, date)', _('Date must be unique per company !')),
    ]
