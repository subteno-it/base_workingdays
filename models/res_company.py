# -*- coding: utf-8 -*-
# Copyright 2012 Syleam
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, rruleset, DAILY, MO, TU, WE, TH, FR, SA, SU
from datetime import datetime
from pytz import utc, timezone


class ResCompany(models.Model):
    _inherit = 'res.company'

    workingday_monday = fields.Boolean(string='Monday', default=True, help='Checked if employees of this company works on monday')
    workingday_tuesday = fields.Boolean(string='Tuesday', default=True, help='Checked if employees of this company works on tuesday')
    workingday_wednesday = fields.Boolean(string='Wednesday', default=True, help='Checked if employees of this company works on wednesday')
    workingday_thursday = fields.Boolean(string='Thursday', default=True, help='Checked if employees of this company works on thursday')
    workingday_friday = fields.Boolean(string='Friday', default=True, help='Checked if employees of this company works on friday')
    workingday_saturday = fields.Boolean(string='Saturday', default=False, help='Checked if employees of this company works on saturday')
    workingday_sunday = fields.Boolean(string='Sunday', default=False, help='Checked if employees of this company works on sunday')
    days_validation_ids = fields.One2many(comodel_name='res.company.day.validation', inverse_name='company_id', string='Days Validation', help='lines of fields to check on write')
    specific_working_date_ids = fields.One2many(comodel_name='res.company.workdate', inverse_name='company_id', string='Specific Working Date', help='list of dates worked, to bypass not worked dates')

    @api.model
    def verify_valid_date(self, date, before=False, delay=0):
        """
        Searches the first available date before or after 'date' argument
        Available dates are checked days, limited to work days from country
        """
        res_country_workdates_obj = self.env['res.country.workdates']

        # Check if the field 'date' is date or datetime format
        if len(date) == 10:
            date = datetime.strptime(date, '%Y-%m-%d')
            is_date = True
        else:
            date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            is_date = False
            # We will calculate datetime based on the timezone of the user if set
            if self.env.context.get('tz'):
                date = utc.localize(date, is_dst=True).astimezone(timezone(self.env.context['tz']))
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

        for company in self:
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
                diff_day = res_country_workdates_obj.not_worked(company.country_id.id, diff_day, dates_list[0], dates_list[-1])

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
                if self.env.context.get('tz'):
                    chosen_day = timezone(self.env.context['tz']).localize(chosen_day, is_dst=True).astimezone(utc)
                valid_dates[company.id] = chosen_day.strftime('%Y-%m-%d %H:%M:%S')

        return valid_dates
