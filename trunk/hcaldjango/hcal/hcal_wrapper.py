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

from django.utils.translation import gettext as _
from hdate import Hdate

class HcalWrapper(Hdate):
    ''' a thin wrapper around the libhdate Hdate class
    
        it adds -
            int_to_str : an independent function for Hebrew numbers (*)
            
            min_to_str : converts libhdate time to human readable HH:MM string
            
            date_to_dict : converts the date to a dictionary, with information
            useful for printing the date in a calendar
            
            week_to_dict : creates a dictionary for printing a week
            in the calendar, it has a header and 7 days
            
            month_to_dict : creates a dictionary for printing a month
            in the calendar, it has a header and 7 * 6 days
            
        (*) the libhdate internal Hebrew numbers function is using
            libhdate localization and we want to use django's
    '''
    
    def __init__(self):
        ''' init the wrapper class
        '''
        
        Hdate.__init__(self)
        
        # shabat and holiday starts 20 minutes before sunset
        self.min_to_candlelight = 20
        
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
        
        # tel aviv location
        self.longitude = 32.08 # N
        self.latitude = 34.8 # E
        self.time_zone = 3 # UTC+2 + DST+1
        
        self.set_location (self.longitude, self.latitude, self.time_zone)
        
    def int_to_str(self, n):
        ''' convert numbers to Hebrew number strings
        
            work the same way as libhdate internal function,
            but use django localization system
        '''
        
        # return the number without conversion if we
        # do not use Hebrew numbers translation
        if _('USE_HEB_NUMBERS') != 'TRUE':
            return "%d" % n
        
        # copy of the libhdate number to string functionality
        h_number = ""
        digits = [
            [" ", "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט"],
            ["ט", "י", "כ", "ל", "מ", "נ", "ס", "ע", "פ", "צ"],
            [" ", "ק", "ר", "ש", "ת"],
        ]
        
        # sanity checks
        if n < 1 or n > 10000:
            return None
        
        if n >= 1000:
            h_number += digits[0][n / 1000]
            n %= 1000
            
        while n >= 400:
            h_number += digits[2][4]
            n -= 400
        
        if n >= 100:
            h_number += digits[2][n / 100]
            n %= 100
        
        if n >= 10:
            if n == 15 or n == 16:
                n -= 9
            h_number += digits[1][n / 10]
            n %= 10
        
        if n > 0:
            h_number += digits[0][n]

        # add " to the he Hebrew number string
        h_number = h_number.decode('utf-8')
        length = len(h_number);
        
        if length > 2:
            h_number = h_number[0:-1] + '"' + h_number[-1]
        
        return h_number.encode('utf-8')
    
    def min_to_str(self, m):
        ''' converts libhdate time, minutes since midnight, to %H:%M format
        '''
        
        hour = m / 60
        minute = m % 60
        
        return "%02d:%02d" % (hour, minute)
    
    def date_to_dict(self):
        ''' converts the date to a dictionary, with information
            useful for printing the date in a calendar
            
            Notice: this function changes the date of this object
        '''
        
        output = {}
        
        # libhdate 1.6 - 1.8 python bindings 
        # have a bug with day of the week strings
        day_strings = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        
        # get Gregorian date
        # day_fo_week - 1 .. 7 => Sunday .. Saturday
        output['gdate'] = {
            'day' : self.get_gday(), 
            'month' : self.get_gmonth(),
            'month_str' : self.get_month_string(False), 
            'year' : self.get_gyear(), 
            'day_of_week' : self.get_day_of_the_week(),
            'day_of_week_str' : _(day_strings[self.get_day_of_the_week() - 1]),}
        
        # get Hebrew date
        output['hdate'] = {
            'day' : self.int_to_str(self.get_hday()), 
            'day_num' : self.get_hday(), 
            'month' : self.get_hmonth(),
            'month_str' : _(self.get_hebrew_month_string(False)), 
            'year' : self.int_to_str(self.get_hyear()),}
        
        # check for sfirat ha omer
        output['omer'] = {
            'is_omer' : self.get_omer_day() != 0,
            'number' : self.int_to_str(self.get_omer_day()),}
        
        # check for holiday
        # type:
        #   1 yom tov
        #   2 erev yom kipor
        #   3 chol hamoed
        #   4 hanuka ans purim
        #   5 tzom
        #   6 .. 9 other holidays
        output['holiday'] = {
            'type' : self.get_holyday_type(), 
            'title' : _(self.get_holyday_string(False) or 'None'),}
        
        # check for parash
        output['parasha'] = {
            'is_parasha' : self.get_parasha_string(False),
            'title' : _(self.get_parasha_string(False) or 'None'),}
        
        # get day times
        output['times'] = {
            'sunrise' : self.min_to_str(self.get_sunrise()),
            'sunset' : self.min_to_str(self.get_sunset()),
            
            'candlelight' : self.min_to_str(self.get_sunset() - self.min_to_candlelight),
            'three_stars' : self.min_to_str(self.get_three_stars()),}
        
        # add class of day
        day_clases = []
        if output['hdate']['day_num'] == 1:
            day_clases.append('rosh_hodesh')
        if output['holiday']['type'] == 1:
            day_clases.append('yom_tov')
        if output['holiday']['type'] == 5:
            day_clases.append('tzom')
        if output['holiday']['type'] in [3, 4]:
            day_clases.append('chol_hamoed')
        if output['gdate']['day_of_week'] == 6:
            day_clases.append('shishi')
        if output['gdate']['day_of_week'] == 7:
            day_clases.append('shabat')
        
        output['class'] = " ".join(day_clases)
        
        # check for hag
        output['is_hag'] = (self.get_holyday_type() == 1)
        
        # check for erev hag
        jd = self.get_julian()
        self.set_jd(jd + 1)
        output['is_erev_hag'] = (self.get_holyday_type() == 1)
        
        return output
    
    def week_to_dict(self):
        ''' creates a dictionary for printing a week
            in the calendar, it has a header and 7 days
            
            Notice: this function changes the date of this object
        '''
        
        return self._days_to_dict(7)
    
    def month_to_dict(self):
        ''' creates a dictionary for printing a month
            in the calendar, it has a header and 7 * 6 days
            
            Notice: this function changes the date of this object
        '''
        
        return self._days_to_dict(6 * 7)
    
    def _days_to_dict(self, number_of_days = 7):
        ''' creates a dictionary for printing day span
            in the calendar, it has a header and N days
            
            Notice: this function changes the date of this object
        '''
        
        # get the Julian for Sunday
        dow = self.get_day_of_the_week() - 1
        jd = self.get_julian() - dow
        
        # get all the days from Sunday untill Saturday
        days = []
        for i in range(jd, jd + number_of_days):
            self.set_jd(i)
            days.append(self.date_to_dict())
        
        # get the week's header
        header = {}
        
        # check if this week spans two Gregorian years 
        if days[0]['gdate']['year'] == days[-1]['gdate']['year']:
           header['gyear'] = "%d" % days[0]['gdate']['year']
        else:
            header['gyear'] = "%d-%d" % (
                days[0]['gdate']['year'], days[-1]['gdate']['year'])
        
        # check if this week spans two Gregorian months 
        if days[0]['gdate']['month'] == days[-1]['gdate']['month']:
           header['gmonth'] = days[0]['gdate']['month_str']
        else:
            header['gmonth'] = "%s-%s" % (
                days[0]['gdate']['month_str'], days[-1]['gdate']['month_str'])
        
        # check if this week spans two Hebrew years 
        if days[0]['hdate']['year'] == days[-1]['hdate']['year']:
           header['hyear'] = "%s" % days[0]['hdate']['year']
        else:
            header['hyear'] = "%s-%s" % (
                days[0]['hdate']['year'], days[-1]['hdate']['year'])
        
        # check if this week spans two Hebrew months 
        if days[0]['hdate']['month'] == days[-1]['hdate']['month']:
           header['hmonth'] = days[0]['hdate']['month_str']
        else:
            header['hmonth'] = "%s-%s" % (
                days[0]['hdate']['month_str'], days[-1]['hdate']['month_str'])
                
        return {'header' : header, 'days' : days}

