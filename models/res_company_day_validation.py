# -*- coding: utf-8 -*-
# Copyright 2012 Syleam
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _


class ResCompanyDayValidation(models.Model):
    _name = 'res.company.day.validation'
    _description = 'Lines of objects to verify dates'

    company_id = fields.Many2one(comodel_name='res.company',
                                 string='Company', help='Company of this line')
    model_id = fields.Many2one(comodel_name='ir.model',
                               string='Model', required=True, help='Model of this line')
    field_id = fields.Many2one(comodel_name='ir.model.fields', string='Field',
                               required=True, help='Field of this line')
    before = fields.Boolean(string='Before', help='Check if the computed date must be before the original date')

    _sql_constraints = [
        ('uniq_model_field', 'unique(company_id, model_id, field_id)', _('The model/field couple must be unique per company !')),
    ]
