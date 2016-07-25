# -*- coding: utf-8 -*-
##############################################################################
#
#    base_workingdays module for OpenERP, Manage working days
#    Copyright (C) 2012 SYLEAM Info Services (<http://www.syleam.fr/>)
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#              Sylvain GARANCHER <sylvain.garancher@syleam.fr>
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
from openerp.osv import orm
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, rruleset, DAILY, MO, TU, WE, TH, FR, SA, SU
from datetime import datetime
from pytz import utc, timezone


class res_company(osv.osv):
    _inherit = 'res.company'

    _columns = {
        'workingday_monday': fields.boolean('Monday', help='Checked if employees of this company works on monday'),
        'workingday_tuesday': fields.boolean('Tuesday', help='Checked if employees of this company works on tuesday'),
        'workingday_wednesday': fields.boolean('Wednesday', help='Checked if employees of this company works on wednesday'),
        'workingday_thursday': fields.boolean('Thursday', help='Checked if employees of this company works on thursday'),
        'workingday_friday': fields.boolean('Friday', help='Checked if employees of this company works on friday'),
        'workingday_saturday': fields.boolean('Saturday', help='Checked if employees of this company works on saturday'),
        'workingday_sunday': fields.boolean('Sunday', help='Checked if employees of this company works on sunday'),
        'days_validation_ids': fields.one2many('res.company.day.validation', 'company_id', 'Days Validation', help='Lines of fields to check on write'),
        'specific_working_date_ids': fields.one2many('res.company.workdate', 'company_id', 'Specific Working Date', help='List of dates worked, to bypass not worked dates'),
    }

    _defaults = {
        'workingday_monday': True,
        'workingday_tuesday': True,
        'workingday_wednesday': True,
        'workingday_thursday': True,
        'workingday_friday': True,
        'workingday_saturday': False,
        'workingday_sunday': False,
    }

    def verify_valid_date(self, cr, uid, ids, date, before=False, delay=0, context=None):
        """
        Searches the first available date before or after 'date' argument
        Available dates are checked days, limited to work days from country
        """

        user_obj = self.pool.get('res.users')
        # Get context from user
        ctx = user_obj.context_get(cr, uid)

        res_country_workdates_obj = self.pool.get('res.country.workdates')

        #Check if the field 'date' is date or datetime format
        if len(date) == 10:
            date = datetime.strptime(date, '%Y-%m-%d')
            is_date = True
        else:
            date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            is_date = False
            # We will calculate datetime based on the timezone of the user if set
            if ctx['tz']:
                date = utc.localize(date, is_dst=True).astimezone(timezone(ctx['tz']))
                # Remove TZ in datetime
                date = date.strftime('%Y-%m-%d %H:%M:%S')
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

        # Initialize return value
        valid_dates = {}

        # Search all date between from and to date
        one_year = relativedelta(years=1)
        if before:
            start_date = date - one_year
            end_date = date
        else:
            start_date = date
            end_date = date + one_year

        for company in self.browse(cr, uid, ids, context=context):
            # List available weekdays
            available_weekdays = []
            if company.workingday_monday:
                available_weekdays.append(MO)
            if company.workingday_tuesday:
                available_weekdays.append(TU)
            if company.workingday_wednesday:
                available_weekdays.append(WE)
            if company.workingday_thursday:
                available_weekdays.append(TH)
            if company.workingday_friday:
                available_weekdays.append(FR)
            if company.workingday_saturday:
                available_weekdays.append(SA)
            if company.workingday_sunday:
                available_weekdays.append(SU)

            # List all possible days
            diff_day = rruleset()
            diff_day.rrule(rrule(DAILY, byweekday=available_weekdays, dtstart=start_date, until=end_date))

            # Exclude not worked days from list
            dates_list = list(diff_day)
            # Deletes the not working days for the selected country
            if company.country_id:
                diff_day = res_country_workdates_obj.not_worked(cr, uid, company.country_id.id, diff_day, dates_list[0], dates_list[-1])

            # Add specific dates
            for spec in company.specific_working_date_ids:
                spec_date = datetime.strptime(spec.date, '%Y-%m-%d')
                if start_date <= spec_date and spec_date <= end_date:
                    diff_day.rdate(spec_date)

            # Choose the good day
            diff_day = sorted(list(diff_day))
            chosen_day = diff_day[delay]
            if before:
                chosen_day = diff_day[-1 - delay]

            # Add the chosen day in return dict
            if is_date:
                valid_dates[company.id] = chosen_day.strftime('%Y-%m-%d')
            else:
                # We convert the date without timezone of user
                if ctx['tz']:
                    chosen_day = timezone(ctx['tz']).localize(chosen_day, is_dst=True).astimezone(utc)
                valid_dates[company.id] = chosen_day.strftime('%Y-%m-%d %H:%M:%S')

        return valid_dates

