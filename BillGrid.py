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
#  04/15/2023     Initial version v0.1

import wx
import wx.grid as grd
import re
from datetime import date, datetime
from Date import Date
from BillList import BillList

class BillGrid(wx.Frame):
#  self.bills_frame = BillGrid(self, self.bills.bills, title="PyAsset: Bills", filename=self.bill_filename) # Current call from AssetFrame.py looks like this JJG 9/15/2025
    def __init__(self, *args, **kwargs):
        bills = args[1]
        try:
            title = kwargs["title"]
        except:
            title = kwargs["title"] = "pyAsset: Bills"
        try:
            filename = kwargs["filename"]
        except:
            filename = kwargs["filename"] = ""
        self.dateFormat = Date.get_global_date_format(self)
        self.dateSep = Date.get_global_date_sep(self)
        self.columnNames = ["Type", "Payee", "Amount", "Min Due", "Due Date", "Sched Date", "Pmt Acct", "Pmt Method", "Frequency"]
        self.bills = BillList()
        for bill in bills:
            self.bills.insert(bill)
        self.maxRows = self.getNumBills()
        self.maxCols = self.getNumColumns()
        super(BillGrid, self).__init__(args[0], title=title, size=(self.maxRows, self.maxCols))
        self.edited = False

        self.Bind(wx.EVT_CLOSE,self.close) 

        # Define all needed event bindings
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
        self.BILL_TYPE_COL = Headers.index("Type")
        self.BILL_PAYEE_COL = Headers.index("Payee")
        self.BILL_AMOUNT_COL = Headers.index("Amount")
        self.BILL_MIN_DUE_COL = Headers.index("Min Due")
        self.BILL_DUE_DATE_COL = Headers.index("Due Date")
        self.BILL_SCHED_DATE_COL = Headers.index("Sched Date")
        self.BILL_PMT_ACCT_COL = Headers.index("Pmt Acct")
        self.BILL_PMT_METHOD_COL = Headers.index("Pmt Method")
        self.BILL_FREQUENCY_COL = Headers.index("Frequency")

        # Define the widths of the columns in the grid
        BILL_TYPE_COL_WIDTH = 150
        BILL_PAYEE_COL_WIDTH = 300
        BILL_AMOUNT_COL_WIDTH = 75
        BILL_MIN_DUE_COL_WIDTH = 75
        BILL_DUE_DATE_COL_WIDTH = 100
        BILL_SCHED_DATE_COL_WIDTH = 100
        BILL_PMT_ACCT_COL_WIDTH = 150
        BILL_PMT_METHOD_COL_WIDTH = 80
        BILL_FREQUENCY_COL_WIDTH = 5
        BILL_PAYMENT_COL_WIDTH = 9

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
            [self.BILL_TYPE_COL, BILL_TYPE_COL_WIDTH, self.STRING_TYPE, self.NOT_EDITABLE, self.NO_ZERO_SUPPRESS],
            [self.BILL_PAYEE_COL, BILL_PAYEE_COL_WIDTH, self.STRING_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
            [self.BILL_AMOUNT_COL, BILL_AMOUNT_COL_WIDTH, self.DOLLAR_TYPE, self.EDITABLE, self.NO_ZERO_SUPPRESS],
            [self.BILL_MIN_DUE_COL, BILL_MIN_DUE_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE, self.NO_ZERO_SUPPRESS],
            [self.BILL_DUE_DATE_COL, BILL_DUE_DATE_COL_WIDTH, self.DATE_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
            [self.BILL_SCHED_DATE_COL, BILL_SCHED_DATE_COL_WIDTH, self.DATE_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
            [self.BILL_PMT_ACCT_COL, BILL_PMT_ACCT_COL_WIDTH, self.STRING_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
            [self.BILL_PMT_METHOD_COL, BILL_PMT_METHOD_COL_WIDTH, self.STRING_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
            [self.BILL_FREQUENCY_COL, BILL_FREQUENCY_COL_WIDTH, self.STRING_TYPE, self.EDITABLE, self.ZERO_SUPPRESS],
        ]

        self.make_widgets()
        self.redraw_all() 

    def redraw_all(self, index=None):
        if index == None:
            index = -1
        nbills = len(self.bills)
        start_range = 0
        end_range = nbills
        if index == -1:
            nrows = self.bill_grid.GetNumberRows()
            if nrows > 0 and (index == None or index == -1):
                self.bill_grid.DeleteRows(0, nrows)
                nrows = 0
            if nrows < nbills:
                rows_needed = nbills - nrows
                self.bill_grid.AppendRows(rows_needed)
        else:
            start_range = index
            end_range = start_range + 1

        # Display the bills
        for row in range(start_range, end_range):
            for col in range(self.getNumColumns()):
                ret_val = wx.OK
                if row < 0 or row >= nbills:
                    str = "Warning: skipping redraw on bad cell %d %d!" % (row, col)
                    ret_val = self.DisplayMsg(str)
                if ret_val != wx.OK:
                    continue

                cellType = self.getColType(col)
                if cellType == self.DOLLAR_TYPE:
                    self.GridCellDollarRenderer(row, col)
                elif cellType == self.RATE_TYPE:
                    self.GridCellPercentRenderer(row, col)
                elif cellType == self.DATE_TYPE:
                    self.GridCellDateRenderer(row, col)
                elif cellType == self.DATE_TIME_TYPE:
                    self.GridCellDateTimeRenderer(row, col)
                elif cellType == self.STRING_TYPE:
                    self.GridCellStringRenderer(row, col)
                else:
                    self.GridCellErrorRenderer(row, col)

        cursorCell = index
        if index == -1:
            if nbills > 0:
                cursorCell = nbills - 1
            else:
                cursorCell = 0
        else:
            if index > nbills:
                cursorCell = nbills - 1
            else:
                cursorCell = index
        self.bill_grid.SetGridCursor(cursorCell, 0)
        self.bill_grid.MakeCellVisible(cursorCell, True)
        self.Show()

    def getNumBills(self):
        return len(self.bills)

    def getMinNumRows(self):
        return(self.minNumRows)

    def getNumColumns(self):
        return(len(self.columnNames))

    def getColName(self, col):
        return self.bill_grid.GetColLabelValue(col)

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

    def do_layout(self):
        self.bill_grid.Layout()
        self.bill_grid.Show()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.bill_grid, proportion=1, flag=wx.EXPAND | wx.ALL)
        self.panel.SetSizerAndFit(sizer)        
        self.Fit()
        self.Show()

    def getColMethod(self, row, i):
        currBill = self.bills[row]
        if i == self.BILL_TYPE_COL:
            return currBill.get_type()
        elif i == self.BILL_PAYEE_COL:
            return currBill.get_payee()
        elif i == self.BILL_AMOUNT_COL:
            return currBill.get_amount()
        elif i == self.BILL_MIN_DUE_COL:
            return currBill.get_min_due()
        elif i == self.BILL_DUE_DATE_COL:
            return currBill.get_due_date()
        elif i == self.BILL_SCHED_DATE_COL:
            return currBill.get_sched_date()
        elif i == self.BILL_PMT_ACCT_COL:
            return currBill.get_pmt_acct()
        elif i == self.BILL_PMT_METHOD_COL:
            return currBill.get_pmt_method()
        elif i == self.BILL_FREQUENCY_COL:
            return currBill.get_pmt_frequency()
        else:
            return "??"

    def getNumLayoutCols(self):
        return len(self.col_info)

    def make_menus(self):
        self.bill_grid.menubar = wx.MenuBar()
        self.SetMenuBar(self.bill_grid.menubar)
        self.make_filemenu()
        self.make_editmenu()
        self.make_helpmenu()

    def make_filemenu(self):
        self.filemenu = wx.Menu()
        ID_IMPORT_CSV = wx.NewId()
        ID_IMPORT_XLSM = wx.NewId()
        ID_EXPORT_TEXT = wx.NewId()
        ID_ARCHIVE = wx.NewId()
        self.filemenu.Append(wx.ID_OPEN, "Open\tCtrl-o",
                             "Open a new bill file", wx.ITEM_NORMAL)
        self.filemenu.Append(wx.ID_SAVE, "Save\tCtrl-s",
                             "Save the current bills", wx.ITEM_NORMAL)
        self.filemenu.Append(wx.ID_SAVEAS, "Save As",
                             "Save the current bills under a different name", wx.ITEM_NORMAL)
        self.filemenu.Append(ID_IMPORT_CSV, "Import CSV\tCtrl-c",
                             "Import bills from a CSV file",
                             wx.ITEM_NORMAL)
#        self.filemenu.Append(ID_IMPORT_XLSM, "Import XLSM\tCtrl-X",
#                             "Import bills from an EXCEL file with Macros",
#                             wx.ITEM_NORMAL)
        self.filemenu.Append(ID_EXPORT_TEXT, "Export Text",
                             "Export the current bills as a text file",
                             wx.ITEM_NORMAL)
        self.filemenu.Append(ID_ARCHIVE, "Archive",
                             "Archive bills older than a specified date",
                             wx.ITEM_NORMAL)
        self.filemenu.Append(wx.ID_CLOSE, "Close\tCtrl-w",
                             "Close the current file", wx.ITEM_NORMAL)
        self.filemenu.Append(wx.ID_EXIT, "Exit\tCtrl-q",
                             "Exit PyAsset", wx.ITEM_NORMAL)
        self.bill_grid.menubar.Append(self.filemenu, "&File")
        self.Bind(wx.EVT_MENU, self.load_file, None, wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.save_file, None, wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.save_as_file, None, wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.import_CSV_file, None, ID_IMPORT_CSV)
        #self.Bind(wx.EVT_MENU, self.export_text, None, ID_EXPORT_TEXT)
        self.Bind(wx.EVT_MENU, self.archive, None, ID_ARCHIVE)
        self.Bind(wx.EVT_MENU, self.close, None, wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.quit, None, wx.ID_EXIT)

    def make_editmenu(self):
        ID_SORT = wx.NewId()
        ID_MARK_ENTRY = wx.NewId()
        ID_VOID_ENTRY = wx.NewId()
        ID_DELETE_ENTRY = wx.NewId()
        ID_RECONCILE = wx.NewId()
        self.editmenu = wx.Menu()
        self.editmenu.Append(wx.ID_NEW, "New Entry\tCtrl-n",
                             "Create a new bill in the register",
                             wx.ITEM_NORMAL)
        self.editmenu.Append(ID_SORT, "Sort Entries",
                             "Sort entries", wx.ITEM_NORMAL)
        self.editmenu.Append(ID_MARK_ENTRY, "Mark Cleared\tCtrl-m",
                             "Mark the current bill cleared",
                             wx.ITEM_NORMAL)
        self.editmenu.Append(ID_VOID_ENTRY, "Void Entry\tCtrl-v",
                             "", wx.ITEM_NORMAL)
        self.editmenu.Append(ID_DELETE_ENTRY, "Delete Entry",
                             "Delete the current bill", wx.ITEM_NORMAL)
        self.editmenu.Append(ID_RECONCILE, "Reconcile\tCtrl-r",
                             "Reconcile your Asset", wx.ITEM_NORMAL)
        self.bill_grid.menubar.Append(self.editmenu, "&Edit")
        self.Bind(wx.EVT_MENU, self.newentry, None, wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.sort, None, ID_SORT)
        self.Bind(wx.EVT_MENU, self.markcleared, None, ID_MARK_ENTRY)
        self.Bind(wx.EVT_MENU, self.voidentry, None, ID_VOID_ENTRY)
        self.Bind(wx.EVT_MENU, self.deleteentry, None, ID_DELETE_ENTRY)
        return

    def make_helpmenu(self):
        ID_HELP = wx.NewId()
        self.helpmenu = wx.Menu()
        self.helpmenu.Append(wx.ID_ABOUT, "About",
                             "About PyAsset", wx.ITEM_NORMAL)
        self.helpmenu.Append(ID_HELP, "Help\tCtrl-h",
                             "PyAsset Help", wx.ITEM_NORMAL)

        self.bill_grid.menubar.Append(self.helpmenu, "&Help")
        self.Bind(wx.EVT_MENU, self.about, None, wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.gethelp, None, ID_HELP)

    def make_widgets(self):
        self.panel = wx.Panel(self)
        self.bill_grid = wx.grid.Grid(self.panel)
        self.set_properties()
        self.make_menus()
        self.do_layout()

    # TODO Investigate making GridCell Renderers be true cell renderers vice functions!

    def GridCellErrorRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        self.SetCellAlignment(row, col, wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        tableValue = "Bad: %s" % (cellValue)
        self.bill_grid.SetCellValue(row, col, tableValue)

    def GridCellDefaultRenderer(self, row, col):
        self.bill_grid.SetCellTextColour(row, col, 'black')
        self.bill_grid.SetReadOnly(row, col, self.getColEdit(col))
        self.bill_grid.SetCellAlignment(row, col, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        cellValue = str(self.getColMethod(row, col))
        if self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS and (cellValue == "0" or cellValue == "0.00"):
            cellValue = ""
        # Note that this doesn't display the value in the grid so that if further formatting is required, user won't see default formatting first!
        return cellValue

    def GridCellDollarRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        self.bill_grid.SetCellAlignment(row, col, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
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
                self.bill_grid.SetCellTextColour(row, col, 'red')
                format_str = format_start + "-$" + num_format
                tableValue = format_str % (blanks, str_out)
            else:
                self.bill_grid.SetCellTextColour(row, col, 'black')
                format_str = format_start + " $" + num_format
                tableValue = format_str % (blanks, str_out)
        self.bill_grid.SetCellValue(row, col, tableValue)

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
        self.bill_grid.SetCellValue(row, col, tableValue)

    def GridCellDateRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        if cellValue == None or cellValue == "None":
            tableValue = ""
        elif self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS and (cellValue == "0" or cellValue == ""):
            tableValue = ""
        else:
            parsed_cell_date = Date.parse_date(self, cellValue, Date.get_global_date_format(self))
            if parsed_cell_date != None:
                tableDate = wx.DateTime.FromDMY(parsed_cell_date["day"], parsed_cell_date["month"]-1, parsed_cell_date["year"])
                dateFormat = Date.get_global_date_format(self)
                date_sep = Date.get_global_date_sep(self)
                dateParts = dateFormat.split(date_sep)
                tableValue = ""
                for i in range(len(dateParts)):
                    if dateParts[i] == "%m":
                        tableValue = tableValue + "%02d" % (int(parsed_cell_date["month"]))
                    elif dateParts[i] == "%d":
                        tableValue = tableValue + "%02d" % (int(parsed_cell_date["day"]))
                    elif dateParts[i] == "%Y":
                        tableValue = tableValue + "%04d" % (int(parsed_cell_date["year"]))
                    elif dateParts[i] == "%y":
                        # assume all 2 digit years are in the range 2000 <= year < 2099.  Don't expect this software to be used in the year 2100!! JJG 07/08/2021
                        tableValue = tableValue + "%04d" % (2000 + int(parsed_cell_date["year"]))
                    if i < len(dateParts)-1:
                        tableValue = tableValue + "%s" % (Date.get_global_date_sep(self))
            else:
                tableValue = ""
                self.DisplayMsg("Bad cell date for row %d col %d ignored: %s" % (row, col, cellValue))
        self.bill_grid.SetCellAlignment(row, col, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.bill_grid.SetCellValue(row, col, tableValue)

    def GridCellDateTimeRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        if (self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS and cellValue == "0") or cellValue=='None':
            tableValue = ""
        else:
            datePart,timePart = cellValue.split(" ")
            parsed_cell_date = Date.parse_date(self, datePart, Date.get_global_date_format(self))
            self.SetCellAlignment(row, col, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
            dateFormat = Date.get_global_date_format(self)
            date_sep = Date.get_global_date_sep(self)
            dateParts = dateFormat.split(date_sep)
            tableValue = ""
            for i in range(len(dateParts)):
                if dateParts[i] == "%m":
                    tableValue = tableValue + "%02d" % (int(parsed_cell_date["month"]))
                elif dateParts[i] == "%d":
                    tableValue = tableValue + "%02d" % (int(parsed_cell_date["day"]))
                elif dateParts[i] == "%Y":
                    tableValue = tableValue + "%04d" % (int(parsed_cell_date["year"]))
                elif dateParts[i] == "%y":
                    # assume all 2 digit years are in the range 2000 <= year < 2099.  Don't expect this software to be used in the year 2100!! JJG 07/08/2021
                    tableValue = tableValue + "%04d" % (2000 + int(parsed_cell_date["year"]))
                if i < len(dateParts)-1:
                    tableValue = tableValue + "%s" % (Date.get_global_date_sep(self))
            tableValue = "%02s/%02s/%04s %s" % (month, day, year, timePart)
        self.bill_grid.SetCellValue(row, col, tableValue)

    def GridCellStringRenderer(self, row, col):
        cellValue = str(self.getColMethod(row, col))
        self.bill_grid.SetCellAlignment(row, col, wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        if self.getColZeroSuppress(row, col) == self.ZERO_SUPPRESS \
               and (cellValue == '0' or cellValue == '0.00' or cellValue == '' or cellValue.startswith('Unknown') or cellValue == 'None'):
            tableValue = ""
        else:
            tableValue = cellValue
        self.bill_grid.SetCellValue(row, col, tableValue)

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
            if col_type == self.DOLLAR_TYPE: new_value = 0.00
        if row < 0 or row >= len(self.bills):
            str = "Warning: cellchanging on bad cell %d %d!" % (row, col)
            ret_val = self.DisplayMsg(str)
        elif self.col_info[col][self.EDIT_COL] == self.NOT_EDITABLE:
            str = "Warning: Changes not allowed for column %s!" % (self.getColName(col))
            ret_val = self.DisplayMsg(str)
        if ret_val == wx.OK and self.col_info[col][self.TYPE_COL] == self.DOLLAR_TYPE:
            # TODO  move regular expression for dollar format to new object
            m = re.match("^-?\$?\d{1,3}(\,?\d{3})*(\.\d{2})?$", new_value)
            if m:
                self.edited = True
                dollar_amount = new_value.replace("$", "").replace(",", "")
                if "." not in dollar_amount:
                    dollar_amount += ".00"
                    evt.Veto()
                    self.bill_grid.SetCellValue(row, col, dollar_amount)
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
            pass
        if ret_val == wx.OK:
            self.billchange(row,col,new_value)
            self.redraw_all(row)  # only redraw current row
        else:
            evt.Veto()

    def set_properties(self):
        total_width = 60  # non-zero start value to account for record number and status lines of frame!
        colNames = self.columnNames
        grid = self.bill_grid
        grid.CreateGrid(self.maxRows, self.maxCols)
        grid.SetSize((self.maxRows, self.maxCols))
        for j in range(len(self.bills)):
            for i in range(len(self.columnNames)):
                grid.SetColLabelValue(i, colNames[i])
                cur_width = self.getColWidth(i)
                total_width += cur_width
                grid.SetColSize(i, cur_width)
                grid.SetCellValue(j, i, str(self.getColMethod(j, i)))
        style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        grid.SetWindowStyle(style)

    def update_bill_grid_dates(self, oldDateFormat, newDateFormat):
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
                                print("update_bill_grid_dates: Warning: unknown method for cell! row, ", row, " col ", col, " Skipping!")

    def cellchange(self, evt):
        doredraw = 0
        row = evt.GetRow()
        col = evt.GetCol()
        if row < 0: return
        if row >= len(self.cur_bill):
            print("Warning: modifying incorrect cell!")
            return
        self.edited = True
        bill = self.cur_bill[row]
        val = self.cbgrid.GetCellValue(row, col)
        if col == 0:
            bill.setdate(val)
        elif col == 1:
            bill.setnumber(val)
        elif col == 2:
            bill.setpayee(val)
        elif col == 3:
            if val:
                bill.set_state("cleared")
        elif col == 4:
            bill.setmemo(val)
        elif col == 5:
            doredraw = 1
            bill.setamount(val)
        else:
            print("Warning: modifying incorrect cell!")
            return
        if doredraw:
            self.redraw_all(row)  # only redraw [row:]

    def load_file(self, *args):
        self.close()
        self.edited = False
        try:
            mffile = open(self.filename, 'r')
        except:
            error = "No such file or directory :" + self.filename
            self.MsgBox(error) 
            return None
        lines = mffile.readlines()
        mffile.close()
        for i in range(len(lines)):
            lines[i] = lines[i].replace('"', '').strip()                       # remove " from every line and remove leading and trailing spaces
        fields = lines[0].split(",")
        bill_fields = Bill.get_bill_fields()
        args = {}
        for j in range(len(fields)):
            if j == len(fields)-1:
                fields[j] = fields[j].strip()
            fields[j] = fields[j].replace(' ','_').lower()              # convert field names to keywords by replacing spaces with underscores and changing to all lower case                    
            bill_fields[j] = bill_fields[j].replace(' ','_').lower()    # convert bill_field names to keywords by replacing spaces with underscores and changing to all lower case                    
            bill_index=bill_fields.index(fields[j])
            args[fields[j]] = bill_index
        for i in range(1,len(lines)):
            new_bill = Bill(self, self.parent)
            vals = lines[i].split(",")
            for j in range(len(fields)-1):
                vals[j] = vals[j].replace("'","").strip()               # Get rid of '' and leading and trailing spaces
            for k in range(len(args)-1):
                cur_field = fields[k]
                val = vals[args[cur_field]]
                bill_index = bill_fields.index(cur_field)            # Make sure the fields in the file match the fields in the Bill class
                if bill_index != -1:
                    if cur_field == "payee":
                        new_bill.set_payee(val)
                    elif cur_field == "type":
                        new_bill.set_type(val)
                    elif cur_field == "amount":
                        new_bill.set_amount(val)
                    elif cur_field == "min_due":
                        new_bill.set_min_due(val)
                    elif cur_field == "due_date":
                        new_bill.set_due_date(val)
                    elif cur_field == "sched_date":
                        new_bill.set_sched_date(val)
                    elif cur_field == "pmt_acct":
                        new_bill.set_pmt_acct(val)
                    elif cur_field == "pmt_method":
                        new_bill.set_pmt_method(val)
                    elif cur_field == "pmt_freq":
                        new_bill.set_pmt_frequency(val)
                    elif cur_field == "check_number":
                        new_bill.set_check_number(val)
                    else:
                        print("Unknown field " + cur_field + " ignored for line " + lines[i])
            billsList = self.parent.getBillsList()
            billsList.append(new_bill)
        self.redraw_all(-1)
        self.SetTitle("PyAsset: %s" % self.filename)
        return

    def save_file(self, *args):
        self.edited = False
        billList = self.bills
        if self.filename != "" and len(billList) != 0:
            file = open(self.filename, 'w')                             # Make sure file starts empty! JJG 1/17/2024
            file.close()
            bill_fields = Bill.get_bill_fields()
            fields = ''
            for field in bill_fields:
                fields += '"' + field + '",'                            # Add "" around each field name in case there are spaces
            fields = [fields[0:len(fields)-1]]                          # create a header line of the field names. Remove extra ',' added in the loop and make a list
            self.process_bill_list(billList, "writeBillsToCSV", lines=fields)

    def process_bill_list(self, billsList, function, lines=None):
#        print("process_bill_list: billsList:" + str(billsList) + ", function: " + function + ", lines: ", str(lines))
        if lines != None:
            with open(self.filename, 'a') as file:
                fileLines = '\n'.join(lines)
                file.writelines("%s" % fileLines)
                file.write('\n')
        if billsList != None:
            lines = []
            for i in range(len(billsList)):
                if function == 'writeBillsToCSV':
                        cur_bill = str(billsList.bills[i])
                        lines.append(cur_bill)
                elif function == 'delete':
                    try:
                        transFrame = billsList.bills.bills[0].trans_frame
                    except:
                        transFrame = None
                    if transFrame != None:
                        transFrame.Destroy()
                    del billsList.bills[0]                         # Since we are deleting the entire list, we can just delete the first one each time!
                else:
                    pass                                            # JJG 1/26/24  TODO add code to print error if unknown function parameter passed to process_asset_list
            if function == 'delete':
                self.ClearGrid()
            if function == 'writeBillsToCSV':
                with open(self.filename, 'a') as file:
                    fileLines = '\n'.join(lines)
                    file.writelines("%s" % fileLines)
#                    file.write('\n')
            if function != 'add':
                self.redraw_all()

    def save_as_file(self, *args):
        d = wx.FileDialog(self, "Save", "", "", "*.qif", wx.FD_OPEN)
        if d.ShowModal() == wx.ID_OK:
            fname = d.GetFilename()
            dir = d.GetDirectory()
            self.filename = os.path.join(dir, fname)
            self.SetTitle("PyAsset: %s" % self.filename)
        return

    def close(self, *args):
        if self.edited:
            d = wx.MessageDialog(self, 'Save file before closing', 'Question',
                                 wx.YES_NO)
            if d.ShowModal() == wx.ID_YES: self.save_file()

        self.quit(self, *args)

    def quit(self, *args):

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

#        del self.Parent.bills_frame
        self.Destroy()

    def write_file(self, date_, amount_, memo_, payee_, filelocation_):
    #
    #     @brief Receives data to be written to and its location
    #
    #     @params[in] date_
    #     Data of bill
    #     @params[in] amount_
    #     Amount of money for bill
    #     @params[in] memo_
    #     Description of bill
    #     @params[in] payee_
    #     Who bill was paid to
    #     @params[in] filelocation_
    #     Location of the Output file
    #
    #
    # https://en.wikipedia.org/wiki/Quicken_Interchange_Format
    #
        outFile = open(filelocation_, "a")  # Open file to be appended
        outFile.write("!Type:Cash\n")  # Header of bill, Currently all set to cash
        outFile.write("D")  # Date line starts with the capital D
        outFile.write(date_)
        outFile.write("\n")

        outFile.write("T")  # bill amount starts here
        outFile.write(amount_)
        outFile.write("\n")

        outFile.write("M")  # Memo Line
        outFile.write(memo_)
        outFile.write("\n")

        if (payee_ != -1):
            outFile.write("P")  # Payee line
            outFile.write(payee_)
            outFile.write("\n")

        outFile.write("^\n")  # The last line of each bill starts with a Caret to mark the end
        outFile.close()

    def read_csv(self, inf_, outf_, deff_):  # will need to receive input csv and def file
    #
    #     @brief  Takes given CSV and parses it to be exported to a QIF
    #
    #     @params[in] inf_
    #     File to be read and converted to QIF
    #     @params[in] outf_
    #     File that the converted data will go
    #     @params[in] deff_
    #     @params[in] deff_
    #     File with the settings for converting CSV
    #
    #
        csvdeff = csv.reader(deff_, delimiter=',')
        next(csvdeff, None)

        for settings in csvdeff:
            date_ = int(settings[0])  # convert to int
            amount_ = int(settings[2])  # How much was the bill
            memo_ = int(settings[3])  # discription of the bill
            payee_ = int(settings[4])  # Where the money is going
            deli_ = settings[5]  # How the csv is separated
            header_ = int(settings[6])  # Set if there is a header to skip

        csvIn = csv.reader(inf_, delimiter=deli_)  # create csv object using the given separator

        if header_ >= 1:  # If there is a header skip the fist line
            next(csvIn, None)  # skip header

        for row in csvIn:
            self.write_file(row[date_], row[amount_], row[memo_], row[payee_], outf_)  # export each row as a qif entry

        inf_.close()
        deff_.close()

    def import_CSV_file(self, *args):
        # Appends the records from a .csv file to the current Asset
        d = wx.FileDialog(self, "Import", "", "", "*.csv", wx.FD_OPEN)
        if d.ShowModal() == wx.ID_OK:
            self.edited = True
            fname = d.GetFilename()
            dir = d.GetDirectory()
            total_name_in = os.path.join(dir, fname)
            total_name_extension_place = total_name_in.find(".csv")
            total_name_def = ""
            total_name_qif = ""
            if total_name_extension_place != -1:
                total_name_def = total_name_in[:total_name_extension_place] + ".def"
                total_name_qif = total_name_in[:total_name_extension_place] + ".qif"
            # print value_name_in, value_name_def, value_name_qif
            error = ""
            try:
                fromfile = open(total_name_in, 'r')
            except:
                error = total_name_in + ' does not exist / cannot be opened !!\n'

            if total_name_qif != "":
                try:
                    tofile = open(total_name_qif, 'a')
                except:
                    error = total_name_qif + ' cannot be created !!\n'

            if total_name_def != "":
                if os.path.isfile(total_name_def):
                    deffile = open(total_name_def, 'r')
                else:
                    error = total_name_def + ' does not exist / cannot be opened !!\n'

            if error == "":
                tofile = total_name_qif
                self.read_csv(fromfile, tofile, deffile)
                self.cur_bill.read_qif(total_name_qif)
                fromfile.close()
                deffile.close()
                self.redraw_all(-1)

                if self.cur_bill.name:
                    title = "PyAsset: %s" % self.cur_bill.name
                else:
                    title = "Pyasset"
                self.bill_grid.SetTitle(title)

            else:
                d = wx.MessageDialog(self, error)
                d.ShowModal()
                d.Destroy()

    def export_text(self, *args):
        d = wx.FileDialog(self, "Save", "", "", "*.txt", wx.SAVE)
        if d.ShowModal() == wx.ID_OK:
            fname = d.GetFilename()
            dir = d.GetDirectory()
            self.cur_bill.write_txt(os.path.join(dir, fname))
        return

    def archive(self, *args):
        d = wx.TextEntryDialog(self,
                               "Archive bills before what date?",
                               "Archive Date")
        if d.ShowModal() == wx.ID_OK:
            date = Date(d.GetValue())
        else:
            date = None
        d.Destroy()
        if not date: return
        archive = Asset()
        newcb_startbill = bill()
        newcb_startbill.amount = 0
        newcb_startbill.payee = "Starting Balance"
        newcb_startbill.memo = "Archived by PyAsset"
        newcb_startbill.state = "cleared"
        newcb_startbill.date = date

        newcb = Asset()
        newcb.filename = self.cur_bill.filename
        newcb.name = self.cur_bill.name
        newcb.append(newcb_startbill)
        archtot = 0

        for bill in self.cur_bill:
            if bill.date < date and bill.state == "cleared":
                archive.append(bill)
                archtot += bill.amount
            else:
                newcb.append(bill)
        newcb_startbill.amount = archtot
        self.cur_bill = newcb
        while 1:
            d = wx.FileDialog(self, "Save Archive As", "", "", "*.qif", wx.SAVE)
            if d.ShowModal() == wx.ID_OK:
                fname = d.GetFilename()
                dir = d.GetDirectory()
            d.Destroy()
            if fname: break
        archive.write_qif(os.path.join(dir, fname))
        self.redraw_all(-1)
        self.edited = True
        return

    def newentry(self, *args):
        self.edited = True
        self.bills.append(Bill(self.parent))
        self.AppendRows()
        nbills = self.GetNumberRows()
        self.SetGridCursor(nbills - 1, 0)
        self.MakeCellVisible(nbills - 1, 1)

    def sort(self, *args):
        self.edited = True
        self.bills.sort()
        self.redraw_all(-1)

    def voidentry(self, *args):
        index = self.GetGridCursorRow()
        if index < 0:
            errorMsg = "index out of bounds in void - %d: ignored" % (index)
            self.DisplayMsg(errorMsg)
        else:
            bill = self.bills[index]
            if bill.get_state() != "void":
                msg = "Really void this bill?"
                title = "Really void?"
                void = True
            else:
                msg = "Really unvoid this bill?"
                title = "Really unvoid?"
                void = False
            d = wx.MessageDialog(self,
                                 msg,
                                 title, wx.YES_NO)
            if d.ShowModal() == wx.ID_YES:
                self.edited = True
                today_date = Date.get_curr_date(self.parent)
                # Toggle values so if it was void make it active and if active make it void
                if void:
                    bill.set_payee("VOID: " + bill.get_payee())
                    bill.set_memo("voided %s" % today_date)
                    bill.set_prev_state(bill.get_state())
                    bill.set_state("void")
                else:
                    new_payee = bill.get_payee()[5:]
                    bill.set_payee(new_payee)
                    unvoid_msg = "; unvoided %s" % today_date
                    bill.set_memo(bill.get_memo() + unvoid_msg)
                    new_state = bill.get_prev_state()
                    bill.set_state(new_state)
                proj_value = self.bills.update_current_and_projected_values(0)
                self.bills.parent.set_value_proj(proj_value)
                for i in range(index, self.getNumBills()):
                    self.setValue(i, "Value", str(round(self.bills[i].get_current_value(),2)))
                self.redraw_all()  # redraw only [index:]

    def deleteentry(self, *args):
        index = self.GetGridCursorRow()
        if index < 0:
            errorMsg = "index out of bounds in deleteentry - %d: ignored" % (index)
            self.DisplayMsg(errorMsg)
        else:
            d = wx.MessageDialog(self,
                                 "Really delete this bill?",
                                 "Really delete?", wx.YES_NO)
            if d.ShowModal() == wx.ID_YES:
                del self.bills[index]
            self.redraw_all()  # only redraw cells [index-1:]
 
    def adjust_balance(self, diff):
        self.edited = True
        bill = bill()
        bills = self.bills.append()
        bill.payee = "Balance Adjustment"
        bill.amount = diff
        bill.state = "cleared"
        bill.memo = "Adjustment"
        self.redraw_all(-1)  # only redraw [-1]?
        return

    def get_cleared_balance(self):
        value = 0.0
        for bill in self.cur_bill:
            if bill.get_state() == "cleared":
                value = value + bill.amount
        return value

    def about(self, *args):
        d = wx.MessageDialog(self,
                             "Python Bill Manager\n"
                             "Copyright (c) 2026 Joseph J. Gorak\n"
                             "Released under the Gnu GPL\n"
                             "About JGBillManager",
                             wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()

    def gethelp(self, *args):
        d = HelpDialog(self, -1, "Help", __doc__)
        val = d.ShowModal()
        d.Destroy()

    def markcleared(self, *args):
        index = self.GetGridCursorRow()
        if index < 0:
            errorMsg = "index out of bounds in markcleared - %d: ignored" % (index)
            self.DisplayMsg(errorMsg)
        else:
            self.edited = True
            prev_state = self.bills[index].get_prev_state()
            cur_state = self.bills[index].get_state()
            self.bills[index].set_prev_state(cur_state)
            if cur_state == "cleared":
                self.bills[index].set_state(cur_state)
                self.setValue(index, "State", cur_state)
            else:
                self.bills[index].set_state(prev_state)
                self.setValue(index, "State", prev_state)
        return

    def billchange(self, which_bill, which_column, new_value):
        colName = self.getColName(which_column)
        bill_changed = self.bills[which_bill]
        modified = True
        old_value = -1
        print("billFrame: Recieved notification that bill ", bill_changed.get_payee(), " column", colName, "changed, new_value", new_value)
        if colName == "Payee":
            old_value = bill_changed.get_payee()
            bill_changed.set_payee(new_value)
        elif colName == "Amount":
            old_value = bill_changed.get_amount()
            bill_changed.set_amount(new_value)
        elif colName == "Min Due":
            old_value = bill_changed.get_min_due()
            bill_changed.set_min_due(new_value)
        elif colName == "Due Date":
            old_value = bill_changed.get_due_date()
            bill_changed.set_due_date(new_value)
        elif colName == "Sched Date":
            old_value = bill_changed.get_sched_date()
            bill_changed.set_sched_date(new_value)
        elif colName == "Pmt Acct":
            old_value = bill_changed.get_pmt_acct()
            bill_changed.set_pmt_acct(new_value)
        elif colName == "Due Date":
            old_value = bill_changed.get_due_date()
            bill_changed.set_due_date(new_value)
        elif colName == "Pmt Method":
            old_value = bill_changed.get_pmt_method()
            bill_changed.set_pmt_method(new_value)
        elif colName == "Frequency":
            old_value = bill_changed.get_pmt_frequency()
            bill_changed.set_pmt_frequency(new_value)
        else:
            self.DisplayMsg("Unknown column " + colName + " ignored!")
            new_value = -1
            modified = False

        if old_value != new_value:
            pmt_acct = bill_changed.get_pmt_acct()
            pmt_acct_bad = pmt_acct == "Other" or pmt_acct == "Unknown" or pmt_acct == ""
            if bill_changed.get_amount() != 0.0 and bill_changed.get_sched_date() != "" and not pmt_acct_bad:
                print("Need to process a transaction to " + bill_changed.get_payee() + " from " + bill_changed.get_pmt_acct() + " for " + str(bill_changed.get_amount()) + " on " + bill_changed.get_sched_date())
                bill_type = bill_changed.get_type()
                #TODO: Need to finish logic for adding transactions for billbudgeting  JJG 9/13/2025
                if bill_type == "Checking and savings":
                    pmt_acct_payee = "xfer to " + bill_changed.get_payee()
                    assets = self.parent.getAssets()
                    bill_changed_payee = "Deposit from " + assets[assets.index(pmt_acct)].get_name()

                    payee_asset_index = assets.index(bill_changed.get_payee())
                    payee_transactions = assets[payee_asset_index].transactions
                    payee_trans = Transaction(self.parent, payee=bill_changed_payee, action=bill_changed.get_action(), sched_date=bill_changed.get_sched_date(),
                                             due_date=bill_changed.get_due_date(), pmt_method=bill_changed.get_pmt_method(), amount=bill_changed.get_amount()
                                             )
                    if payee_transactions.index(bill_changed_payee, bill_changed.get_sched_date()) == -1:
                        payee_transactions.insert(payee_trans)
                        payee_transactions.update_current_and_projected_values()

                    pmt_acct_asset_index = assets.index(bill_changed.get_pmt_acct())
                    pmt_acct_transactions = assets[pmt_acct_asset_index].transactions
                    pmt_acct_trans_index = pmt_acct_transactions.index(pmt_acct_payee, bill_changed.get_sched_date())
                    pmt_bill_changed = pmt_acct_transactions[pmt_acct_trans_index]
                    pmt_acct_trans = Transaction(self.parent, payee=pmt_acct_payee, action=pmt_bill_changed.get_action(), sched_date=pmt_bill_changed.get_sched_date(),
                                                 due_date=pmt_bill_changed.get_due_date(), pmt_method=pmt_bill_changed.get_pmt_method(), amount=pmt_bill_changed.get_amount()
                                                )
                    if pmt_acct_transactions.index(pmt_acct_payee, pmt_bill_changed.get_sched_date()):
                        pmt_acct_transactions.insert(pmt_acct_trans)
                        pmt_acct_transactions.update_current_and_projected_values()

                elif bill_type == "Credit Card":
                    pass
                elif bill_type == "Loan":
                    pass
                elif bill_type == "Expense":
                    pass
                else:
                    self.DisplayMsg("Unknown bill type " + bill_type + " ignored!")
                    modified = False
        else:
            modified = False

        if modified == True:
            self.edited = True

    def MsgBox(self, message):
        d = wx.MessageDialog(self, message, "error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()

    def OnCellLeftClick(self, evt):
        row = evt.GetRow()
        col = evt.GetCol()
        pos = evt.GetPosition()
        if row < len(self.bills):
            if col == self.BILL_PMT_ACCT_COL:
                asset_name = self.bill_grid.GetCellValue(row, col)
                asset_frame = self.parent
                pmt_asset_index = asset_frame.assets.index(asset_name)
                if pmt_asset_index != -1:
                    asset_frame.addTransactionFrame(pmt_asset_index,False)
            else:
                print("OnCellLeftClick: bill_grid (%d,%d) %s\n" % (row, col, pos))
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
        print("OnLabelLeftClick: bill_grid (%d,%d) %s\n" % (evt.GetRow(),
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
        row = self.bill_grid.GetGridCursorRow()
        col = self.bill_grid.GetGridCursorCol()

        if self.bill_grid.IsCellEditControlEnabled():
            self.bill_grid.HideCellEditControl()
            self.bill_grid.DisableCellEditControl()

        try:
            value = self.bill_grid.GetCellValue(row, col)
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
