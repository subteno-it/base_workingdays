# -*- coding: utf-8 -*-
# Copyright 2012 Syleam
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


#####
# Redefine ORM's create and write method to automatically verify dates on all models
#####

# Save the original create method to call it after
original_create = models.BaseModel.create
# Save the original write method to call it after
original_write = models.BaseModel.write


@api.model
@api.returns('self', lambda value: value.id)
def new_create(self, vals):
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
    if 'company_id' in vals:
        company_id = vals['company_id']

    if company_id:
        # Search for validation configurations currently on written fields
        day_validation_line_ids = day_validation_line_obj.search([
            ('company_id', '=', company_id),
            ('model_id.model', '=', self._name),
            ('field_id.name', 'in', vals.keys())
        ])
        company = res_company_obj.browse(company_id)
        for line in day_validation_line_ids:
            if vals[line.field_id.name]:
                # Verify dates, and adjust if needed
                vals[line.field_id.name] = company.verify_valid_date(vals[line.field_id.name], before=line.before)[company_id]

    # Call standard behaviour
    return original_create(self, vals)


@api.multi
def new_write(self, vals):
    """
    New write method for the orm
    Automatically checks for dates before doing the real write
    """
    if not self:
        return True

    if self._table != 'ir_module_module':
        day_validation_line_obj = self.env['res.company.day.validation']
        res_company_obj = self.env['res.company']
        company_id = 0

        # Retrieve the company of the user
        if self.env.user.company_id.id:
            company_id = self.env.user.company_id.id

        # If the used model has no company, search for its value
        model_fields = self.fields_get_keys()
        if 'company_id' in vals:
            company_id = vals['company_id']
        elif 'company_id' in model_fields and 'company_id' not in vals:
            self_data = self.read(['company_id'])
            company_ids = dict([(data['id'], data['company_id'] and data['company_id'][0] or company_id) for data in self_data])

        for record in self:
            # Retrieve the good company_id, if necessary
            if 'company_id' in model_fields and 'company_id' not in vals:
                company_id = company_ids[record.id]

            if company_id:
                # Search for validation configurations currently on written fields
                day_validation_line_ids = day_validation_line_obj.search([
                    ('company_id', '=', company_id),
                    ('model_id.model', '=', self._name),
                    ('field_id.name', 'in', vals.keys())
                ])
                company = res_company_obj.browse(company_id)
                for line in day_validation_line_ids:
                    if vals[line.field_id.name]:
                        # Verify dates, and adjust if needed
                        vals[line.field_id.name] = company.verify_valid_date(vals[line.field_id.name], before=line.before)[company_id]

    # Call standard behaviour
    return original_write(self, vals)

# Attaches the new create method to the orm
models.BaseModel.create = new_create
# Attaches the new write method to the orm
models.BaseModel.write = new_write