res_company()


class res_company_workdate(osv.osv):
    _name = 'res.company.workdate'
    _description = 'Specific working date'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True, help='Company for this working date'),
        'date': fields.date('Date', required=True, help='Specific working date'),
    }

    _sql_constraints = [
        ('uniq_date', 'unique(company_id, date)', 'Date must be unique per company !'),
    ]

res_company_workdate()


class res_country_workdates(osv.osv):
    _name = 'res.country.workdates'
    _description = 'Working dates by country'

    def fr_datepaques(self, year):
        """
        Find date of Paques
        """
        a = year // 100
        b = year % 100
        c = (3 * (a + 25)) // 4
        d = (3 * (a + 25)) % 4
        e = (8 * (a + 11)) // 25
        f = (5 * a + b) % 19
        g = (19 * f + c - e) % 30
        h = (f + 11 * g) // 319
        j = (60 * (5 - d) + b) // 4
        k = (60 * (5 - d) + b) % 4
        m = (2 * j - k - g + h) % 7
        n = (g - h + m + 114) // 31
        p = (g - h + m + 114) % 31

        day = p + 1
        month = n

        return (year, month, day)

    def fr_not_worked(self, diff_day, date_start, date_end):
        nb_year = date_end.year - date_start.year + 1

        while True:
            if nb_year:
                nb_year -= 1

                # Search day of paques
                paques = self.fr_datepaques(date_end.year - nb_year)
                date_paques = datetime(paques[0], paques[1], paques[2], date_start.hour, date_start.minute, date_start.second)
                # Search monday of paques
                date_paques_monday = date_paques + relativedelta(days=1)
                # Search Thursday of Ascension
                date_ascension = date_paques + relativedelta(days=39)
                # Search monday of pentecote
                date_pentecote_monday = date_paques + relativedelta(days=50)

                # Exclude monday of paques
                diff_day.exdate(date_paques_monday)
                # Exclude monday of pentecote
                diff_day.exdate(date_pentecote_monday)
                # Exclude thursday of ascension
                diff_day.exdate(date_ascension)
                # Exclude new year
                diff_day.exdate(datetime(date_end.year - nb_year, 1, 1, date_start.hour, date_start.minute, date_start.second))
                # Exclude fete du travail
                diff_day.exdate(datetime(date_end.year - nb_year, 5, 1, date_start.hour, date_start.minute, date_start.second))
                # Exclude victoire 1945
                diff_day.exdate(datetime(date_end.year - nb_year, 5, 8, date_start.hour, date_start.minute, date_start.second))
                # Exclude fete nationale
                diff_day.exdate(datetime(date_end.year - nb_year, 7, 14, date_start.hour, date_start.minute, date_start.second))
                # Exclude Assomption
                diff_day.exdate(datetime(date_end.year - nb_year, 8, 15, date_start.hour, date_start.minute, date_start.second))
                # Exclude Toussaint
                diff_day.exdate(datetime(date_end.year - nb_year, 11, 1, date_start.hour, date_start.minute, date_start.second))
                # Exclude Armistice 1918
                diff_day.exdate(datetime(date_end.year - nb_year, 11, 11, date_start.hour, date_start.minute, date_start.second))
                # Exclude Noel
                diff_day.exdate(datetime(date_end.year - nb_year, 12, 25, date_start.hour, date_start.minute, date_start.second))
            else:
                break

        return diff_day

    def not_worked(self, cr, uid, country_id, diff_day, date_start, date_end, context=None):
        ir_model_data_obj = self.pool.get('ir.model.data')

        # Search the id.model.data for selected country
        ir_model_data_ids = ir_model_data_obj.search(cr, uid, [('res_id', '=', country_id), ('model', '=', 'res.country')], context=context)
        if ir_model_data_ids:
            # If a country was found, call the good method
            country_xml_id = ir_model_data_obj.browse(cr, uid, ir_model_data_ids, context=context)[0]
            country_xml_id = '%s.%s' % (country_xml_id.module, country_xml_id.name)

            # Compute french not working days
            if country_xml_id == 'base.fr':
                diff_day = self.fr_not_worked(diff_day, date_start, date_end)

        return diff_day

