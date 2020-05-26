#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2016,2020 Joseph J. Gorak. All rights reserved.
This code is in development -- use at your own risk. Email
comments, patches, complaints to joe.gorak@gmail.com

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""

#  Version information
#  6/11/2016     Initial version v0.1

# To Do list:
# Use time module functions to parse dates
# Plot balance vs day
# Search functions
# goto date

import wx
import time

class Date:
    def __init__(self, curr_date=None):
        self.set_curr_date(curr_date)
        self.set_proj_date(curr_date)
        self.set_last_paydate(curr_date)
        self.set_next_paydate(curr_date)

    def __cmp__(self, other):
        val = cmp(self.year, other.year)
        if val:
            return val
        val = cmp(self.month, other.month)
        if val:
            return val
        val = cmp(self.day, other.day)
        return val

    def __str__(self):
        return self.formatUS()

    def formatUS(self):
        return "%02d/%02d/%04d" % (self.month, self.day, self.year)

    def parse_datestring(self, in_date):
        dt = wx.DateTime()  # Uninitialized datetime
        if dt.ParseFormat(in_date, "%m-%d-%Y") > 0:
            err_stat = "good"
        elif dt.ParseFormat(in_date, "%m/%d/%Y") > 0:
            err_stat = "good"
        else:
            err_stat = "bad"
        if err_stat == "bad" or dt.year < 1000:
            return None
        else:
            return {"year": dt.year, "month": dt.month + 1, "day": dt.day}

    def set_curr_date(self, curr_date):
        if (curr_date == None):
            self.curr_date = time.localtime(time.time())
            self.year = self.curr_date[0]
            self.month = self.curr_date[1]
            self.day = self.curr_date[2]
        else:
            self.curr_date = curr_date
            self.parse_datestring(curr_date)
        return print(self.curr_date)

    def set_proj_date(self, proj_date):
        if (proj_date == None):
            self.proj_date = time.localtime(time.time())
            self.year = self.proj_date[0]
            self.month = self.proj_date[1]
            self.day = self.proj_date[2]
        else:
            self.proj_date = proj_date
            self.parse_datestring(proj_date)

    def set_last_paydate(self, last_paydate):
        if (last_paydate == None):
            self.last_paydate = time.localtime(time.time())
            self.year = self.last_paydate[0]
            self.month = self.last_paydate[1]
            self.day = self.last_paydate[2]
        else:
            self.last_paydate = last_paydate
            self.parse_datestring(last_paydate)

    def set_next_paydate(self, next_paydate):
        if (next_paydate == None):
            self.next_paydate = time.localtime(time.time())
            self.year = self.next_paydate[0]
            self.month = self.next_paydate[1]
            self.day = self.next_paydate[2]
        else:
            self.next_paydate = next_paydate
            self.parse_datestring(next_paydate)

    def get_curr_date(self):
        return self.curr_date

    def get_proj_date(self):
        return self.proj_date

    def get_last_paydate(self):
        return self.last_paydate

    def get_next_paydate(self):
        return self.next_paydate