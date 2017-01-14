#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2016,2017 Joseph J. Gorak. All rights reserved.
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
#  10/27/2016     Initial version v0.1

import wx
import wx.grid as grd
import re
from datetime import date, datetime


class AssetGrid(grd.Grid):
    def __init__(self, frame):
        self.grid = grd.Grid.__init__(self, frame, -1)
        self.frame = frame
        self.Bind(grd.EVT_GRID_CELL_CHANGING, self.cellchanging)

        # Define the layout of the grid in the frame
        self.ACCT_NAME_COL = 0
        self.ACCT_CURR_VAL_COL = 1
        self.ACCT_PROJ_VAL_COL = 2
        self.ACCT_LAST_PULL_COL = 3
        self.ACCT_LIMIT_COL = 4
        self.ACCT_AVAIL_ONLINE_COL = 5
        self.ACCT_AVAIL_PROJ_COL = 6
        self.ACCT_RATE_COL = 7
        self.ACCT_PAYMENT_COL = 8
        self.ACCT_DUE_DATE_COL = 9
        self.ACCT_SCHED_DATE_COL = 10
        self.ACCT_MIN_PMT_COL = 11
        self.ACCT_STMT_BAL_COL = 12
        self.ACCT_AMT_OVER_COL = 13
        self.ACCT_CASH_LIMIT_COL = 14
        self.ACCT_CASH_USED_COL = 15
        self.ACCT_CASH_AVAIL_COL = 16

        # Define the widths of the columns in the grid
        ACCT_NAME_COL_WIDTH = 150
        ACCT_CURR_VAL_COL_WIDTH = 75
        ACCT_PROJ_VAL_COL_WIDTH = 75
        ACCT_LAST_PULL_COL_WIDTH = 120
        ACCT_LIMIT_COL_WIDTH = 80
        ACCT_AVAIL_ONLINE_COL_WIDTH = 80
        ACCT_AVAIL_PROJ_COL_WIDTH = 80
        ACCT_RATE_COL_WIDTH = 5
        ACCT_PAYMENT_COL_WIDTH = 9
        ACCT_DUE_DATE_COL_WIDTH = 75
        ACCT_SCHED_DATE_COL_WIDTH = 75
        ACCT_MIN_PMT_COL_WIDTH = 8
        ACCT_STMT_BAL_COL_WIDTH = 8
        ACCT_AMT_OVER_COL_WIDTH = 8
        ACCT_CASH_LIMIT_COL_WIDTH = 8
        ACCT_CASH_USED_COL_WIDTH = 8
        ACCT_CASH_AVAIL_COL_WIDTH = 8

        # Define what the valid input data types are
        self.DOLLAR_TYPE = 0
        self.RATE_TYPE = 1
        self.DATE_TYPE = 2
        self.DATE_TIME_TYPE = 3
        self.STRING_TYPE = 4

        # Define if field is editable or not
        self.NOT_EDITABLE = True
        self.EDITABLE = False

        # Define if field should be suppressed if zero
        self.NO_ZERO_SUPPRESS = False
        self.ZERO_SUPPRESS = True

        # Define indices of columns in grid layout array
        self.NAME_COL = 0
        self.WIDTH_COL = 1
        self.TYPE_COL = 2
        self.EDIT_COL = 3
        self.ZERO_SUPPRESS_COL = 4

        # Grid layout array
        self.col_info = [
                         [self.ACCT_NAME_COL, ACCT_NAME_COL_WIDTH, self.STRING_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.ACCT_CURR_VAL_COL, ACCT_CURR_VAL_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE, self.NO_ZERO_SUPPRESS],
                         [self.ACCT_PROJ_VAL_COL, ACCT_PROJ_VAL_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE, self.NO_ZERO_SUPPRESS],
                         [self.ACCT_LAST_PULL_COL, ACCT_LAST_PULL_COL_WIDTH, self.DATE_TIME_TYPE, self.NOT_EDITABLE, self.ZERO_SUPPRESS],
                         [self.ACCT_LIMIT_COL, ACCT_LIMIT_COL_WIDTH, self.DOLLAR_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.ACCT_AVAIL_ONLINE_COL, ACCT_AVAIL_ONLINE_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE, self.ZERO_SUPPRESS],
                         [self.ACCT_AVAIL_PROJ_COL, ACCT_AVAIL_PROJ_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE, self.ZERO_SUPPRESS],
                         [self.ACCT_RATE_COL, ACCT_RATE_COL_WIDTH, self.RATE_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.ACCT_PAYMENT_COL, ACCT_PAYMENT_COL_WIDTH, self.DOLLAR_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.ACCT_DUE_DATE_COL, ACCT_DUE_DATE_COL_WIDTH, self.DATE_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.ACCT_SCHED_DATE_COL, ACCT_SCHED_DATE_COL_WIDTH, self.DATE_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.ACCT_MIN_PMT_COL, ACCT_MIN_PMT_COL_WIDTH, self.DOLLAR_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.ACCT_STMT_BAL_COL, ACCT_STMT_BAL_COL_WIDTH, self.DOLLAR_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.ACCT_AMT_OVER_COL, ACCT_AMT_OVER_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE, self.ZERO_SUPPRESS],
                         [self.ACCT_CASH_LIMIT_COL, ACCT_CASH_LIMIT_COL_WIDTH, self.DOLLAR_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.ACCT_CASH_USED_COL, ACCT_CASH_USED_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE, self.ZERO_SUPPRESS],
                         [self.ACCT_CASH_AVAIL_COL, ACCT_CASH_AVAIL_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE, self.ZERO_SUPPRESS]
                        ]

        return

    def getColName(self, col):