res_country_workdates()


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

#####
# Redefine ORM's create and write method to automatically verify dates on all models
#####

# Save the original create method to call it after
original_orm_create = orm.BaseModel.create
# Save the original write method to call it after
original_orm_write = orm.BaseModel.write


def new_orm_create(self, cr, uid, values, context=None):
    """
    New create method for the orm
    Automatically checks for dates before doing the real create
    """
    day_validation_line_obj = self.pool.get('res.company.day.validation')
    res_company_obj = self.pool.get('res.company')
    company_id = 0

    # Retrieve the company of the user
    user = self.pool.get('res.users').read(cr, uid, uid, ['company_id'], context=context)
    if user['company_id']:
        company_id = user['company_id'][0]

    # If the model has a company_id, get it
    if 'company_id' in values:
        company_id = values['company_id']

    if company_id:
        # Search for validation configurations currently on written fields
        day_validation_line_ids = day_validation_line_obj.search(cr, uid, [
            ('company_id', '=', company_id),
            ('model_id.model', '=', self._name),
            ('field_id.name', 'in', values.keys())], context=context)
        for line in day_validation_line_obj.browse(cr, uid, day_validation_line_ids, context=context):
            if values[line.field_id.name]:
                # Verify dates, and adjust if needed
                values[line.field_id.name] = res_company_obj.verify_valid_date(cr, uid, [company_id], values[line.field_id.name], before=line.before, context=None)[company_id]

    # Call standard behaviour
    return original_orm_create(self, cr, uid, values, context=context)


def new_orm_write(self, cr, uid, ids, values, context=None):
    """
    New write method for the orm
    Automatically checks for dates before doing the real write
    """
    day_validation_line_obj = self.pool.get('res.company.day.validation')
    res_company_obj = self.pool.get('res.company')
    company_id = 0

    # Assert ids is a list
    if not isinstance(ids, list):
        ids = [ids]

    # Retrieve the company of the user
    user = self.pool.get('res.users').read(cr, uid, uid, ['company_id'], context=context)
    if user['company_id']:
        company_id = user['company_id'][0]

    # If the used model has no company, search for its value
    model_fields = self.fields_get_keys(cr, uid, context=context)
    if 'company_id' in values:
        company_id = values['company_id']
    elif 'company_id' in model_fields and not 'company_id' in values:
        self_data = self.read(cr, uid, ids, ['company_id'], context=context)
        company_ids = dict([(data['id'], data['company_id'] and data['company_id'][0] or company_id) for data in self_data])

    for id in ids:
        # Retrieve the good company_id, if necessary
        if 'company_id' in model_fields and not 'company_id' in values:
            company_id = company_ids[id]

        if company_id:
            # Search for validation configurations currently on written fields
            day_validation_line_ids = day_validation_line_obj.search(cr, uid, [
                ('company_id', '=', company_id),
                ('model_id.model', '=', self._name),
                ('field_id.name', 'in', values.keys())
            ], context=context)
            for line in day_validation_line_obj.browse(cr, uid, day_validation_line_ids, context=context):
                if values[line.field_id.name]:
                    # Verify dates, and adjust if needed
                    values[line.field_id.name] = res_company_obj.verify_valid_date(cr, uid, [company_id], values[line.field_id.name], before=line.before, context=None)[company_id]

    # Call standard behaviour
    return original_orm_write(self, cr, uid, ids, values, context=context)

# Attaches the new create method to the orm
orm.BaseModel.create = new_orm_create
# Attaches the new write method to the orm
orm.BaseModel.write = new_orm_write




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
