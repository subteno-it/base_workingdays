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

from openerp import models, fields


class ResCompanyWorkdate(models.Model):
    _name = 'res.company.workdate'
    _description = 'Specific working date'

    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('res.company.workdate'), help='Company for this working date')
    date = fields.Date(string='Date', required=True, help='Specific working date')

    _sql_constraints = [
        ('uniq_date', 'unique(company_id, date)', 'Date must be unique per company !'),
    ]


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