#        lab = self.GetColLabelValue(col)
        if col == self.ACCT_NAME_COL:
            return "Acct name"
        elif col == self.ACCT_CURR_VAL_COL:
            return "Curr val"
        elif col == self.ACCT_LAST_PULL_COL:
            return "Last pulled"
        elif col == self.ACCT_LIMIT_COL:
            return "Limit"
        elif col == self.ACCT_AVAIL_ONLINE_COL:
            return "Avail online"
        elif col == self.ACCT_RATE_COL:
            return "Rate"
        elif col == self.ACCT_PAYMENT_COL:
            return "Payment amt"
        elif col == self.ACCT_DUE_DATE_COL:
            return "Due date"
        elif col == self.ACCT_SCHED_DATE_COL:
            return "Sched date"
        elif col == self.ACCT_MIN_PMT_COL:
            return "Min pmt"
        elif col == self.ACCT_STMT_BAL_COL:
            return "Stmt Bal"
        elif col == self.ACCT_AMT_OVER_COL:
            return "Amt Over"
        elif col == self.ACCT_CASH_LIMIT_COL:
            return "Cash Limit"
        elif col == self.ACCT_CASH_USED_COL:
            return "Cash Used"
        elif col == self.ACCT_CASH_AVAIL_COL:
            return "Cash Avail"
        else:
            return "Unknown"

    def getColWidth(self, i):
        return self.col_info[i][self.WIDTH_COL]

    def getColType(self, i):
        return self.col_info[i][self.TYPE_COL]

    def getColEdit(self, i):
        return self.col_info[i][self.EDIT_COL]

    def getColZeroSuppress(self, row, i):
        return self.col_info[i][self.ZERO_SUPPRESS_COL]

    def getColMethod(self, row, i):
        if i == self.ACCT_NAME_COL:
            return self.frame.assets[row].name
        elif i == self.ACCT_CURR_VAL_COL:
            return self.frame.assets[row].total
        elif i == self.ACCT_PROJ_VAL_COL:
            return self.frame.assets[row].total
        elif i == self.ACCT_LAST_PULL_COL:
            return self.frame.assets[row].last_pull_date
        elif i == self.ACCT_LIMIT_COL:
            return self.frame.assets[row].limit
        elif i == self.ACCT_AVAIL_ONLINE_COL:
            return self.frame.assets[row].avail
        elif i == self.ACCT_AVAIL_PROJ_COL:
            return self.frame.assets[row].avail
        elif i == self.ACCT_RATE_COL:
            return self.frame.assets[row].rate
        elif i == self.ACCT_PAYMENT_COL:
            return self.frame.assets[row].payment
        elif i == self.ACCT_DUE_DATE_COL:
            return self.frame.assets[row].due_date
        elif i == self.ACCT_SCHED_DATE_COL:
            return self.frame.assets[row].sched
        elif i == self.ACCT_MIN_PMT_COL:
            return self.frame.assets[row].min_pay
            #                         [ACCT_STMT_BAL_COL, ACCT_STMT_BAL_COL_WIDTH, DOLLAR_TYPE, EDITABLE, None],
            #                         [ACCT_AMT_OVER_COL, ACCT_AMT_OVER_COL_WIDTH, DOLLAR_TYPE, NOT_EDITABLE, None],
            #                         [ACCT_CASH_LIMIT_COL, ACCT_CASH_LIMIT_COL_WIDTH, DOLLAR_TYPE, EDITABLE, None],
            #                         [ACCT_CASH_USED_COL, ACCT_CASH_USED_COL_WIDTH, DOLLAR_TYPE, NOT_EDITABLE, None],
            #                         [ACCT_CASH_AVAIL_COL, ACCT_CASH_AVAIL_COL_WIDTH, DOLLAR_TYPE, NOT_EDITABLE, None]
        return "??"

    def getNumLayoutCols(self):
        return len(self.col_info)

