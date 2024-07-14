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
#  08/07/2021     Version v0.2

import wx
import wx.grid as grd
import re
from datetime import date, datetime
from Date import Date

class TransactionGrid(grd.Grid):
    def __init__(self, frame, panel, **keywords):
        self.dateFormat = Date.get_global_date_format(Date)
        self.dateSep = Date.get_global_date_sep(self)
        self.grid = grd.Grid.__init__(self, panel, **keywords)
        self.frame = frame
        self.Bind(grd.EVT_GRID_CELL_CHANGING, self.cellchanging)

        # test all the events
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
        #self.Bind(grd.EVT_GRID_SELECT_CELL, self.OnSelectCell)

        self.Bind(grd.EVT_GRID_EDITOR_SHOWN, self.OnEditorShown)
        self.Bind(grd.EVT_GRID_EDITOR_HIDDEN, self.OnEditorHidden)
        self.Bind(grd.EVT_GRID_EDITOR_CREATED, self.OnEditorCreated)

        # Define the layout of the grid in the frame
        self.TRANS_PMT_METHOD_COL = 0
        self.TRANS_CHECK_NUM_COL = 1
        self.TRANS_PAYEE_COL = 2
        self.TRANS_AMOUNT_COL = 3
        self.TRANS_ACTION_COL = 4
        self.TRANS_VALUE_COL = 5
        self.TRANS_SCHED_DATE_COL = 6
        self.TRANS_DUE_DATE_COL = 7
        self.TRANS_STATE_COL = 8
        self.TRANS_COMMENT_COL = 9
        self.TRANS_MEMO_COL = 10

        # Define the widths of the columns in the grid
        TRANS_PMT_METHOD_COL_WIDTH = 80
        TRANS_CHECK_NUM_COL_WIDTH = 60
        TRANS_PAYEE_COL_WIDTH = 300
        TRANS_AMOUNT_COL_WIDTH = 60
        TRANS_ACTION_COL_WIDTH = 50
        TRANS_VALUE_COL_WIDTH = 65
        TRANS_SCHED_DATE_COL_WIDTH = 70
        TRANS_DUE_DATE_COL_WIDTH = 70
        TRANS_STATE_COL_WIDTH = 70
        TRANS_COMMENT_COL_WIDTH = 300
        TRANS_MEMO_COL_WIDTH = 300

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
                         [self.TRANS_PMT_METHOD_COL, TRANS_PMT_METHOD_COL_WIDTH, self.STRING_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.TRANS_CHECK_NUM_COL, TRANS_CHECK_NUM_COL_WIDTH, self.STRING_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.TRANS_PAYEE_COL, TRANS_PAYEE_COL_WIDTH, self.STRING_TYPE, self.EDITABLE, self.NO_ZERO_SUPPRESS],
                         [self.TRANS_AMOUNT_COL, TRANS_AMOUNT_COL_WIDTH, self.DOLLAR_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.TRANS_ACTION_COL, TRANS_ACTION_COL_WIDTH, self.STRING_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.TRANS_VALUE_COL, TRANS_VALUE_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE, self.NO_ZERO_SUPPRESS],
                         [self.TRANS_SCHED_DATE_COL, TRANS_SCHED_DATE_COL_WIDTH, self.DATE_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.TRANS_DUE_DATE_COL, TRANS_DUE_DATE_COL_WIDTH, self.DATE_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.TRANS_STATE_COL, TRANS_STATE_COL_WIDTH, self.STRING_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.TRANS_COMMENT_COL, TRANS_COMMENT_COL_WIDTH, self.STRING_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
                         [self.TRANS_MEMO_COL, TRANS_MEMO_COL_WIDTH, self.STRING_TYPE, self.NOT_EDITABLE, self.ZERO_SUPPRESS],
        ]

        return

    def getNumLayoutCols(self):
        return len(self.col_info)

    def getDateFormat(self):
        return self.dateFormat

    def setDateFormat(self):
        self.dateFormat = Date.get_global_date_format(Date)

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
            print("Bad value for zero_suppress:" + zero_suppress + " Ignored! Should be either " + self.ZERO_SUPPRESS + " or " + self.NO_ZERO_SUPPRESS_)
        else:
            self.col_info[i][self.ZERO_SUPPRESS_COL] = zero_suppress

    def getFrame(self):
        return self.Parent

    def getColMethod(self, row, i):
        if i == self.TRANS_PMT_METHOD_COL:
            return self.frame.transactions[row].get_pmt_method()
        elif i == self.TRANS_CHECK_NUM_COL:
            return self.frame.transactions[row].get_check_num()
        elif i == self.TRANS_PAYEE_COL:
            return self.frame.transactions[row].get_payee()
        elif i == self.TRANS_AMOUNT_COL:
            return self.frame.transactions[row].get_amount()
        elif i == self.TRANS_ACTION_COL:
            return self.frame.transactions[row].get_action()
        elif i == self.TRANS_VALUE_COL:
            return self.frame.transactions[row].get_current_value()
        elif i == self.TRANS_DUE_DATE_COL:
            return self.frame.transactions[row].get_due_date()
        elif i == self.TRANS_SCHED_DATE_COL:
            return self.frame.transactions[row].get_sched_date()
        elif i == self.TRANS_STATE_COL:
            return self.frame.transactions[row].get_state()
        elif i == self.TRANS_COMMENT_COL:
            return self.frame.transactions[row].get_comment()
        elif i == self.TRANS_MEMO_COL:
            return self.frame.transactions[row].get_memo()
        else:
            return "??"

    def setColMethod(self, row, i, value):
        ret_val = "??"
        if i == self.TRANS_PMT_METHOD_COL:
            ret_val = self.frame.transactions[row].set_pmt_method(value)
        elif i == self.TRANS_CHECK_NUM_COL:
            ret_val = self.frame.transactions[row].set_check_num(value)
        elif i == self.TRANS_PAYEE_COL:
            ret_val = self.frame.transactions[row].set_payee(value)
        elif i == self.TRANS_AMOUNT_COL:
            ret_val = self.frame.transactions[row].set_amount(value)
        elif i == self.TRANS_ACTION_COL:
            ret_val = self.frame.transactions[row].set_action(value)
        elif i == self.TRANS_VALUE_COL:
            ret_val = self.frame.transactions[row].set_current_value(value)
        elif i == self.TRANS_DUE_DATE_COL:
            ret_val = self.frame.transactions[row].set_due_date(value)
        elif i == self.TRANS_SCHED_DATE_COL:
            ret_val = self.frame.transactions[row].set_sched_date(value)
        elif i == self.TRANS_STATE_COL:
            ret_val = self.frame.transactions[row].set_state(value)
        elif i == self.TRANS_COMMENT_COL:
            ret_val = self.frame.transactions[row].set_comment(value)
        elif i == self.TRANS_MEMO_COL:
            ret_vak = self.frame.transactions[row].set_memo(value)
        return ret_val

    def getCurrTrans(self, row, col):
        col = col                                   # JJG 1/1/2024 So editor will do folding right!
        return self.getFrame().transactions[row]

    def getNumLayoutCols(self):
        return len(self.col_info)

