# -*- coding: utf-8 -*-
# Copyright 2012 Syleam
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
from dateutil.rrule import rrule, MINUTELY


class ResCountryWorkdates(models.Model):
    _name = 'res.country.workdates'
    _description = 'Working dates by country'

    @api.model
    def fr_not_worked(self, diff_day):
        # Exclude new year
        diff_day.exrule(rrule(MINUTELY, bymonth=1, bymonthday=1, bysecond=0))
        # Exclude fete du travail
        diff_day.exrule(rrule(MINUTELY, bymonth=5, bymonthday=1, bysecond=0))
        # Exclude victoire 1945
        diff_day.exrule(rrule(MINUTELY, bymonth=5, bymonthday=8, bysecond=0))
        # Exclude fete nationale
        diff_day.exrule(rrule(MINUTELY, bymonth=7, bymonthday=14, bysecond=0))
        # Exclude Assomption
        diff_day.exrule(rrule(MINUTELY, bymonth=8, bymonthday=15, bysecond=0))
        # Exclude Toussaint
        diff_day.exrule(rrule(MINUTELY, bymonth=11, bymonthday=1, bysecond=0))
        # Exclude Armistice 1918
        diff_day.exrule(rrule(MINUTELY, bymonth=11, bymonthday=11, bysecond=0))
        # Exclude Noel
        diff_day.exrule(rrule(MINUTELY, bymonth=12, bymonthday=25, bysecond=0))
        # Exclude paques
        diff_day.exrule(rrule(MINUTELY, byeaster=0, bysecond=0))
        # Exclude monday of paques
        diff_day.exrule(rrule(MINUTELY, byeaster=1, bysecond=0))
        # Exclude monday of pentecote
        diff_day.exrule(rrule(MINUTELY, byeaster=39, bysecond=0))
        # Exclude thursday of ascension
        diff_day.exrule(rrule(MINUTELY, byeaster=50, bysecond=0))
        return diff_day

    @api.model
    def not_worked(self, country_id, diff_day, date_start, date_end):
        if country_id == self.env.ref('base.fr').id:
            diff_day = self.fr_not_worked(diff_day)
        return diff_day
