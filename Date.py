#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2016-2022 Joseph J. Gorak. All rights reserved.
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
    def __init__(self, parent, in_dateFormat, in_payType, in_ref_date):
        self.parent = parent
        self.dateFormat = in_dateFormat
        self.payType = in_payType
        self.ref_date = in_ref_date
        self.set_curr_date()
        self.year, self.month, self.day = self.parse_datestring(self.curr_date)
        self.set_proj_date(self.curr_date)
        self.set_curr_paydate()
        self.set_next_paydate()

    def __lt__(self, other):
        val = __lt__(self.year, other.year)
        if val:
            return val
        val = __lt__(self.month, other.month)
        if val:
            return val
        val = __lt__(self.day, other.day)
        return val

    def __gt__(self, other):
        val = __gt__(self.year, other.year)
        if val:
            return val
        val = __gt__(self.month, other.month)
        if val:
            return val
        val = __gt__(self.day, other.day)
        return val

    def __le__(self, other):
        val = __le__(self.year, other.year)
        if val:
            return val
        val = __le__(self.month, other.month)
        if val:
            return val
        val = __le__(self.day, other.day)
        return val

    def __ge__(self, other):
        val = __ge__(self.year, other.year)
        if val:
            return val
        val = __ge__(self.month, other.month)
        if val:
            return val
        val = __ge__(self.day, other.day)
        return val

    def __eq__(self, other):
        val = __eq__(self.year, other.year)
        if val:
            return val
        val = __eq__(self.month, other.month)
        if val:
            return val
        val = __eq__(self.day, other.day)
        return val

    def __ne__(self, other):
        val = __ne__(self.year, other.year)
        if val:
            return val
        val = __ne__(self.month, other.month)
        if val:
            return val
        val = __ne__(self.day, other.day)
        return val

    def parse_datestring(self, in_date):
        dt = wx.DateTime()  # Uninitialized datetime
        dateFormat2 = self.dateFormat.replace("/","-")
        if dt.ParseFormat(in_date, self.dateFormat) > 0:
            err_stat = "good"
        elif dt.ParseFormat(in_date, dateFormat2) > 0:
            err_stat = "good"
        else:
            err_stat = "bad"
        if err_stat == "bad" or dt.year < 1000:
            return None
        else:
            return {"year": dt.year, "month": dt.month + 1, "day": dt.day}

    def set_curr_date(self):
        self.curr_date = wx.DateTime.Today()
        self.curr_date = self.curr_date.Format(self.dateFormat)

    def set_proj_date(self, proj_date):
        if (proj_date == None):
            self.proj_date = time.localtime(time.time())
        else:
            self.proj_date = proj_date
        self.parsed_proj_date = Date.parse_datestring(self, proj_date)
        self.pay_dates = Date.get_paydates_in_range(self, self.curr_date, self.proj_date)
        print("Pay dates in range %s-%s: %s" % (Date.get_curr_date(self), Date.get_proj_date(self), self.pay_dates))

    def get_pay_incr(self):
        if self.payType == "every  week":
            incr = wx.DateSpan(weeks=1)
        elif self.payType == "every 2 weeks":
            incr = wx.DateSpan(weeks=2)
        elif self.payType == "every month":
            incr = wx.DateSpan(months=1)
        else:
            incr = None
        return incr

    def set_curr_paydate(self):
        if self.ref_date == "":
            return ""
        test_curr_paydate_parsed = self.parse_datestring(self.curr_date)
        test_curr_paydate = wx.DateTime.FromDMY(test_curr_paydate_parsed['day'], test_curr_paydate_parsed['month'] - 1,
                                                test_curr_paydate_parsed['year'])
        ref_date_parsed = self.parse_datestring(self.ref_date)
        ref_date = wx.DateTime.FromDMY(ref_date_parsed['day'], ref_date_parsed['month']-1, ref_date_parsed['year'])
        incr = self.get_pay_incr()
        if incr == None:
            self.MsgBox("Bad pay Type - curr paydate calculations ignored!")
            return
        while ref_date < test_curr_paydate:
            ref_date.Add(incr)
        if ref_date > test_curr_paydate:
            ref_date.Subtract(incr)
        self.curr_paydate = ref_date
        self.curr_paydate = self.curr_paydate.Format(self.dateFormat)
        return self.curr_paydate

    def set_next_paydate(self):
        if self.ref_date == "":
            return ""
        next_paydate = self.curr_paydate
        next_paydate_parsed = self.parse_datestring(next_paydate)
        next_paydate = wx.DateTime.FromDMY(next_paydate_parsed['day'], next_paydate_parsed['month']-1, next_paydate_parsed['year'])
        incr = self.get_pay_incr()
        if incr == None:
            self.MsgBox("Bad pay Type - next paydate calculations ignored!")
            return
        next_paydate.Add(incr)
        self.next_paydate = next_paydate.Format(self.dateFormat)
        return self.next_paydate

    def get_curr_date(self):
        return self.curr_date

    def get_proj_date(self):
        return self.proj_date

    def get_curr_paydate(self):
        if self.ref_date == "":
            self.MsgBox("No pay information entered! Get curr_paydate skipped")
            return
        return self.curr_paydate

    def get_next_paydate(self):
        if self.ref_date == "":
            self.MsgBox("No pay information entered! Get next_paydate skipped")
            return
        return self.next_paydate

    def get_paydates_in_range(self, start_date, end_date):
        if self.ref_date == "":
            self.MsgBox("No pay information entered! get paydates_in_range skipped")
            return
        start_date_parsed = Date.parse_datestring(self, start_date)
        start_date = wx.DateTime.FromDMY(start_date_parsed["day"], start_date_parsed["month"]-1, start_date_parsed["year"])
        end_date_parsed = Date.parse_datestring(self, end_date)
        end_date = wx.DateTime.FromDMY(end_date_parsed["day"], end_date_parsed["month"]-1, end_date_parsed["year"])
        paydates = []
        if end_date < start_date:
            start_date, end_date = end_date, start_date
        incr = Date.get_pay_incr(self)
        if incr == None:
            self.MsgBox("Bad pay Type - get_paydate_in_range calculations ignored!")
            return
        ref_date_parsed = Date.parse_datestring(self, self.ref_date)
        ref_date = wx.DateTime.FromDMY(ref_date_parsed['day'], ref_date_parsed['month']-1, ref_date_parsed['year'])
        if ref_date > start_date:
            while ref_date > start_date:
                ref_date.Subract(incr)
            if ref_date < start_date:
                ref_date.Add(incr)
        elif ref_date < start_date:
            while ref_date < start_date:
                ref_date.Add(incr)
            if ref_date > start_date:
                ref_date.Subtract(incr)
        if ref_date >= start_date and ref_date <= end_date:
            paydates.append(ref_date)
        else:
            ref_date.Add(incr)
        while ref_date <= end_date:
            pay_date = ref_date.Format(self.dateFormat)
            paydates.append(pay_date)
            ref_date.Add(incr)
        return paydates

    def convertDateFormat(self, in_date, in_dateFormat, out_dateFormat):
#        print("In date: %s (using format %s)" % (in_date, in_dateFormat))
        savedFormat = self.dateFormat
        self.dateFormat = in_dateFormat
        in_date_parsed=Date.parse_datestring(self, in_date)
        in_date = wx.DateTime.FromDMY(in_date_parsed['day'], in_date_parsed['month']-1, in_date_parsed['year'])
        out_date = in_date.Format(out_dateFormat)
#        print("Out date: %s (using format %s)" % (out_date, out_dateFormat))
        self.dateFormat = savedFormat
        return out_date

    # Helper method(s):

    def MsgBox(self, message):
        d = wx.MessageDialog(self.parent, message, "error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()