#TODO Investigate making GridCell Renderers be true cell renderers vice functions!

    def GridCellErrorRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        self.SetCellAlignment(row, col, wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        tableValue = "Bad: %s" % (cellValue)
        self.frame.trans_grid.SetCellValue(row, col, tableValue)

    def GridCellDefaultRenderer(self, row, col):
        self.SetCellTextColour(row, col, 'black')
        self.SetReadOnly(row, col, self.getColEdit(col))
        self.SetCellAlignment(row, col, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        cellValue = str(self.getColMethod(row, col))
        if self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS and (cellValue == "0" or cellValue == "0.00" or cellValue == "None"):
            cellValue = ""
        # Note that this doesn't display the value in the grid so that if further formatting is required, user won't see default formatting first!
        return cellValue

    def GridCellDollarRenderer(self, row, col):
        cellValue = str(self.getColMethod(row,col))
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
            field_width = 13                                    # Assume largest number is 999,999.99 which needs 10 places so add a couple for safety!
            num_chars = len(str_out)
            num_blanks = field_width - num_chars - 1
            blanks = "" * num_blanks
            format_start = "%%%1ds" % (num_blanks)
            num_format = "%%%1ds" %(num_chars)
            if negative:
                self.frame.trans_grid.SetCellTextColour(row, col, 'red')
                format_str = format_start + "-$" + num_format
                tableValue = format_str % (blanks, str_out)
            else:
                format_str = format_start + " $" + num_format
                tableValue = format_str % (blanks, str_out)
        self.frame.trans_grid.SetCellValue(row, col, tableValue)

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
        self.frame.trans_grid.SetCellValue(row, col, tableValue)

    def GridCellDateRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        if cellValue == None or cellValue == "None":
            tableValue = ""
        elif self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS and (cellValue == "0" or cellValue == ""):
            tableValue = ""
        else:
            returned_date = Date.parse_date(self, cellValue, Date.get_global_date_format(Date))
            if returned_date != None:
                tableDate = wx.DateTime.FromDMY(returned_date["day"], returned_date["month"] - 1, returned_date["year"])
                dateFormat = Date.get_global_date_format(Date)
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
                        tableValue = tableValue + "%s" % (date_sep)
            else:
                tableValue = ""
                self.DisplayMsg("Bad cell date for row %d col %d ignored: %s" % (row, col, cellValue))
        self.SetCellAlignment(row, col, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.frame.trans_grid.SetCellValue(row, col, tableValue)

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
        if self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS and (cellValue == "0" or cellValue == "0.00" or cellValue == "None"):
            tableValue = ""
        else:
            tableValue = cellValue
        self.frame.trans_grid.SetCellValue(row, col, tableValue)

    def DisplayMsg(self, str):
        d = wx.MessageDialog(self, str, "Error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()
        return wx.CANCEL

    def cellchanging(self, evt):
        row = evt.GetRow()
        col = evt.GetCol()
        ret_val = wx.OK
        new_value = evt.String.strip()
        if new_value == "":
            col_type = self.col_info[col][self.TYPE_COL]
            if col_type == self.DOLLAR_TYPE: new_value = "0.00"
        if row < 0 or row >= len(self.frame.transactions):
            str = "Warning: cellchanging on bad cell %d %d!" % (row, col)
            ret_val =  self.DisplayMsg(str)
        elif self.col_info[col][self.EDIT_COL] == self.NOT_EDITABLE:
            str = "Warning: Changes not allowed for column %s!" % (self.getColName(col))
            ret_val =  self.DisplayMsg(str)
        if ret_val == wx.OK and self.col_info[col][self.TYPE_COL] == self.DOLLAR_TYPE:
            #TODO  move regular expression for dollar format to new object
            m = re.match("^-?\$?\d{1,3}(\,?\d{3})*(\.\d{2})?$", new_value)
            if m:
                self.edited = True
                dollar_amount = new_value.replace("$", "").replace(",", "")
                if "." not in dollar_amount:
                    dollar_amount += ".00"
                    evt.Veto()
                    self.frame.trans_grid.SetCellValue(row, col, dollar_amount)
                evt.String = dollar_amount
            else:
                str = "%s is not a valid dollar string" % (new_value)
                ret_val =  self.DisplayMsg(str)
        elif ret_val == wx.OK and self.col_info[col][self.TYPE_COL] == self.RATE_TYPE:
            #TODO  move regular expression for rate format to new object
            m = re.match("^\d{1,3}(\.\d{1,3})?\%?$", new_value)
            if m:
                self.edited = True
                evt.Veto()
                rate_amount = Round(float(new_value.replace("%", ""))/100.0, 2)
                evt.String = "%8.5f" % (rate_amount)
            else:
                str = "%s is not a valid rate string" % (new_value)
                ret_val = self.DisplayMsg(str)
        elif ret_val == wx.OK and self.col_info[col][self.TYPE_COL] == self.DATE_TYPE:
            if new_value == "" and self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS:
                evt.Veto()
            else:
                dateFormat = Date.get_global_date_format(Date)
                date_sep = Date.get_global_date_sep(self)
                input_date = new_value.split(date_sep)
                dateParts = dateFormat.split(date_sep)
                tableValue = ""
                if len(input_date) == 3:
                    for i in range(len(dateParts)):
                        if dateParts[i] == "%m":
                            tableValue = tableValue + "%02d" % (int(input_date[i]))
                        elif dateParts[i] == "%d":
                            tableValue = tableValue + "%02d" % (int(input_date[i]))
                        elif dateParts[i] == "%Y":
                            tableValue = tableValue + "%04d" % (int(input_date[i]))
                        elif dateParts[i] == "%y":
                            # assume all 2 digit years are in the range 2000 <= year < 2099.  Don't expect this software to be used in the year 2100!! JJG 07/08/2021
                            tableValue = tableValue + "%04d" % (2000 + int(input_date[i]))
                        if i < len(dateParts)-1:
                            tableValue = tableValue + "%s" % (date_sep)
                evt.Veto()
                try:
                    returned_date = Date.parse_date(self, tableValue, Date.get_global_date_format(Date))
                except:
                    str = "%s is not a valid date string" % (new_value)
                    ret_val = self.DisplayMsg(str)
                else:
                    self.edited = True
                    evt.String = tableValue
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
                        self.edited = True
                        in_datetime_string = "%04s-%02d-%02d %02d:%02d:%02d" % (year, mon, day, hour, min, sec)
                        evt.String = in_datetime_string
                else:
                    str = "%s is not a valid datetime string" % (new_value)
                    ret_val = self.DisplayMsg(str)
        elif ret_val == wx.OK and self.col_info[col][self.TYPE_COL] == self.STRING_TYPE:
            if col == self.TRANS_ACTION_COL:
                if new_value != "+" and new_value != "-":
                    str = "%s is not a valid action string" % (new_value)
                    ret_val = self.DisplayMsg(str)
            else:
                pass
        else:
            if ret_val != wx.OK:
                str = "Warning: cellchanging not allowed for cell %d %d!" % (row, col)
                ret_val =  self.DisplayMsg(str)
        if ret_val == wx.OK:
            print("TransactionGrid: Change detected for row", row, ", col", col)
            self.frame.assetchange(row, col, new_value)
            self.frame.redraw_all()
        else:
            evt.Veto()

    def setValue(self, row, colName, cellValue):
        found = False
        for i in range(len(self.columnNames)):
            if self.columnNames[i] == colName:
                found = True
                break
        if found:
            self.SetCellValue(row, i, cellValue)

    def set_properties(self, frame):
        frame.statusbar.SetStatusWidths([-1])
        statusbar_fields = [""]
        self.columnNames = ["Pmt Method", "Chk #", "Payee", "Amount", "Action", "Value", "Sched Date", "Due Date", "State", "Comment", "Memo"];

        for i in range(len(statusbar_fields)):
            frame.statusbar.SetStatusText(statusbar_fields[i], i)
#        self.CreateGrid(0, len(self.columnNames))
        self.value_width = 60  # non-zero start value to account for record number of TransactionGrid frame!
        for i in range(len(self.columnNames)):
            self.SetColLabelValue(i, self.columnNames[i])
            cur_width = self.getColWidth(i)
            self.value_width += cur_width
            self.SetColSize(i, cur_width)
        return self.value_width

    def update_transaction_grid_dates(self, oldDateFormat, newDateFormat):
        self.edited = True
        nassets = len(self.assets)
        for row in range(nassets):           
            for col in range(self.assetGrid.getNumLayoutCols()):
                cellValue = self.assetGrid.GridCellDefaultRenderer(row, col)
                if cellValue != None and cellValue != 'None':
                    cellType = self.assetGrid.getColType(col)
                    if (cellType == self.assetGrid.DATE_TYPE or cellType == self.assetGrid.DATE_TIME_TYPE) and oldDateFormat != None and newDateFormat != None:
                        tableValue = Date.convertDateFormat(Date, cellValue, oldDateFormat, newDateFormat)["str"]
                        if cellType == self.assetGrid.DATE_TIME_TYPE:
                            time = cellValue.split(" ")[1]
                            tableValue += " " + time
                        if tableValue != "":
                            curr_asset = self.assetGrid.getCurrAsset(row, col)
                            if self.assetGrid.setColMethod(curr_asset, row, col, tableValue) != "??":
                                if cellType == self.assetGrid.DATE_TIME_TYPE:
                                    self.assetGrid.GridCellDateTimeRenderer(row, col)
                                else:
                                    self.assetGrid.GridCellDateRenderer(row, col)
                            else:
                                print("update_asset_grid_dates: Warning: unknown method for cell! row, ", row, " col ", col, " Skipping!")

    def close(self, *args):
        self.Unbind(grd.EVT_GRID_CELL_CHANGING)

        # Unbind all the events
        self.Unbind(grd.EVT_GRID_CELL_LEFT_CLICK)
        self.Unbind(grd.EVT_GRID_CELL_RIGHT_CLICK)
        self.Unbind(grd.EVT_GRID_CELL_LEFT_DCLICK)
        self.Unbind(grd.EVT_GRID_CELL_RIGHT_DCLICK)

        self.Unbind(grd.EVT_GRID_LABEL_LEFT_CLICK)
        self.Unbind(grd.EVT_GRID_LABEL_RIGHT_CLICK)
        self.Unbind(grd.EVT_GRID_LABEL_LEFT_DCLICK)
        self.Unbind(grd.EVT_GRID_LABEL_RIGHT_DCLICK)

        self.Unbind(grd.EVT_GRID_ROW_SIZE)
        self.Unbind(grd.EVT_GRID_COL_SIZE)

        self.Unbind(grd.EVT_GRID_RANGE_SELECT)
        #self.Unbind(grd.EVT_GRID_CELL_CHANGE)
        #self.Unbind(grd.EVT_GRID_SELECT_CELL)

        self.Unbind(grd.EVT_GRID_EDITOR_SHOWN)
        self.Unbind(grd.EVT_GRID_EDITOR_HIDDEN)
        self.Unbind(grd.EVT_GRID_EDITOR_CREATED)

        self.Destroy()

    def OnCellLeftClick(self, evt):
        print("OnCellLeftClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                 evt.GetCol(),
                                                 evt.GetPosition()))
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
        print("OnLabelLeftClick: (%d,%d) %s\n" % (evt.GetRow(),
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
        value = self.GetCellValue(evt.GetRow(), evt.GetCol())

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

        value = self.GetCellValue(row, col)

        if value == 'no good 2':
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

