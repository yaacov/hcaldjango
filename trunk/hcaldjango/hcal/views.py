#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# Copyright (C) 2012 Yaacov Zamir (2012) <kobi.zamir@gmail.com>
# Author: Yaacov Zamir (2012) <kobi.zamir@gmail.com>

from django.template import Context, loader
from django.http import HttpResponse

from django.utils import translation
from django.utils.translation import ugettext as _

from hcal_wrapper import HcalWrapper
    
def index(request, hyear = 5773, theme = 'images'):
    ''' render a calendar for a year
    
        hyear - the Hebrew year to render 
            (e.g. Hebrew 5773 is Gregorian 2012-2013)
    '''
    
    hyear = int(hyear)
    hcal = HcalWrapper()
    
    # time calculations use the location
    # some useful locations and time zones:
    #    Eilat : 29, 34, 2
    #    Haifa : 32, 34, 2
    #    Jerusalem : 31, 35, 2
    #    Tel Aviv : 32, 34, 2
    #    Ashdod : 31, 34, 2
    #    Beer Sheva : 31, 34, 2
    #    Tiberias : 32, 35, 2
    #    London : 51, 0, 0
    #    Paris : 48, 2, 1
    #    New York : 40, -74, -5
    #    Moscow : 55, 37, 3
    
    # set location for tel aviv
    longitude = 32.08 # N
    latitude = 34.8 # E
    time_zone = 2 # UTC+2
    dst = 1 # DST - daylight saving time
    
    hcal.set_location (longitude, latitude, time_zone + dst)
    
    # set holiday and readings (parasha) for Israel / Diaspory
    hcal.set_israel ()
    #set_diaspora ()
    
    # get Julian for year start
    hcal.set_hdate(1, 1, hyear)
    jd_1_tishrey = hcal.get_julian()
    
    # get header for year calendar,
    #   calculate Gregorian year for 5 be Iyaar)
    hcal.set_hdate(5, 8, hyear)
    gyear = hcal.get_gyear()
    hyear_length = hcal.get_size_of_year()
    
    # significant dates
    mered_gadol = gyear - 70
    israel = gyear - 1948
    jerusalem = gyear - 1967
    
    # set the header
    header = {
        'hyear' : hcal.int_to_str(hcal.get_hyear()), 
        'gyear' : '%d-%d' % (gyear - 1, gyear),
        'mered_gadol' : mered_gadol,
        'israel' : israel,
        'jerusalem' : jerusalem,
        'hebrew_year_length' : hyear_length
    }
    
    # get the weeks in this year's calendar
    weeks = []
    for i in range(0, hyear_length + 7, 7):
        # move calendar to the printing week
        hcal.set_jd(jd_1_tishrey + i)
        days = hcal.week_to_dict()
        
        # add an image for this week header
        image = hcal.get_weeks()
        days['header']['image'] = '/static/%s/%d.png' % (theme, image % 20 + 1)
        
        weeks.append(days)
    
    # render the calendar
    t = loader.get_template('weekly.html')
    c = Context({
        'header' : header,
        'weeks' : weeks,
    })
    
    return HttpResponse(t.render(c))

