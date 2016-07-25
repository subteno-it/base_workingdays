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


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
