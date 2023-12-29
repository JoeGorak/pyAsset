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
#  08/07/2021     Version v0.2

import wx
from wx.core import DefaultTimeSpanFormat
import wx.grid as grd
import re
from datetime import date, datetime
from Date import Date

class AssetGrid(grd.Grid):
    def __init__(self, frame, **keywrds):
        self.dateFormat = Date.get_global_date_format(self)
        self.dateSep = Date.get_global_date_sep(self)
        self.columnNames = ["Account", "Value (Curr)", "Value (Proj)", "last pulled",
                            "Limit", "Avail (Online)", "Avail (Proj)", "Rate",
                            "Payment", "Due Date", "Sched", "Min Pmt", "Stmt Bal",
                            "Amt Over", "Cash Limit", "Cash used", "Cash avail"]
        self.grid = grd.Grid.__init__(self, frame, **keywrds)
        self.minNumRows = frame.BestSize.Height
        self.CreateGrid(self.minNumRows, len(self.columnNames))
        self.frame = frame

        # Define all needed evenent bindings
        self.Bind(grd.EVT_GRID_CELL_CHANGING, self.cellchanging)

        self.Bind(grd.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.Bind(grd.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
        self.Bind(grd.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)
        self.Bind(grd.EVT_GRID_CELL_RIGHT_DCLICK, self.OnCellRightDClick)

        self.Bind(grd.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        self.Bind(grd.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClick)
        self.Bind(grd.EVT_GRID_LABEL_LEFT_DCLICK, self.OnLabelLeftDClick)
        self.Bind(grd.EVT_GRID_LABEL_RIGHT_DCLICK, self.OnLabelRightDClick)

        self.Bind(grd.EVT_GRID_ROW_SIZE, self.OnRowSize)
        self.Bind(grd.EVT_GRID_COL_SIZE, self.OnColSize)

        self.Bind(grd.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        #self.Bind(grd.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        self.Bind(grd.EVT_GRID_SELECT_CELL, self.OnSelectCell)

        self.Bind(grd.EVT_GRID_EDITOR_SHOWN, self.OnEditorShown)
        self.Bind(grd.EVT_GRID_EDITOR_HIDDEN, self.OnEditorHidden)
        self.Bind(grd.EVT_GRID_EDITOR_CREATED, self.OnEditorCreated)

        # Define the layout of the grid in the frame
        Headers = self.columnNames
        self.ACCT_NAME_COL = Headers.index("Account")
        self.ACCT_CURR_VAL_COL = Headers.index("Value (Curr)")
        self.ACCT_PROJ_VAL_COL = Headers.index("Value (Proj)")
        self.ACCT_LAST_PULL_COL = Headers.index("last pulled")
        self.ACCT_LIMIT_COL = Headers.index("Limit")
        self.ACCT_AVAIL_ONLINE_COL = Headers.index("Avail (Online)")
        self.ACCT_AVAIL_PROJ_COL = Headers.index("Avail (Proj)")
        self.ACCT_RATE_COL = Headers.index("Rate")
        self.ACCT_PAYMENT_COL = Headers.index("Payment")
        self.ACCT_DUE_DATE_COL = Headers.index("Due Date")
        self.ACCT_SCHED_DATE_COL = Headers.index("Sched")
        self.ACCT_MIN_PMT_COL = Headers.index("Min Pmt")
        self.ACCT_STMT_BAL_COL = Headers.index("Stmt Bal")
        self.ACCT_AMT_OVER_COL = Headers.index("Amt Over")
        self.ACCT_CASH_LIMIT_COL = Headers.index("Cash Limit")
        self.ACCT_CASH_USED_COL = Headers.index("Cash used")
        self.ACCT_CASH_AVAIL_COL = Headers.index("Cash avail")

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
            [self.ACCT_CASH_AVAIL_COL, ACCT_CASH_AVAIL_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE, self.ZERO_SUPPRESS],
        ]

    def getMinNumRows(self):
        return(self.minNumRows)

    def getNumColumns(self):
        return(len(self.columnNames))

    def getColName(self, col):
        return self.GetColLabelValue(col)

    def getColWidth(self, i):
        return self.col_info[i][self.WIDTH_COL]

    def getColType(self, i):
        return self.col_info[i][self.TYPE_COL]

    def getColEdit(self, i):
        return self.col_info[i][self.EDIT_COL]

    def getColZeroSuppress(self, row, i):
        return self.col_info[i][self.ZERO_SUPPRESS_COL]

    def setColZeroSuppress(self, row, i, zero_suppress):
        if zero_suppress != self.ZERO_SUPPRESS and zero_suppress != self.NO_ZERO_SUPPRESS:
            print(
                "Bad value for zero_suppress:" + zero_suppress + " Ignored! Should be either " + self.ZERO_SUPPRESS + " or " + self.NO_ZERO_SUPPRESS_)
        else:
            self.col_info[i][self.ZERO_SUPPRESS_COL] = zero_suppress

    def getFrame(self):
        return(self.Parent.Parent)

    def getColMethod(self, row, i):
        currAsset = self.getFrame().assets[row]
        if i == self.ACCT_NAME_COL:
            return currAsset.get_name()
        elif i == self.ACCT_CURR_VAL_COL:
            return currAsset.get_value()
        elif i == self.ACCT_PROJ_VAL_COL:
            return currAsset.get_value_proj()
        elif i == self.ACCT_LAST_PULL_COL:
            return currAsset.get_last_pull_date()
        elif i == self.ACCT_LIMIT_COL:
            return currAsset.get_limit()
        elif i == self.ACCT_AVAIL_ONLINE_COL:
            return currAsset.get_avail()
        elif i == self.ACCT_AVAIL_PROJ_COL:
            return currAsset.get_avail_proj()
        elif i == self.ACCT_RATE_COL:
            return currAsset.get_rate()
        elif i == self.ACCT_PAYMENT_COL:
            return currAsset.get_payment()
        elif i == self.ACCT_DUE_DATE_COL:
            return currAsset.get_due_date()
        elif i == self.ACCT_SCHED_DATE_COL:
            return currAsset.get_sched_date()
        elif i == self.ACCT_MIN_PMT_COL:
            return currAsset.get_min_pay()
        elif i == self.ACCT_STMT_BAL_COL:
            return currAsset.get_stmt_bal()
        elif i == self.ACCT_CASH_LIMIT_COL:
            return currAsset.get_cash_limit()
        elif i == self.ACCT_CASH_USED_COL:
            return currAsset.get_cash_used()
        elif i == self.ACCT_CASH_AVAIL_COL:
            return currAsset.get_cash_avail()
        else:
            return "??"

    def getNumLayoutCols(self):
        return len(self.col_info)

    # TODO Investigate making GridCell Renderers be true cell renderers vice functions!

    def GridCellErrorRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        self.SetCellAlignment(row, col, wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        tableValue = "Bad: %s" % (cellValue)
        self.getFrame().assetGrid.SetCellValue(row, col, tableValue)

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
        self.SetCellAlignment(row, col, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        try:
            NumberAmount = cellValue.replace("$", "").replace(",", "")
            amount = round(float(NumberAmount),2)
        except:
            amount = round(float(0.0),2)
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
        groups = [cents]
        groups.append(".")
        amount = round(amount - float(cent_val) / 100, 2)
        if amount < 1:
            groups.append("0")
            groups.append(",")
        while amount >= 1:
            next_digits = "%s" % str((int(amount) % 1000))
            while len(next_digits) < 3:
                if amount > 100:
                    digit = "0"
                else:
                    digit = " "
                next_digits = digit + next_digits
            groups.append(next_digits)
            groups.append(",")
            amount = round(amount / 1000, 2)
        str_out = ""
        for j in range(len(groups) - 2, -1, -1):
            str_out += str(groups[j])
        if self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS and str_out == "0.00":
            tableValue = ""
        else:
            str_out = str_out.strip(' \t')
            field_width = 13  # Assume largest number is 999,999.99 which needs 10 places so add a couple for safety!
            num_chars = len(str_out)
            num_blanks = field_width - num_chars - 1
            blanks = "" * num_blanks
            format_start = "%%%1ds" % (num_blanks)
            num_format = "%%%1ds" % (num_chars)
            if negative:
                self.getFrame().assetGrid.SetCellTextColour(row, col, 'red')
                format_str = format_start + "-$" + num_format
                tableValue = format_str % (blanks, str_out)
            else:
                self.getFrame().assetGrid.SetCellTextColour(row, col, 'black')
                format_str = format_start + " $" + num_format
                tableValue = format_str % (blanks, str_out)
        self.getFrame().assetGrid.SetCellValue(row, col, tableValue)

    def GridCellPercentRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        try:
            rate = float(cellValue)
        except:
            rate = 0.0
        if self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS and rate == 0.0:
            tableValue = ""
        else:
            tableValue = "%13.3f%%" % (rate * 100.0)
        self.getFrame().assetGrid.SetCellValue(row, col, tableValue)

    def GridCellDateRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        if cellValue == None or cellValue == "None":
            tableValue = ""
        elif self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS and (cellValue == "0" or cellValue == ""):
            tableValue = ""
        else:
            returned_date = Date.parse_date(self, cellValue, Date.get_global_date_format(self))
            if returned_date != None:
                tableDate = wx.DateTime.FromDMY(returned_date["day"], returned_date["month"]-1, returned_date["year"])
                dateFormat = Date.get_global_date_format(self)
                date_sep = Date.get_global_date_sep(self)
                dateParts = dateFormat.split(date_sep)
                tableValue = ""
                for i in range(len(dateParts)):
                    if dateParts[i] == "%m":
                        tableValue = tableValue + "%02d" % (int(returned_date["month"]))
                    elif dateParts[i] == "%d":
                        tableValue = tableValue + "%02d" % (int(returned_date["day"]))
                    elif dateParts[i] == "%Y":
                        tableValue = tableValue + "%04d" % (int(returned_date["year"]))
                    elif dateParts[i] == "%y":
                        # assume all 2 digit years are in the range 2000 <= year < 2099.  Don't expect this software to be used in the year 2100!! JJG 07/08/2021
                        tableValue = tableValue + "%04d" % (2000 + int(returned_date["year"]))
                    if i < len(dateParts)-1:
                        tableValue = tableValue + "%s" % (Date.get_global_date_sep(self))
            else:
                tableValue = ""
                self.DisplayMsg("Bad cell date for row %d col %d ignored: %s" % (row, col, cellValue))
        self.SetCellAlignment(row, col, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.getFrame().assetGrid.SetCellValue(row, col, tableValue)

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
        self.getFrame().assetGrid.SetCellValue(row, col, tableValue)

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
        if new_value == "":
            col_type = self.col_info[col][self.TYPE_COL]
            if col_type == self.DOLLAR_TYPE: new_value = "0.00"
        if row < 0 or row >= len(self.getFrame().assets):
            str = "Warning: cellchanging on bad cell %d %d!" % (row, col)
            ret_val = self.DisplayMsg(str)
        elif self.col_info[col][self.EDIT_COL] == self.NOT_EDITABLE:
            str = "Warning: Changes not allowed for column %s!" % (self.getColName(col))
            ret_val = self.DisplayMsg(str)
        if ret_val == wx.OK and self.col_info[col][self.TYPE_COL] == self.DOLLAR_TYPE:
            # TODO  move regular expression for dollar format to new object
            m = re.match("^-?\$?\d{1,3}(\,?\d{3})*(\.\d{2})*$", new_value)
            if m:
                self.edited = True
                dollar_amount = new_value.replace("$", "").replace(",", "")
                if "." not in dollar_amount:
                    dollar_amount += ".00"
                    evt.Veto()
                    self.getFrame().assetGrid.SetCellValue(row, col, dollar_amount)
                evt.String = dollar_amount
            else:
                str = "%s is not a valid dollar string" % (new_value)
                ret_val = self.DisplayMsg(str)
        elif ret_val == wx.OK and self.col_info[col][self.TYPE_COL] == self.RATE_TYPE:
            # TODO  move regular expression for rate format to new object
            m = re.match("^\d{1,3}(\.\d{1,3})?\%?$", new_value)
            if m:
                self.edited = True
                evt.Veto()
                rate_amount = float(new_value.replace("%", "")) / 100.0
                evt.String = "%8.5f" % (rate_amount)
            else:
                str = "%s is not a valid rate string" % (new_value)
                ret_val = self.DisplayMsg(str)
        elif ret_val == wx.OK and self.col_info[col][self.TYPE_COL] == self.DATE_TYPE:
            if new_value == "" and self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS:
                evt.Veto()
            else:
                # TODO  move regular expression for date format to new object
                m = re.match("^\d{1,2}([/-])\d{1,2}([/-])\d{4}?$", new_value)
                if m:
                    sep = m.groups()
                    evt.Veto()
                    pos1 = new_value.index(sep[0])
                    pos2 = new_value.rindex(sep[1])
                    mon = int(new_value[0:pos1])
                    day = int(new_value[pos1 + 1:pos2])
                    year = int(new_value[pos2 + 1:])
                    try:
                        in_date = date(year, mon, day)
                    except:
                        str = "%s is not a valid date string" % (new_value)
                        ret_val = self.DisplayMsg(str)
                    else:
                        self.edited = True
                        in_date_string = "%04s-%02d-%02d" % (year, mon, day)
                        evt.String = in_date_string
                else:
                    str = "%s is not a valid date string" % (new_value)
                    ret_val = self.DisplayMsg(str)
        elif ret_val == wx.OK and self.col_info[col][self.TYPE_COL] == self.DATE_TIME_TYPE:
            if new_value == "" and self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS:
                evt.Veto()
            else:
                # TODO  move regular expression for datetime format to new object
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
                    day = int(new_value[pos1 + 1:pos2])
                    year = int(new_value[pos2 + 1:pos3])
                    hour = int(new_value[pos3 + 1:pos4])
                    min = int(new_value[pos4 + 1:pos5])
                    sec = int(new_value[pos5 + 1:])
                    try:
                        in_datetime = datetime(year, mon, day, hour, min, sec)
                    except:
                        str = "%s is not a valid datetime string" % (new_value)
                        ret_val = self.DisplayMsg(str)
                    else:
                        self.edited = True
                        in_datetime_string = "%04s-%02d-%02d %02d:%02d:%02d" % (year, mon, day, hour, min, sec)
                        evt.String = in_datetime_string
                else:
                    str = "%s is not a valid datetime string" % (new_value)
                    ret_val = self.DisplayMsg(str)
        elif ret_val == wx.OK and self.col_info[col][self.TYPE_COL] == self.STRING_TYPE:
            pass
        else:
            if ret_val != wx.OK:
                str = "Warning: cellchanging not allowed for cell %d %d!" % (row, col)
                ret_val = self.DisplayMsg(str)
        if ret_val == wx.OK:
            self.getFrame().assetchange(evt)
            self.getFrame().redraw_all(row)  # only redraw current row
        else:
            evt.Veto()

    def set_properties(self, frame):
        frame.SetTitle("PyAsset: Asset")
        self.total_width = 60  # non-zero start value to account for record number and status lines of frame!
        for i in range(len(self.columnNames)):
            self.SetColLabelValue(i, self.columnNames[i])
            cur_width = self.getColWidth(i)
            self.total_width += cur_width
            self.SetColSize(i, cur_width)
        return self.total_width

    def OnCellLeftClick(self, evt):
        row = evt.GetRow()
        col = evt.GetCol()
        pos = evt.GetPosition()
        if row < len(self.getFrame().assets):
            if col == self.ACCT_NAME_COL:
                self.getFrame().add_transaction_frame(row, col)
            else:
                print("OnCellLeftClick: AssetGrid (%d,%d) %s\n" % (row, col, pos))
            evt.Skip()

    def OnCellRightClick(self, evt):
        print("OnCellRightClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                  evt.GetCol(),
                                                  evt.GetPosition()))
        evt.Skip()

    def OnCellLeftDClick(self, evt):
        print("OnCellLeftDClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                  evt.GetCol(),
                                                  evt.GetPosition()))
        evt.Skip()

    def OnCellRightDClick(self, evt):
        print("OnCellRightDClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                   evt.GetCol(),
                                                   evt.GetPosition()))
        evt.Skip()

    def OnLabelLeftClick(self, evt):
        print("OnLabelLeftClick: AssetGrid (%d,%d) %s\n" % (evt.GetRow(),
                                                  evt.GetCol(),
                                                  evt.GetPosition()))
        evt.Skip()

    def OnLabelRightClick(self, evt):
        print("OnLabelRightClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                   evt.GetCol(),
                                                   evt.GetPosition()))
        evt.Skip()

    def OnLabelLeftDClick(self, evt):
        print("OnLabelLeftDClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                   evt.GetCol(),
                                                   evt.GetPosition()))
        evt.Skip()

    def OnLabelRightDClick(self, evt):
        print("OnLabelRightDClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                    evt.GetCol(),
                                                    evt.GetPosition()))
        evt.Skip()

    def OnRowSize(self, evt):
        print("OnRowSize: row %d, %s\n" % (evt.GetRowOrCol(),
                                           evt.GetPosition()))
        evt.Skip()

    def OnColSize(self, evt):
        print("OnColSize: col %d, %s\n" % (evt.GetRowOrCol(),
                                           evt.GetPosition()))
        evt.Skip()

    def OnRangeSelect(self, evt):
        if evt.Selecting():
            msg = 'Selected'
        else:
            msg = 'Deselected'
        print("OnRangeSelect: %s  top-left %s, bottom-right %s\n" % (msg, evt.GetTopLeftCoords(),
                                                                     evt.GetBottomRightCoords()))
        evt.Skip()

    def OnCellChange(self, evt):
        print("OnCellChange: (%d,%d) %s\n" % (evt.GetRow(), evt.GetCol(), evt.GetPosition()))

        # Show how to stay in a cell that has bad data.  We can't just
        # call SetGridCursor here since we are nested inside one so it
        # won't have any effect.  Instead, set coordinates to move to in
        # idle time.
        try:
            value = self.GetCellValue(evt.GetRow(), evt.GetCol())
        except:
            value = 'no good'

        if value == 'no good':
            self.moveTo = evt.GetRow(), evt.GetCol()

    def OnSelectCell(self, evt):
        if evt.Selecting():
            msg = 'Selected'
        else:
            msg = 'Deselected'
        print("OnSelectCell: %s (%d,%d) %s\n" % (msg, evt.GetRow(),
                                                 evt.GetCol(), evt.GetPosition()))

        # Another way to stay in a cell that has a bad value...
        row = self.GetGridCursorRow()
        col = self.GetGridCursorCol()

        if self.IsCellEditControlEnabled():
            self.HideCellEditControl()
            self.DisableCellEditControl()

        try:
            value = self.GetCellValue(row, col)
        except:
            value = 'no good'

        if value == 'no good':
            return  # cancels the cell selection

        evt.Skip()

    def OnEditorShown(self, evt):
        if evt.GetRow() == 6 and evt.GetCol() == 3 and \
                wx.MessageBox("Are you sure you wish to edit this cell?",
                              "Checking", wx.YES_NO) == wx.NO:
            evt.Veto()
            return

        print("OnEditorShown: (%d,%d) %s\n" % (evt.GetRow(), evt.GetCol(),
                                               evt.GetPosition()))
        evt.Skip()

    def OnEditorHidden(self, evt):
        if evt.GetRow() == 6 and evt.GetCol() == 3 and \
                wx.MessageBox("Are you sure you wish to  finish editing this cell?",
                              "Checking", wx.YES_NO) == wx.NO:
            evt.Veto()
            return

        print("OnEditorHidden: (%d,%d) %s\n" % (evt.GetRow(),
                                                evt.GetCol(),
                                                evt.GetPosition()))
        evt.Skip()

    def OnEditorCreated(self, evt):
        print("OnEditorCreated: (%d, %d) %s\n" % (evt.GetRow(),
                                                  evt.GetCol(),
                                                  evt.GetControl()))
