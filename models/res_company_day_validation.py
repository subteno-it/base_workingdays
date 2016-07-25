# -*- coding: utf-8 -*-
##############################################################################
#
#    base_workingdays module for OpenERP, Manage working days
#    Copyright (C) 2016 SYLEAM Info Services (<http://www.syleam.fr>)
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of base_workingdays
#
#    base_workingdays is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    base_workingdays is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _


class res_company_day_validation(osv.osv):
    _name = 'res.company.day.validation'
    _description = 'Lines of objects to verify dates'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', help='Company of this line'),
        'model_id': fields.many2one('ir.model', 'Model', required=True, help='Model of this line'),
        'field_id': fields.many2one('ir.model.fields', 'Field', domain="[('model_id', '=', model_id), ('ttype', 'in', ('date', 'datetime'))]", required=True, help='Field of this line'),
        'before': fields.boolean('Before', help='Check if the computed date must be before the original date'),
    }

    _defaults = {
        'before': False,
    }

    _sql_constraints = [
        ('uniq_model_field', 'unique(company_id, model_id, field_id)', _('The model/field couple must be unique per company !')),
    ]

res_company_day_validation()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
