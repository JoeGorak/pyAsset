#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2016-2025 Joseph J. Gorak. All rights reserved.
This code is in development -- use at your own risk. Email
comments, patches, complaints to joegorak808@outlook.com

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

import wx
import re

from wx.core import DateTime
from datetime import datetime

class Date:
    global_date_format = "%m/%d/%Y"
    global_date_sep = "/"
    global_curr_date = wx.DateTime.Today()
    global_proj_date = wx.DateTime.Today()

    #JJG 12/23/2023 Added defaults if none provided
    def __init__(self, parent, in_refDate=None, in_dateFormat="", in_payType=""):
        Date.parent = parent
        self.parent = parent
        parsed_in_date = self.parseDateFormat(in_dateFormat)
        in_dateFormat = parsed_in_date[0]
        in_dateSep = parsed_in_date[1]
        Date.set_global_date_format(Date, in_dateFormat)
        Date.set_global_date_sep(Date, in_dateSep)
        self.parent = parent
        self.curr_date = self.set_curr_date()
        self.proj_date = self.set_proj_date("")
        self.set_global_proj_date(self.proj_date)
 
    def getDateFormats(self):
        return ["%m/%d/%Y", "%Y/%m/%d", "%m-%d-%Y", "%Y-%m-%d"]

    def guessDateFormat(self, in_date, globalUpdate = False):
        if type(in_date) is dict:
            in_date = in_date["str"]
        dateFormat = Date.get_global_date_format(Date)              # JJG 7/28/2024 if no date passed, just return current global format
        dateSep = Date.get_global_date_sep(Date)
        if in_date == "":
            return dateFormat
        found = False
        dateFormats = Date.getDateFormats(self)
        try:
            slash_ind = in_date.index("/")
        except:
            slash_ind = -1
        try:
            dash_ind = in_date.index("-")
        except:
            dash_ind = -1
        if slash_ind != -1:
            dateSep = "/"
            dateParts = in_date.split(dateSep)
            if int(dateParts[0]) > 31:
                dateFormat = "%Y/%m/%d"
            else:
                dateFormat = "%m/%d/%Y"
        elif dash_ind != -1:
            dateSep = '-'
            dateParts = in_date.split(dateSep)
            if int(dateParts[0]) > 31:
                dateFormat = "%Y-%m-%d"
            else:
                dateFormat = "%m-%d-%Y"
        else:
            dateFormat = "%m/%d/%Y"
            Date.MsgBox(Date, "Unknown date format for date %s ignored - default to %s" % (in_date, dateFormat))
        if globalUpdate:
            self.set_global_date_format(Date, dateFormat)
            self.set_global_date_sep(Date, dateSep)
        return dateFormat

    def parseDateFormat(self, in_dateFormat=""):
        dateFormats = Date.getDateFormats(self)
        if in_dateFormat != "":
            try:
                dateFormatChoice = dateFormats.index(in_dateFormat)
            except:
                dateFormatChoice = -1
        else:
            dateFormatChoice = dateFormats.index("%m/%d/%Y")
        dateFormat = dateFormats[dateFormatChoice]
        try:
            slash_ind = dateFormat.index("/")
        except:
            slash_ind = -1
        try:
            dash_ind = dateFormat.index("-")
        except:
            dash_ind = -1
        if slash_ind != -1:
            dateSep = "/"
        elif dash_ind != -1:
            dateSep = '-'
        else:
            dataFormatChoice = -1
        if dateFormatChoice == -1:
            today = Date.set_curr_date(self)["str"]
            if today.index("/") == 4:
                dateFormatChoice = dateFormats.index("%Y/%m/%d")
                dateSep = "/"
            else:
                dateFormatChoice = dateFormats.index("%m/%d/%Y")
                dateSep = "/"
