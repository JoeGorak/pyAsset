#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2016-2024 Joseph J. Gorak. All rights reserved.
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
    global_date_format = ""
    global_date_sep = ""
    global_curr_date = { "dt": None, "str": "" }
    global_proj_date = ""

    #JJG 12/23/2023 Added defaults if none provided
    def __init__(self, parent, in_refDate=None, in_dateFormat="", in_payType=""):
        self.parent = parent
        self.dateFormats = self.getDateFormats()
        if in_dateFormat != "":
            try:
                self.dateFormatChoice = self.dateFormats.index(in_dateFormat)
                self.dateSep = "/"
            except:
                self.dateFormatChoice = -1
            if self.dateFormatChoice == -1:
                today = Date.set_curr_date(self)["str"]
                if today.index("/") == 4:
                    self.dateFormatChoice = 1
                    self.dateSep = "/"
                else:
                    self.dateFormatChoice = 0
                    self.dateSep = "/"
                defaultDateFormat = self.dateFormats[self.dateFormatChoice].replace("%m", "mm").replace("%d", "dd").replace("%y", "yy").replace("%Y", "yyyy")
                self.MsgBox("Unknown date format %s ignored - default to %s" % (in_dateFormat, defaultDateFormat))
        else:
            self.dateFormatChoice = 0
            self.dateSep = "/"
        self.dateFormat = self.dateFormats[self.dateFormatChoice]
        self.inDateFormat = self.dateFormats[self.dateFormatChoice]
        Date.set_global_date_format(self,self.inDateFormat)
        Date.set_global_date_sep(self,self.dateSep)
        if in_dateFormat == "" or in_dateFormat == None:
            self.dateFormat = "%m/%d/%Y"                                # JJG 12/23/2023   added default if no dateFormat given
        else:
            self.dateFormat = in_dateFormat
        self.set_global_date_format(self.dateFormat)
        self.parent = parent
        self.curr_date = self.set_curr_date()
        self.proj_date = self.set_proj_date(self.curr_date["str"])
        self.set_global_proj_date(self.proj_date)
        Date.set_global_curr_date(self, self.get_curr_date())
        Date.set_global_proj_date(self, self.get_proj_date())
        Date.set_global_date_format(self, self.dateFormat)
        Date.set_global_date_sep(self,"/")
 
    def getDateFormats(self):
        return ["%m/%d/%Y", "%Y/%m/%d", "%m-%d-%Y", "%Y-%m-%d"]

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
        in_date = in_date.replace("'","/").replace(" ","0")           # JJG 1/12/2022 replaced ' with / and " " with 0 to handle Quicken .QIF files!
        m = re.match("^[\d]+([/-])[\d]+([/-])[\d]+$", in_date)        # JJG 1/12/2022 removed number length restrictions to handle Quicken .QIF files!
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
                        year = 2000 + int(in_fields[i])
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
                inp_date = in_date.replace("'","/").replace(" ","0")           # JJG 1/22/2022 replace ' with / and " " with 0 to handle Quicken .QIF files!
                dt = wx.DateTime()  # Uninitialized datetime
                in_date = inp_date + " 12:00:00 PM"                            # append a valid time so parse will succeed if we have a valid date! JJG 08/04/2021
                if type(in_date_format) is not str:
                    in_date_format = Date.global_date_format
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
        else:
            self.retVal = { "year" : dt.year, "month" : dt.month + 1, "day" : dt.day, "dt" : dt }
        return self.retVal

    def set_curr_date(self):
        curr_date = wx.DateTime.Today()
        retVal = { "dt": curr_date, "str": curr_date.Format(self.get_date_format()) }
        self.curr_date = retVal["str"]
        return retVal

    def set_proj_date(self, proj_date):
        retVal = None
        error = False
        self.proj_date = ""
        if type(proj_date) is str:
            parsed_proj_date = None
            if (proj_date != ""):
                parsed_proj_date = Date.parse_date(self, proj_date, self.get_date_format())
            if parsed_proj_date != None:
                proj_date_in = wx.DateTime.FromDMY(parsed_proj_date['day'], parsed_proj_date['month']-1, parsed_proj_date['year'])
                self.proj_date = proj_date_in.Format(self.dateFormat)
        elif type(proj_date) is dict:
            self.proj_date = proj_date["str"].Format(self.dateFormat)
        else:
            error = True
        if error:
            self.MsgBox("Bad projected date (%s) - ignored!" % (str(proj_date)))
        else:
            retVal = self.proj_date
        Date.set_global_proj_date(self, retVal)
        return retVal

    def set_date_format(self, desired_date_format):
        Date.global_date_format = desired_date_format
        self.dateFormat = desired_date_format

    def get_date_format(self):
        return Date.global_date_format

    def get_curr_date(self):
        return Date.global_curr_date

    def get_proj_date(self):
        return Date.global_proj_date

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
