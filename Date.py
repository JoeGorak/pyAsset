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
#  06/11/2016     Initial version v0.1
#  07/04/2021     Added error checking to parse_date
#  08/07/2021     Version v0.2

# To Do list:
# Plot balance vs day
# Search functions
# goto date

import wx
import re

from wx.core import DateTime

class Date:
    global_date_format = None
    global_date_sep = None
    global_curr_date = { "dt": None, "str": "" }
    global_proj_date = None
    global_curr_paydate = None
    global_next_paydate = None

    def __init__(self, parent, in_dateFormat, in_payType, in_ref_date):
        self.set_global_date_format(in_dateFormat)
        self.parent = parent
        self.dateFormat = in_dateFormat
        self.payType = in_payType
        self.ref_date = in_ref_date
        self.curr_date = self.set_curr_date()
        self.proj_date = self.set_proj_date(self.curr_date["str"])
        self.set_global_proj_date(self.proj_date)
        Date.set_curr_paydate(self)
        Date.set_next_paydate(self)
        Date.set_global_curr_date(self, self.get_curr_date())
        Date.set_global_proj_date(self, self.get_proj_date())
        Date.set_global_date_format(self, self.dateFormat)

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

    def get_date_fields(self, in_date):
        month = 0
        day = 0
        year = 0
        date_sep = Date.get_global_date_sep(self)
        date_fields = self.dateFormat.split(date_sep)
        m = re.match("^[\d]{2,4}([/-])[\d]{1,2}([/-\'])[\d]{2,4}$", in_date)        # JJG 1/9/2022 Added ' to second date separator to handle Quicken .QIF files!
        if m:
            sep = m.groups()
            pos1 = in_date.index(sep[0])
            pos2 = in_date.rindex(sep[1])
            in_fields = []
            in_fields.append(int(in_date[0:pos1]))
            in_fields.append(int(in_date[pos1+1:pos2]))
            in_fields.append(int(in_date[pos2+1:]))
            if len(date_fields) == 3:
                for i in range(3):
                    if date_fields[i] == "%m":
                        month = int(in_fields[i])
                    elif date_fields[i] == "%d":
                        day = int(in_fields[i])
                    elif date_fields[i] == "%Y":
                        year = int(in_fields[i])
                    elif date_fields[i] == "%y":
                        # assume all 2 digit years are in the range 2000 <= year < 2099.  Don't expect this software to be used in the year 2100!! JJG 07/08/2021
                        year = 2000 + int(in_field[i])
                returnVal = [ year, month, day ]
            else:
                returnVal = None                  # Shouldn't happen if properties correct but be defensive! Trust but verify!!        
        else:
            returnVal = None
        return returnVal

    def parse_date(self, in_date, in_date_format):
        error = False
        self.retVal = None
        if type(in_date) is str:
            if in_date == "":
                dt = wx.DateTime.Today()
            else:
                dt = wx.DateTime()  # Uninitialized datetime
                in_date = in_date + " 12:00:00 PM"           # append a valid time so parse will succeed if we have a valid date! JJG 08/04/2021
                if dt.ParseFormat(in_date, in_date_format) == -1:
                    error = True
        elif type(in_date) is DateTime:
            dt = in_date
        elif type(in_date) is Date or type(in_date) is dict:
            dt = in_date["dt"]
        else:
            error = True
        if error:
            pass                                # Leave error message display to the caller!  We just return None!
            #self.MsgBox("Bad input date (%s) in Date.parse_date - ignored!" % (str(in_date)))
        else:
            self.retVal = { "year": dt.year, "month": dt.month + 1, "day": dt.day, "dt": dt }
        return self.retVal

    def set_curr_date(self):
        curr_date = wx.DateTime.Today()
        retVal = { "dt": curr_date, "str": curr_date.Format(self.dateFormat) }
        self.curr_date = retVal
        return retVal

    def set_proj_date(self, proj_date):
        error = False
        self.proj_date = ""
        if type(proj_date) is str:
            if (proj_date != ""):
                self.proj_date = proj_date
            self.parsed_proj_date = Date.parse_date(self, proj_date, self.dateFormat)
            if self.parsed_proj_date == None:
                error = True
            else:
                proj_date_in = wx.DateTime.FromDMY(self.parsed_proj_date['day'], self.parsed_proj_date['month']-1, self.parsed_proj_date['year'])
                self.proj_date = proj_date_in.Format(self.dateFormat)
        elif type(proj_date) is dict:
            self.proj_date = proj_date["str"].Format(self.dateFormat)
        else:
            error = True
        if error:
            self.MsgBox("Bad projected date (%s) - ignored!" % (str(proj_date)))
        else:
            self.pay_dates = Date.get_paydates_in_range(self, self.curr_date, self.proj_date)
            print("Pay dates in range %s-%s: %s" % (self.curr_date["str"], self.proj_date, self.pay_dates))
            retVal = self.proj_date
            #TO DO: Add logic to update Salary transactions for pay_dates
        Date.set_global_proj_date(self, retVal)
        return retVal

    def get_pay_incr(self):
        if self.payType == "every week":
            incr = wx.DateSpan(weeks=1)
        elif self.payType == "every 2 weeks":
            incr = wx.DateSpan(weeks=2)
        elif self.payType == "every month":
            incr = wx.DateSpan(months=1)
        else:
            incr = None
        return incr

    def set_curr_paydate(self):
        retVal = ""
        if self.ref_date == None:
            self.MsgBox("Reference pay date not found - curr paydate calculations ignored!")
        else:
            test_curr_paydate = Date.get_curr_date(self)["dt"]
            while test_curr_paydate != None and type(test_curr_paydate) != DateTime:
                test_curr_paydate =  test_curr_paydate["dt"]
            if type(self.ref_date) is DateTime:
                ref_date = self.ref_date
            else:
                ref_date = Date.convertDateFormat(self, self.ref_date, self.dateFormat, self.dateFormat)["dt"]
            incr = Date.get_pay_incr(self)
            if incr == None:
                self.MsgBox("Bad pay Type - curr paydate calculations ignored!")
            else:
                while ref_date < test_curr_paydate:
                    ref_date.Add(incr)
                if ref_date > test_curr_paydate:
                    ref_date.Subtract(incr)
                self.curr_paydate = ref_date.Format(self.dateFormat)
                retVal = self.curr_paydate
        Date.global_curr_paydate = retVal
        return retVal

    def set_next_paydate(self):
        retVal = ""
        if self.ref_date == None:
            self.MsgBox("Reference pay date not found - curr paydate calculations ignored!")
        else:
            next_paydate = self.curr_paydate
            next_paydate = Date.convertDateFormat(self, next_paydate, self.dateFormat, self.dateFormat)["dt"]
            incr = Date.get_pay_incr(self)
            if incr == None:
                self.MsgBox("Bad pay Type - next paydate calculations ignored!")
            else:
                next_paydate.Add(incr)
                self.next_paydate = next_paydate.Format(self.dateFormat)
                retVal = self.next_paydate
        Date.global_next_paydate = retVal
        return retVal

    def get_date_format(self):
        return self.dateFormat

    def get_curr_date(self):
        return Date.global_curr_date

    def get_proj_date(self):
        return Date.global_proj_date

    def get_curr_paydate(self):
        retVal = None
        if self.ref_date == "":
            self.MsgBox("No pay information entered! Get curr_paydate skipped")
        else:
            retVal = Date.global_curr_paydate
        return retVal

    def get_next_paydate(self):
        retVal = None
        if self.ref_date == "":
            self.MsgBox("No pay information entered! Get next_paydate skipped")
            return
        else:
            retVal = Date.global_next_paydate
        return retVal

    def get_paydates_in_range(self, start_date, end_date):
        paydates = None
        dateFormat = Date.get_global_date_format(self)
        if self.ref_date == None:
            self.MsgBox("No pay information entered! get paydates_in_range skipped")
        else:
            start_date_parsed = Date.parse_date(self, start_date["dt"], dateFormat)
            if start_date_parsed == None:
                self.MsgBox("Can't parse start date (%s) - ignored!" % (start_date))
            else:
                start_date = wx.DateTime.FromDMY(start_date_parsed["day"], start_date_parsed["month"]-1, start_date_parsed["year"])
                end_date_parsed = Date.parse_date(self, end_date, dateFormat)
                if end_date_parsed == None:
                    self.MsgBox("Can't parse end date (%s) - ignored!" % (end_date))
                else:
                    end_date = wx.DateTime.FromDMY(end_date_parsed["day"], end_date_parsed["month"]-1, end_date_parsed["year"])
                    paydates = []
                    if end_date < start_date:
                        start_date, end_date = end_date, start_date
                    incr = Date.get_pay_incr(self)
                    if incr == None:
                        self.MsgBox("Bad pay Type - get_paydates_in_range calculations ignored!")
                    else:
                        ref_date_parsed = Date.parse_date(self, self.ref_date, dateFormat)
                        if ref_date_parsed == None:
                            self.MsgBox("Can't parse ref date (%s) - ignored!" % (ref_date))
                        else:
                            ref_date = wx.DateTime.FromDMY(ref_date_parsed['day'], ref_date_parsed['month']-1, ref_date_parsed['year'])
                            if ref_date > start_date:
                                while ref_date > start_date:
                                    ref_date.Subtract(incr)
                                if ref_date < start_date:
                                    ref_date.Add(incr)
                            elif ref_date < start_date:
                                while ref_date < start_date:
                                    ref_date.Add(incr)
                            if ref_date == start_date:
                                pay_date = ref_date.Format(self.dateFormat)
                                paydates.append(pay_date)
                                ref_date.Add(incr)
                            while ref_date <= end_date:
                                pay_date = ref_date.Format(self.dateFormat)
                                paydates.append(pay_date)
                                ref_date.Add(incr)
        return paydates

    def updatePayDates(self):
        Date.set_curr_paydate(self)
        Date.set_next_paydate(self)
        print("Curr paydate: %s, Next paydate: %s" % (Date.global_curr_paydate, Date.global_next_paydate))

    def convertDateFormat(self, in_date, in_dateFormat, out_dateFormat):
        in_date_parsed = Date.parse_date(self, in_date, in_dateFormat)
        if in_date_parsed == None:
            self.MsgBox("Bad input converting date format (%s) - ignored!" % (in_date))
            out_date = None
            out_date_str = ""
        else:
            in_date = wx.DateTime.FromDMY(in_date_parsed['day'], in_date_parsed['month']-1, in_date_parsed['year'])
            out_date = in_date
            self.dateFormat = out_dateFormat
            out_date_str = out_date.Format(out_dateFormat)
        return { "dt": out_date, "str": out_date_str }

    # Helper method(s):

    def MsgBox(self, message):
        d = wx.MessageDialog(self.parent, message, "error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()

    def set_global_date_format(self, desired_date_format):
        Date.global_date_format = desired_date_format

    def get_global_date_format(self):
        return Date.global_date_format

    def set_global_date_sep(self, sep):
        Date.global_date_sep = sep

    def get_global_date_sep(self):
        return Date.global_date_sep

    def set_global_curr_date(self, curr_date):
        Date.global_curr_date = curr_date

    def get_global_curr_date(self):
        return Date.get_curr_date(self)

    def set_global_proj_date(self, proj_date):
        Date.global_proj_date = proj_date

    def get_global_proj_date(self):
        return Date.global_proj_date