#TODO Investigate making GridCell Renderers be true cell renderers vice functions!

    def GridCellErrorRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        self.SetCellAlignment(row, col, wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        tableValue = "Bad: %s" % (cellValue)
        self.frame.assetGrid.SetCellValue(row, col, tableValue)

    def GridCellDefaultRenderer(self, row, col):
        self.SetCellTextColour(row, col, 'black')
        self.SetReadOnly(row, col, self.getColEdit(col))
        self.SetCellAlignment(row, col, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        cellValue = str(self.getColMethod(row, col))
        if self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS and (cellValue == "0" or cellValue == "0.00"):
            cellValue = ""
        # Note that this doesn't display the value in the grid so that if further formatting is required, user won't see default formatting first!
        return cellValue

    def GridCellDollarRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        try:
            NumberAmount = cellValue.replace("$", "").replace(",", "")
            amount = float(NumberAmount)
        except:
            amount = 0.0
        if amount < 0:
            negative = True
            amount = -amount
        else:
            negative = False
        dotPos = cellValue.find(".")
        if dotPos == -1:
            cent_val = 0
        else:
            cent_val = int(cellValue[dotPos + 1:])
            if dotPos == len(cellValue) - 2:
                cent_val *= 10
        cents = "%02d" % (cent_val)
        cents = str(cents)
        groups = [cents]
        groups.append(".")
        amount -= float(cent_val) / 100
        if amount < 1:
            groups.append("0")
            groups.append(",")
        while amount > 1:
            next_digits = "%s" % str((int(amount) % 1000))
            while len(next_digits) < 3:
                if amount > 100:
                    digit = "0"
                else:
                    digit = " "
                next_digits = digit + next_digits
            groups.append(next_digits)
            groups.append(",")
            amount /= 1000
        str_out = ""
        for j in range(len(groups) - 2, -1, -1):
            str_out += str(groups[j])
        if self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS and str_out == "0.00":
            tableValue = ""
        else:
            if negative:
                self.frame.assetGrid.SetCellTextColour(row, col, 'red')
                tableValue = "-$%13s" % (str_out)
            else:
                tableValue = " $%13s" % (str_out)
        self.frame.assetGrid.SetCellValue(row, col, tableValue)

    def GridCellPercentRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        rate = float(cellValue)
        if self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS and rate == 0.0:
            tableValue = ""
        else:
            tableValue = "%13.3f%%" % (rate * 100.0)
        self.frame.assetGrid.SetCellValue(row, col, tableValue)

    def GridCellDateRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        if self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS and (cellValue == "0" or cellValue == ""):
            tableValue = ""
        else:
            dateParts = cellValue.split("-")
            month = dateParts[1]
            day = dateParts[2]
            year = dateParts[0]
            self.SetCellAlignment(row, col, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
            tableValue = "%02s/%02s/%04s" % (month, day, year)
        self.frame.assetGrid.SetCellValue(row, col, tableValue)

    def GridCellDateTimeRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        if self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS and cellValue == "0":
            tableValue = ""
        else:
            datetimeParts = cellValue.split(" ")
            dateParts = datetimeParts[0].split("-")
            time = datetimeParts[1]
            month = dateParts[1]
            day = dateParts[2]
            year = dateParts[0]
            self.SetCellAlignment(row, col, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
            tableValue = "%02s/%02s/%04s %s" % (month, day, year, time)
        self.SetCellValue(row, col, tableValue)

    def GridCellStringRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        self.SetCellAlignment(row, col, wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        if self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS and (cellValue == "0" or cellValue == "0.00"):
            tableValue = ""
        else:
            tableValue = cellValue
        self.frame.assetGrid.SetCellValue(row, col, tableValue)

    def DisplayMsg(self, str):
        d = wx.MessageDialog(self, str, "Error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()
        return wx.CANCEL

    def cellchanging(self, evt):
        row = evt.GetRow()
        col = evt.GetCol()
        ret_val = wx.OK
        new_value = evt.String
        if row < 0 or row >= len(self.frame.assets):
            str = "Warning: cellchanging on bad cell %d %d!" % (row, col)
            ret_val =  self.DisplayMsg(str)
        if ret_val == wx.OK and self.col_info[col][self.TYPE_COL] == self.DOLLAR_TYPE:
#TODO  move regular expression for dollar format to new object
            m = re.match("^-?\$?\d{1,3}(\,?\d{3})*(\.\d{2})*$", new_value)
            if m:
                self.edited = 1
                dollar_amount = new_value.replace("$", "").replace(",", "")
                if "." not in dollar_amount:
                    dollar_amount += ".00"
                    evt.Veto()
                    self.frame.assetGrid.SetCellValue(row, col, dollar_amount)
                evt.String = dollar_amount
            else:
                str = "%s is not a valid dollar string" % (new_value)
                ret_val =  self.DisplayMsg(str)
        elif ret_val == wx.OK and self.col_info[col][self.TYPE_COL] == self.RATE_TYPE:
#TODO  move regular expression for rate format to new object
            m = re.match("^\d{1,3}(\.\d{1,3})?\%?$", new_value)
            if m:
                self.edited = 1
                evt.Veto()
                rate_amount = float(new_value.replace("%", ""))/100.0
                evt.String = "%8.5f" % (rate_amount)
            else:
                str = "%s is not a valid rate string" % (new_value)
                ret_val = self.DisplayMsg(str)
        elif ret_val == wx.OK and self.col_info[col][self.TYPE_COL] == self.DATE_TYPE:
            if new_value == "" and self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS:
                evt.Veto()
            else:
#TODO  move regular expression for date format to new object
                m = re.match("^\d{1,2}([/-])\d{1,2}([/-])\d{4}?$", new_value)
                if m:
                    sep = m.groups()
                    evt.Veto()
                    pos1 = new_value.index(sep[0])
                    pos2 = new_value.rindex(sep[1])
                    mon = int(new_value[0:pos1])
                    day = int(new_value[pos1+1:pos2])
                    year = int(new_value[pos2+1:])
                    try:
                        in_date = date(year,mon,day)
                    except:
                        str = "%s is not a valid date string" % (new_value)
                        ret_val = self.DisplayMsg(str)
                    else:
                        self.edited = 1
                        in_date_string = "%04s-%02d-%02d" % (year, mon, day)
                        evt.String = in_date_string
                else:
                    str = "%s is not a valid date string" % (new_value)
                    ret_val = self.DisplayMsg(str)
        elif ret_val == wx.OK and self.col_info[col][self.TYPE_COL] == self.DATE_TIME_TYPE:
            if new_value == "" and self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS:
                evt.Veto()
            else:
#TODO  move regular expression for datetime format to new object
                m = re.match("^\d{1,2}([/-])\d{1,2}([/-])\d{4} \d{2}:\d{2}:\d{2}?$", new_value)
                if m:
                    sep = m.groups()
                    evt.Veto()
                    pos1 = new_value.index(sep[0])
                    pos2 = new_value.rindex(sep[1])
                    pos3 = new_value.index(" ")
                    pos4 = new_value.index(":")
                    pos5 = new_value.rindex(":")
                    mon = int(new_value[0:pos1])
                    day = int(new_value[pos1+1:pos2])
                    year = int(new_value[pos2+1:pos3])
                    hour = int(new_value[pos3+1:pos4])
                    min = int(new_value[pos4+1:pos5])
                    sec = int(new_value[pos5+1:])
                    try:
                        in_datetime = datetime(year,mon,day,hour,min,sec)
                    except:
                        str = "%s is not a valid datetime string" % (new_value)
                        ret_val = self.DisplayMsg(str)
                    else:
                        self.edited = 1
                        in_datetime_string = "%04s-%02d-%02d %02d:%02d:%02d" % (year, mon, day, hour, min, sec)
                        evt.String = in_datetime_string
                else:
                    str = "%s is not a valid datetime string" % (new_value)
                    ret_val = self.DisplayMsg(str)
        elif ret_val == wx.OK and self.col_info[col][self.TYPE_COL] == self.STRING_TYPE:
            evt.Veto()
        else:
            str = "Warning: cellchanging not allowed for cell %d %d!" % (row, col)
            ret_val =  self.DisplayMsg(str)
        if ret_val == wx.OK:
            self.frame.assetchange(evt)
        else:
            evt.Veto()
        self.frame.redraw_all(row)  # only redraw current row

    def set_properties(self, frame):
        frame.SetTitle("PyAsset: Asset")
        frame.statusbar.SetStatusWidths([-1])
        statusbar_fields = [""]
        columnNames = ["Account", "Value (Curr)", "Value (Proj)", "last pulled", "Limit", "Avail (Online)", "Avail (Proj)",
                       "Rate",
                       "Payment", "Due Date", "Sched", "Min Pmt", "Stmt Bal", "Amt Over", "Cash Limit", "Cash used",
                       "Cash avail"];

        for i in range(len(statusbar_fields)):
            frame.statusbar.SetStatusText(statusbar_fields[i], i)
        self.CreateGrid(0, len(columnNames))
        self.SetRowLabelSize(frame.rowSize)
        self.SetColLabelSize(frame.colSize)
        self.total_width = 60  # non-zero start value to account for record number of assetGrid frame!
        for i in range(len(columnNames)):
            self.SetColLabelValue(i, columnNames[i])
            cur_width = self.getColWidth(i)
            self.total_width += cur_width
            self.SetColSize(i, cur_width)
        return self.total_width
