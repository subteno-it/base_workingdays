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

from openerp import models, api


#####
# Redefine ORM's create and write method to automatically verify dates on all models
#####

# Save the original create method to call it after
original_orm_create = models.Model.create
# Save the original write method to call it after
original_orm_write = models.Model.write


@api.model
@api.returns('self', lambda value: value.id)
def new_orm_create(self, values):
    """
    New create method for the orm
    Automatically checks for dates before doing the real create
    """
    day_validation_line_obj = self.env['res.company.day.validation']
    res_company_obj = self.env['res.company']
    company_id = 0

    # Retrieve the company of the user
    if self.env.user.company_id:
        company_id = self.env.user.company_id.id

    # If the model has a company_id, get it
    if 'company_id' in values:
        company_id = values['company_id']

    if company_id:
        # Search for validation configurations currently on written fields
        day_validation_line_ids = day_validation_line_obj.search([
            ('company_id', '=', company_id),
            ('model_id.model', '=', self._name),
            ('field_id.name', 'in', values.keys())
        ])
        company = res_company_obj.browse(company_id)
        for line in day_validation_line_ids:
            if values[line.field_id.name]:
                # Verify dates, and adjust if needed
                values[line.field_id.name] = company.verify_valid_date(values[line.field_id.name], before=line.before)[company_id]

    # Call standard behaviour
    return original_orm_create(self, values)


@api.multi
def new_orm_write(self, values):
    """
    New write method for the orm
    Automatically checks for dates before doing the real write
    """
    if not self:
        return True

    day_validation_line_obj = self.env['res.company.day.validation']
    res_company_obj = self.env['res.company']
    company_id = 0

    # Retrieve the company of the user
    if self.env.user.company_id.id:
        company_id = self.env.user.company_id.id

    # If the used model has no company, search for its value
    model_fields = self.fields_get_keys()
    if 'company_id' in values:
        company_id = values['company_id']
    elif 'company_id' in model_fields and 'company_id' not in values:
        self_data = self.read(['company_id'])
        company_ids = dict([(data['id'], data['company_id'] and data['company_id'][0] or company_id) for data in self_data])

    for record in self:
        # Retrieve the good company_id, if necessary
        if 'company_id' in model_fields and 'company_id' not in values:
            company_id = company_ids[record.id]

        if company_id:
            # Search for validation configurations currently on written fields
            day_validation_line_ids = day_validation_line_obj.search([
                ('company_id', '=', company_id),
                ('model_id.model', '=', self._name),
                ('field_id.name', 'in', values.keys())
            ])
            company = res_company_obj.browse(company_id)
            for line in day_validation_line_ids:
                if values[line.field_id.name]:
                    # Verify dates, and adjust if needed
                    values[line.field_id.name] = company.verify_valid_date(values[line.field_id.name], before=line.before)[company_id]

    # Call standard behaviour
    return original_orm_write(self, values)

# Attaches the new create method to the orm
models.Model.create = new_orm_create
# Attaches the new write method to the orm
models.Model.write = new_orm_write

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