#            self.MsgBox("Unknown date format %s ignored - default to %s" % (in_dateFormat, dateFormats[dateFormatChoice]))
        return dateFormat, dateSep

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
        date_format = Date.guessDateFormat(Date, in_date)
        date_fields = Date.parse_date(Date, in_date, date_format)
        retVal = [ date_fields['year'], date_fields['month'], date_fields['day'] ]
        return retVal

    def get_display_date(self, in_date):
        if type(in_date) is not str:
            in_date = in_date["str"]
        return Date.parse_date(Date,in_date,Date.get_global_date_format(Date))["str"]

    def parse_date(self, in_date, date_format):
        error = False
        retVal = None
        if type(in_date) is str:
            if in_date == "":
                dt = wx.DateTime.Today()
            else:
                in_date = in_date.replace("'","/").replace(" ","0")           # JJG 1/22/2022 replace ' with / and " " with 0 to handle Quicken .QIF files!
                dt = wx.DateTime()  # Uninitialized datetime
                if dt.ParseFormat(in_date, date_format) == -1:
                    error = True
            if not error:
                year = dt.year
                month = dt.month+1
                day = dt.day
        elif type(in_date) is DateTime or type(in_date) is datetime:
            dt = in_date
            year = dt.year
            month = dt.month
            if type(in_date) is DateTime:
                month += 1
            day = dt.day
        elif type(in_date) is dict:
            dt = in_date["dt"]
            year = dt.year
            month = dt.month
            if type(dt) is DateTime:
                month += 1
            day = dt.day
        elif type(in_date) is Date:
            dt = in_date["dt"]
            year = dt.year
            month = dt.month
            day = dt.day
        else:
            error = True
        if error:
            pass                                # Leave error message display to the caller!  We just return None!
        else:
            retVal = { "year" : year, "month" : month, "day" : day, "dt" : dt }
            retVal["str"] = wx.DateTime.FromDMY(day, month-1, year).Format(Date.get_global_date_format(Date))
        return retVal

    def get_today_date(self):
        curr_date = wx.DateTime.Today()
        curr_date_str = wx.DateTime.FromDMY(curr_date.day, curr_date.month, curr_date.year).Format(Date.get_global_date_format(Date))
        return { "dt": curr_date, "str": curr_date_str }

    def get_today_date_time(self):
        curr_date = self.get_today_date(self)["str"]
        return { curr_date + str(wx.DateTime.GetTimeNow()) }

    def set_curr_date(self):
        curr_date = Date.get_today_date(Date)
 #       self.curr_date = curr_date["str"]
        Date.set_global_curr_date(Date, curr_date)
        return curr_date

    def set_proj_date(self, proj_date):
        retVal = None
        error = False
        self.proj_date = ""
        if type(proj_date) is str:
            parsed_proj_date = None
            if (proj_date != ""):
                parsed_proj_date = Date.parse_date(self, proj_date, Date.get_date_format(Date))
            else:
                self.proj_date = Date.get_date_format(Date).replace("%y", "yy").replace("%m", "mm").replace("%d", "dd").replace("%Y", "yyyy")
            if parsed_proj_date != None:
                proj_date_in = wx.DateTime.FromDMY(parsed_proj_date['day'], parsed_proj_date['month']-1, parsed_proj_date['year'])
                self.proj_date = proj_date_in.Format(Date.get_date_format(Date))
        elif type(proj_date) is dict:
            self.proj_date = proj_date["dt"].Format(Date.get_date_format(Date))
        else:
            error = True
        if error:
            self.MsgBox("Bad projected date (%s) - ignored!" % (str(proj_date)))
        else:
            retVal = self.proj_date
        Date.set_global_proj_date(Date, retVal)
        return retVal

    def set_date_format(self, desired_date_format):
        return self.set_global_date_format(desired_date_format)

    def get_date_format(self):
        return Date.global_date_format

    def get_curr_date(self):
        return Date.global_curr_date

    def get_proj_date(self):
        return Date.global_proj_date

    def convertDateTimeFormat(self, in_date_time, old_date_format, new_date_format):
        date_time = in_date_time.split()
        in_date = date_time[0]
        in_time = date_time[1]
        new_date = Date.convertDateFormat(self, in_date, old_date_format, new_date_format)["str"]
        return new_date + " " + in_time

    def convertDateFormat(self, in_date, in_dateFormat, out_dateFormat):
        if in_dateFormat != "":
            if type(in_date) is str:
                in_date = Date.parse_date(self, in_date, in_dateFormat)
                out_date_dt = in_date["dt"]
                out_date_str = in_date["str"]
            else:
                year, month, day = Date.get_date_fields(Date, in_date)
                out_date_dt = wx.DateTime.FromDMY(day, month-1, year)
                out_date_str = out_date_dt.Format(out_dateFormat)
        else:
            if type(in_date) is str:
                date_format = self.guessDateFormat(Date, in_date)
                in_date = Date.parse_date(self, in_date, date_format)
            out_date_dt = in_date["dt"]
            out_date_str = in_date["str"]
        return { "dt": out_date_dt, "str": out_date_str }

    # Helper method(s):

    def MsgBox(self, message):
        d = wx.MessageDialog(self.parent, message, "error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()

    def set_global_date_format(self, desired_date_format):
        parsed_date_format = Date.parseDateFormat(Date, desired_date_format)
        self.global_date_format = Date.global_date_format = parsed_date_format[0]
        self.global_date_sep = Date.global_date_sep = parsed_date_format[1]
        return parsed_date_format

    def get_global_date_format(self):
        return Date.global_date_format

    def set_global_date_sep(self, sep):
        Date.global_date_sep = sep

    def get_global_date_sep(self):
        return Date.global_date_sep

    def set_global_curr_date(self, curr_date):
        if type(curr_date) is str:
            parsed_curr_date = Date.parse_date(Date, curr_date, Date.get_global_date_format(Date))
            curr_date = parsed_curr_date
            curr_date_str = wx.DateTime.FromDMY(parsed_curr_date['day'], parsed_curr_date['month'], parsed_curr_date['year'])
            curr_date["str"] = curr_date_str.Format(Date.get_global_date_format(Date))
        Date.global_curr_date = curr_date

    def get_global_curr_date(self):
        return Date.global_curr_date

    def set_global_proj_date(self, proj_date):
        if type(proj_date) is str:
            parsed_proj_date = Date.parse_date(Date,proj_date,Date.get_global_date_format(Date))
            proj_date = parsed_proj_date
        Date.global_proj_date = proj_date

    def get_global_proj_date(self):
        return Date.global_proj_date
