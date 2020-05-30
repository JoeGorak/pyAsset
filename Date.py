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
    def __init__(self, parent, in_payType, in_ref_date, in_netpay):
        self.parent = parent
        self.payType = in_payType
        self.ref_date = in_ref_date
        self.netpay = in_netpay
        curr_date = self.set_curr_date()
        self.set_proj_date(curr_date)
        self.set_curr_paydate()
        self.set_next_paydate()

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
        dateStr = "%02d/%02d/%04d" % (self.month, self.day, self.year)
        return dateStr

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

    def set_curr_date(self):
        curr = time.localtime(time.time())
        dateStr = "%02d/%02d/%04d" % (curr.tm_mon, curr.tm_mday, curr.tm_year)
        self.curr_date = dateStr
        self.year = curr.tm_year
        self.month = curr.tm_mon
        self.day = curr.tm_mday
        return self.curr_date

    def set_proj_date(self, proj_date):
        if (proj_date == None):
            self.proj_date = time.localtime(time.time())
            self.year = self.proj_date[0]
            self.month = self.proj_date[1]
            self.day = self.proj_date[2]
        else:
            self.proj_date = proj_date
 #           self.parse_datestring(proj_date)

    def set_curr_paydate(self):
        self.curr_paydate = ""
        test_curr_paydate = wx.DateTime.FromDMY(self.day, self.month-1, self.year)
        ref_date_parsed = self.parse_datestring(self.ref_date)
        ref_date = wx.DateTime.FromDMY(ref_date_parsed['day'], ref_date_parsed['month']-1, ref_date_parsed['year'])
        print("In Date - set_curr_paydate: ref_Date %s, test_curr_paydate %s" % (ref_date, test_curr_paydate))
        if self.payType == 0:
            incr = wx.DateSpan(weeks=1)
        elif self.payType == 1:
            incr = wx.DateSpan(weeks=2)
        elif self.payType == 2:
            incr = wx.DateSpan(months=1)
        else:
            self.MsgBox("Bad pay Type - paydate calculations ignored!")
            return
        while ref_date < test_curr_paydate:
            ref_date.Add(incr)
        if test_curr_paydate < ref_date:
            while test_curr_paydate < ref_date:
                test_curr_paydate.Add(incr)
        elif test_curr_paydate > ref_date:
            while test_curr_paydate > ref_date:
                test_curr_paydate.Subtract(incr)
        self.curr_paydate = str(test_curr_paydate).split(' ')[0]

    def set_next_paydate(self):
        next_paydate_parsed = self.parse_datestring(self.curr_paydate)
        next_paydate = wx.DateTime.FromDMY(next_paydate_parsed['day'], next_paydate_parsed['month']-1, next_paydate_parsed['year'])
        if self.payType == 0:
            incr = wx.DateSpan(weeks=1)
        elif self.payType == 1:
            incr = wx.DateSpan(weeks=2)
        elif self.payType == 2:
            incr = wx.DateSpan(months=1)
        else:
            self.MsgBox("Bad pay Type - paydate calculations ignored!")
            return
        next_paydate.Add(incr)
        self.next_paydate = str(next_paydate).split(' ')[0]
        return self.next_paydate

    def get_next_paydate(self):
        return self.next_paydate

    def get_curr_date(self):
        return self.curr_date

    def get_proj_date(self):
        return self.proj_date

    def get_curr_paydate(self):
        return self.curr_paydate

    def get_next_paydate(self):
        return self.next_paydate

    # Helper method(s):

    def MsgBox(self, message):
        d = wx.MessageDialog(self, message, "error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()

