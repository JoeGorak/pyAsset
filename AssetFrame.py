#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2016, Joseph J. Gorak. All rights reserved.
This code is in development -- use at your own risk. Email
comments, patches, complas to joe.gorak@gmail.com

This program is free software you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""

#  Version information
#  6/11/2016     Initial version v0.1

# To Do list:
# Speed redraw_all: break o redraw_all, redraw_range, redraw_totals
# Save a backup version of files
# Read and save CBB files?
# Undo?
# Plot balance vs day
# Search functions
# goto date

import wx
import wx.grid
import csv
import os
import copy
from Asset import Asset
from AssetList import AssetList
from Date import Date
from Transaction import Transaction
from HelpDialog import HelpDialog
from ExcelToAsset import ExcelToAsset


class AssetFrame(wx.Frame):

    def __init__(self, style, parent, my_id, title="PyAsset:Asset", myfile=None, **kwds):
        self.assets = AssetList()
        self.cur_asset = None
        self.display_asset = Asset()            # used to update grid on the screen
        self.edited = 0
        self.rowSize = 27
        self.colSize = 20

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

        # Define indices of columns in grid layout array
        self.NAME_COL = 0
        self.WIDTH_COL = 1
        self.TYPE_COL = 2
        self.EDIT_COL = 3

        # Grid layout array
        self.col_info = [[self.ACCT_NAME_COL, ACCT_NAME_COL_WIDTH, self.STRING_TYPE, self.EDITABLE],
                         [self.ACCT_CURR_VAL_COL, ACCT_CURR_VAL_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE],
                         [self.ACCT_PROJ_VAL_COL, ACCT_PROJ_VAL_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE],
                         [self.ACCT_LAST_PULL_COL, ACCT_LAST_PULL_COL_WIDTH, self.DATE_TIME_TYPE, self.NOT_EDITABLE],
                         [self.ACCT_LIMIT_COL, ACCT_LIMIT_COL_WIDTH, self.DOLLAR_TYPE, self.EDITABLE],
                         [self.ACCT_AVAIL_ONLINE_COL, ACCT_AVAIL_ONLINE_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE],
                         [self.ACCT_AVAIL_PROJ_COL, ACCT_AVAIL_PROJ_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE],
                         [self.ACCT_RATE_COL, ACCT_RATE_COL_WIDTH, self.RATE_TYPE, self.EDITABLE],
                         [self.ACCT_PAYMENT_COL, ACCT_PAYMENT_COL_WIDTH, self.DOLLAR_TYPE, self.EDITABLE],
                         [self.ACCT_DUE_DATE_COL, ACCT_DUE_DATE_COL_WIDTH, self.DATE_TYPE, self.EDITABLE],
                         [self.ACCT_SCHED_DATE_COL, ACCT_SCHED_DATE_COL_WIDTH, self.DATE_TYPE, self.EDITABLE],
                         [self.ACCT_MIN_PMT_COL, ACCT_MIN_PMT_COL_WIDTH, self.DOLLAR_TYPE, self.EDITABLE],
                         [self.ACCT_STMT_BAL_COL, ACCT_STMT_BAL_COL_WIDTH, self.DOLLAR_TYPE, self.EDITABLE],
                         [self.ACCT_AMT_OVER_COL, ACCT_AMT_OVER_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE],
                         [self.ACCT_CASH_LIMIT_COL, ACCT_CASH_LIMIT_COL_WIDTH, self.DOLLAR_TYPE, self.EDITABLE],
                         [self.ACCT_CASH_USED_COL, ACCT_CASH_USED_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE],
                         [self.ACCT_CASH_AVAIL_COL, ACCT_CASH_AVAIL_COL_WIDTH, self.DOLLAR_TYPE, self.NOT_EDITABLE]
                        ]

        if style == None:
            style = wx.DEFAULT_FRAME_STYLE
        kwds["style"] = style
        wx.Frame.__init__(self, parent, my_id, title, **kwds)

        self.make_widgets()

        if myfile:
            self.cur_asset.read_qif(myfile)
            self.redraw_all(-1)
            if self.cur_asset.get_name() != None:
                self.SetTitle("PyAsset: Asset %s" % self.cur_asset.get_name())
        return

    def getColName(self,i):
        return self.col_info[i][self.NAME_COL]

    def getColWidth(self, i):
        return self.col_info[i][self.WIDTH_COL]

    def getColType(self, i):
        return self.col_info[i][self.TYPE_COL]

    def getColEdit(self,i):
        return self.col_info[i][self.EDIT_COL]

    def getColMethod(self,i):
        if i == self.ACCT_NAME_COL:
            return self.display_asset.details.name
        elif i == self.ACCT_CURR_VAL_COL:
            return self.display_asset.details.total
        elif i == self.ACCT_PROJ_VAL_COL:
            return self.display_asset.details.total
        elif i == self.ACCT_LAST_PULL_COL:
            return self.display_asset.details.last_pull_date
        elif i == self.ACCT_LIMIT_COL:
            return self.display_asset.details.limit
        elif i == self.ACCT_AVAIL_ONLINE_COL:
            return self.display_asset.details.avail
        elif i == self.ACCT_AVAIL_PROJ_COL:
            return self.display_asset.details.avail
        elif i == self.ACCT_RATE_COL:
            return self.display_asset.details.rate
        elif i == self.ACCT_PAYMENT_COL:
            return self.display_asset.details.payment
        elif i == self.ACCT_DUE_DATE_COL:
            return self.display_asset.details.due_date
        elif i == self.ACCT_SCHED_DATE_COL:
            return self.display_asset.details.sched
        elif i == self.ACCT_MIN_PMT_COL:
            return self.display_asset.details.min_pay
#                         [ACCT_STMT_BAL_COL, ACCT_STMT_BAL_COL_WIDTH, DOLLAR_TYPE, EDITABLE, None],
#                         [ACCT_AMT_OVER_COL, ACCT_AMT_OVER_COL_WIDTH, DOLLAR_TYPE, NOT_EDITABLE, None],
#                         [ACCT_CASH_LIMIT_COL, ACCT_CASH_LIMIT_COL_WIDTH, DOLLAR_TYPE, EDITABLE, None],
#                         [ACCT_CASH_USED_COL, ACCT_CASH_USED_COL_WIDTH, DOLLAR_TYPE, NOT_EDITABLE, None],
#                         [ACCT_CASH_AVAIL_COL, ACCT_CASH_AVAIL_COL_WIDTH, DOLLAR_TYPE, NOT_EDITABLE, None]
        return "??"

    def getNumLayoutCols(self):
        return len(self.col_info)

    def make_widgets(self):
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)
        self.statusbar = self.CreateStatusBar(1, 0)
        self.make_filemenu()
        self.make_editmenu()
        self.make_helpmenu()
        self.make_grid()
        self.set_properties()
        self.do_layout()

    def make_filemenu(self):
        self.filemenu = wx.Menu()
        ID_IMPORT_CSV = wx.NewId()
        ID_IMPORT_XLSM = wx.NewId()
        ID_EXPORT_TEXT = wx.NewId()
        ID_ARCHIVE = wx.NewId()
        self.filemenu.Append(wx.ID_OPEN, "Open\tCtrl-o",
                             "Open a new transction file", wx.ITEM_NORMAL)
        self.filemenu.Append(wx.ID_SAVE, "Save\tCtrl-s",
                             "Save the current transactions in the same file", wx.ITEM_NORMAL)
        self.filemenu.Append(wx.ID_SAVEAS, "Save As",
                             "Save the current transactions under a different name", wx.ITEM_NORMAL)
        self.filemenu.Append(ID_IMPORT_CSV, "Import CSV\tCtrl-c",
                             "Import transactions from a CSV file",
                             wx.ITEM_NORMAL)
        self.filemenu.Append(ID_IMPORT_XLSM, "Import XLSM\tCtrl-X",
                             "Import transactions from an EXCEL file with Macros",
                             wx.ITEM_NORMAL)
        self.filemenu.Append(ID_EXPORT_TEXT, "Export Text",
                             "Export the current transaction register as a text file",
                             wx.ITEM_NORMAL)
        self.filemenu.Append(ID_ARCHIVE, "Archive",
                             "Archive transactions older than a specified date",
                             wx.ITEM_NORMAL)
        self.filemenu.Append(wx.ID_CLOSE, "Close\tCtrl-w",
                             "Close the current file", wx.ITEM_NORMAL)
        self.filemenu.Append(wx.ID_EXIT, "Exit\tCtrl-q",
                             "Exit PyAsset", wx.ITEM_NORMAL)
        self.menubar.Append(self.filemenu, "&File")
        wx.EVT_MENU(self, wx.ID_OPEN, self.load_file)
        wx.EVT_MENU(self, wx.ID_SAVE, self.save_file)
        wx.EVT_MENU(self, wx.ID_SAVEAS, self.save_as_file)
        wx.EVT_MENU(self, ID_IMPORT_CSV, self.import_CSV_file)
        wx.EVT_MENU(self, ID_IMPORT_XLSM, self.import_XLSM_file)
        wx.EVT_MENU(self, ID_EXPORT_TEXT, self.export_text)
        wx.EVT_MENU(self, ID_ARCHIVE, self.archive)
        wx.EVT_MENU(self, wx.ID_CLOSE, self.close)
        wx.EVT_MENU(self, wx.ID_EXIT, self.quit)
        return

    def make_editmenu(self):
        ID_SORT = wx.NewId()
        ID_DELETE_ENTRY = wx.NewId()
        self.editmenu = wx.Menu()
        self.editmenu.Append(wx.ID_NEW, "New Entry\tCtrl-n",
                             "Create a new asset in the list",
                             wx.ITEM_NORMAL)
        self.editmenu.Append(ID_DELETE_ENTRY, "Delete Entry",
                             "Delete the current asset", wx.ITEM_NORMAL)
        self.editmenu.Append(ID_SORT, "Sort Entries",
                             "Sort entries", wx.ITEM_NORMAL)
        self.menubar.Append(self.editmenu, "&Edit")
        wx.EVT_MENU(self, wx.ID_NEW, self.newentry)
        wx.EVT_MENU(self, ID_DELETE_ENTRY, self.deleteentry)
        wx.EVT_MENU(self, ID_SORT, self.sort)
        return

    def make_helpmenu(self):
        ID_HELP = wx.NewId()
        self.helpmenu = wx.Menu()
        self.helpmenu.Append(wx.ID_ABOUT, "About",
                             "About PyAsset", wx.ITEM_NORMAL)
        self.helpmenu.Append(ID_HELP, "Help\tCtrl-h",
                             "PyAsset Help", wx.ITEM_NORMAL)

        self.menubar.Append(self.helpmenu, "&Help")
        wx.EVT_MENU(self, wx.ID_ABOUT, self.about)
        wx.EVT_MENU(self, ID_HELP, self.gethelp)
        return

    def make_grid(self):
        self.cbgrid = wx.grid.Grid(self, -1)
        wx.grid.EVT_GRID_CELL_CHANGE(self, self.cellchange)
        return

    def set_properties(self):
        self.SetTitle("PyAsset: Asset")
        self.statusbar.SetStatusWidths([-1])
        statusbar_fields = [""]
        columnNames = ["Account", "Value (Curr)", "Value (Proj)", "last pulled", "Limit", "Avail (Online)", "Avail (Proj)", "Rate",
                       "Payment", "Due Date", "Sched", "Min Pmt", "Stmt Bal", "Amt Over", "Cash Limit", "Cash used", "Cash avail"];

        for i in range(len(statusbar_fields)):
            self.statusbar.SetStatusText(statusbar_fields[i], i)
        self.cbgrid.CreateGrid(0, len(columnNames))
        self.cbgrid.SetRowLabelSize(self.rowSize)
        self.cbgrid.SetColLabelSize(self.colSize)
        self.total_width = 60                   # non-zero start value to account for record number of cbgrid frame!
        for i in range(len(columnNames)):
            self.cbgrid.SetColLabelValue(i, columnNames[i])
            cur_width = self.getColWidth(i)
            self.total_width += cur_width
            self.cbgrid.SetColSize(i, cur_width)
        nassets = len(self.assets)
        self.SetSize(size=(self.total_width, nassets*self.rowSize))
        self.Show()

    def do_layout(self):
        self.sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_1.Add(self.cbgrid, 1, wx.EXPAND, 0)
        self.SetSizer(self.sizer_1)
        self.SetAutoLayout(True)
        self.sizer_1.Fit(self)
        self.sizer_1.SetSizeHints(self)
        self.Layout()
        self.Show()

    def redraw_all(self, index=None):
        nrows = self.cbgrid.GetNumberRows()
        if nrows > 0:
            self.cbgrid.DeleteRows(0, nrows)
        nassets = len(self.assets)
        if nrows < nassets:
            rows_needed = nassets - nrows
            self.cbgrid.AppendRows(rows_needed)
        for i in range(nassets):
            self.display_asset = copy.deepcopy(self.assets[i])
            for col in range(self.getNumLayoutCols()):
                self.cbgrid.SetCellTextColour(i, col, 'black')
                self.cbgrid.SetReadOnly(i, col, self.getColEdit(col))
                self.cbgrid.SetCellAlignment(i, col, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
                cellValue = str(self.getColMethod(col))
                if (cellValue == "0" or cellValue == "0.0" or cellValue == "??") and col != self.ACCT_CURR_VAL_COL and col != self.ACCT_PROJ_VAL_COL:
                    continue
                else:
                    cellType = self.getColType(col)
                    if cellType == self.DOLLAR_TYPE:
                        amount = float(cellValue)
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
                            if dotPos == len(cellValue)-2:
                                cent_val *= 10
                        cents = "%02d" % (cent_val)
                        cents = str(cents)
                        groups = [cents]
                        groups.append(".")
                        amount -= float(cent_val)/100
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
                        for j in range(len(groups)-2, -1, -1):
                            str_out += str(groups[j])
                        if negative:
                            self.cbgrid.SetCellTextColour(i, col, 'red')
                            tableValue = "-$%13s" % (str_out)
                        else:
                            tableValue = " $%13s" % (str_out)
                    elif cellType == self.RATE_TYPE:
                        rate = float(cellValue)
                        tableValue = "%13.3f%%" % (rate*100.0)
                    elif cellType == self.DATE_TYPE:
                        dateParts = cellValue.split("-")
                        month = dateParts[1]
                        day = dateParts[2]
                        year = dateParts[0]
                        self.cbgrid.SetCellAlignment(i, col, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
                        tableValue = "%02s/%02s/%04s" % (month, day, year)
                    elif cellType == self.DATE_TIME_TYPE:
                        datetimeParts = cellValue.split(" ")
                        dateParts = datetimeParts[0].split("-")
                        time = datetimeParts[1]
                        month = dateParts[1]
                        day = dateParts[2]
                        year = dateParts[0]
                        self.cbgrid.SetCellAlignment(i, col, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
                        tableValue = "%02s/%02s/%04s %s" % (month, day, year, time)
                    elif cellType == self.STRING_TYPE:
                        self.cbgrid.SetCellAlignment(i, col, wx.ALIGN_LEFT, wx.ALIGN_CENTER)
                        tableValue = cellValue
                    else:
                        self.cbgrid.SetCellAlignment(i, col, wx.ALIGN_LEFT, wx.ALIGN_CENTER)
                        tableValue = "Bad: %s" % (cellValue)
                    self.cbgrid.SetCellValue(i, col, tableValue)
        if index == -1:
            self.cbgrid.SetGridCursor(nassets-1, 0)
            self.cbgrid.MakeCellVisible(nassets-1, True)
        elif index > 0:
            self.cbgrid.SetGridCursor(index, 0)
            self.cbgrid.MakeCellVisible(index, True)
        nassets = len(self.assets)
        self.SetSize(size=(self.total_width, nassets*self.rowSize))
        self.Show()
        return

# TODO: Rewrite cellchange to work with cell_info and Asset vice hard_coded transaction values!   JJG 06/27/2016
    def cellchange(self, evt):
        doredraw = 0
        row = evt.GetRow()
        col = evt.GetCol()
        if row < 0: return
        if row >= len(self.cur_asset):
            print "Warning: modifying incorrect cell!"
            return
        col_inf = copy.deepcopy(self.col_info[col])
        if col_inf[self.EDIT_COL] == self.NOT_EDITABLE:
            print "Warning: attempt to edit non-editable column!"
            return
        self.display_asset = copy.deepcopy(self.assets[row])
        self.edited = 1
        transaction = self.assets[row]
        val = self.cbgrid.GetCellValue(row, col)
        if col == 0:
            transaction.setdate(val)
        elif col == 1:
            transaction.setnumber(val)
        elif col == 2:
            transaction.setpayee(val)
        elif col == 3:
            if val:
                transaction.setcleared('x')
        elif col == 4:
            transaction.setmemo(val)
        elif col == 5:
            doredraw = 1
            transaction.setamount(val)
        else:
            print "Warning: modifying incorrect cell!"
            return
        if doredraw: self.redraw_all(row)  # only redraw [row:]
        return

    def load_file(self, *args):
        self.close()
        self.cur_asset = Asset()
        self.edited = 0
        d = wx.FileDialog(self, "Open", "", "", "*.qif", wx.OPEN)
        if d.ShowModal() == wx.ID_OK:
            fname = d.GetFilename()
            dir = d.GetDirectory()
            self.cur_asset.read_qif(os.path.join(dir, fname))
            self.redraw_all(-1)
        if self.cur_asset.name: self.SetTitle("PyAsset: %s" % self.cur_asset.name)
        return

    def save_file(self, *args):
        for cur_asset in self.assets:
            if not cur_asset.filename:
                self.save_as_file()
            else:
                self.edited = 0
            self.cur_asset.write_qif()
        return

    def save_as_file(self, *args):
        d = wx.FileDialog(self, "Save", "", "", "*.qif", wx.SAVE)
        if d.ShowModal() == wx.ID_OK:
            fname = d.GetFilename()
            dir = d.GetDirectory()
            self.cur_asset.write_qif(os.path.join(dir, fname))
        if self.cur_asset.name: self.SetTitle("PyAsset: %s" % self.cur_asset.name)
        return

    def close(self, *args):
        if self.edited:
            d = wx.MessageDialog(self, 'Save file before closing?', 'Question',
                                 wx.YES_NO)
            if d.ShowModal() == wx.ID_YES:
                self.save_file()
        self.assets = AssetList()
        self.cur_asset = Asset()
        nrows = self.cbgrid.GetNumberRows()
        if nrows > 0:
            self.cbgrid.DeleteRows(0, nrows)
            self.redraw_all(-1)
        self.edited = 0
        self.SetTitle("PyAsset: Asset")
        return

    def quit(self, *args):
        self.close()
        self.Close()

    #
    #     @brief Receives data to be written to and its location
    #
    #     @params[in] date_
    #     Data of transaction
    #     @params[in] amount_
    #     Amount of money for transaction
    #     @params[in] memo_
    #     Description of transaction
    #     @params[in] payee_
    #     Who transaction was paid to
    #     @params[in] filelocation_
    #     Location of the Output file
    #
    #
    # https://en.wikipedia.org/wiki/Quicken_Interchange_Format
    #

    def write_file(self, date_, amount_, memo_, payee_, filelocation_):
        outFile = open(filelocation_, "a")  # Open file to be appended
        outFile.write("!Type:Cash\n")  # Header of transaction, Currently all set to cash
        outFile.write("D")  # Date line starts with the capital D
        outFile.write(date_)
        outFile.write("\n")

        outFile.write("T")  # Transaction amount starts here
        outFile.write(amount_)
        outFile.write("\n")

        outFile.write("M")  # Memo Line
        outFile.write(memo_)
        outFile.write("\n")

        if (payee_ != -1):
            outFile.write("P")  # Payee line
            outFile.write(payee_)
            outFile.write("\n")

        outFile.write("^\n")  # The last line of each transaction starts with a Caret to mark the end
        outFile.close()

    #
    #     @brief  Takes given CSV and parses it to be exported to a QIF
    #
    #     @params[in] inf_
    #     File to be read and converted to QIF
    #     @params[in] outf_
    #     File that the converted data will go
    #     @params[in] deff_
    #     File with the settings for converting CSV
    #
    #

    def read_csv(self, inf_, outf_, deff_):  # will need to receive input csv and def file

        csvdeff = csv.reader(deff_, delimiter=',')
        next(csvdeff, None)

        for settings in csvdeff:
            date_ = (settings[0])  # convert to 
            amount_ = (settings[2])  # How much was the transaction
            memo_ = (settings[3])  # discription of the transaction
            payee_ = (settings[4])  # Where the money is going
            deli_ = settings[5]  # How the csv is separated
            header_ = (settings[6])  # Set if there is a header to skip

        csvIn = csv.reader(inf_, delimiter=deli_)  # create csv object using the given separator

        if header_ >= 1:  # If there is a header skip the fist line
            next(csvIn, None)  # skip header

        for row in csvIn:
            self.write_file(row[date_], row[amount_], row[memo_], row[payee_], outf_)  # export each row as a qif entry

        inf_.close()
        deff_.close()

    def import_CSV_file(self, *args):
        # Appends the records from a .csv file to the current Asset
        d = wx.FileDialog(self, "Import", "", "", "*.csv", wx.OPEN)
        if d.ShowModal() == wx.ID_OK:
            self.edited = 1
            fname = d.GetFilename()
            dir = d.GetDirectory()
            total_name_in = os.path.join(dir, fname)
            total_name_extension_place = total_name_in.find(".csv")
            total_name_def = ""
            total_name_qif = ""
            if total_name_extension_place != -1:
                total_name_def = total_name_in[:total_name_extension_place] + ".def"
                total_name_qif = total_name_in[:total_name_extension_place] + ".qif"
            # pr total_name_in, total_name_def, total_name_qif
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
                self.cur_asset.read_qif(total_name_qif)
                fromfile.close()
                deffile.close()
                self.redraw_all(-1)
            else:
                d = wx.MessageDialog(self, error, wx.OK | wx.ICON_INFORMATION)
                d.ShowModal()
                d.Destroy()
                return
        if self.cur_asset.name: self.SetTitle("PyAsset: %s" % self.cur_asset.name)
        return

    def import_XLSM_file(self, *args):
        # Appends or Merges as appropriate the records from a .xlsm file to the current Asset
        d = wx.FileDialog(self, "Import", "", "", "*.xlsm", wx.OPEN)
        if d.ShowModal() == wx.ID_OK:
            self.edited = 1
            fname = d.GetFilename()
            dir = d.GetDirectory()
            total_name_in = os.path.join(dir, fname)
#            total_name_extension_place = total_name_in.find(".xlsm")
            # pr total_name_in
            error = ""
            try:
                fromfile = open(total_name_in, 'r')
            except:
                error = total_name_in + ' does not exist / cannot be opened !!\n'
            fromfile.close()

            if error == "":
                self.cur_assets = None
                xlsm = ExcelToAsset()
                xlsm.OpenXLSMFile(total_name_in)
                latest_assets = xlsm.ProcessAssetsSheet()
#                print latest_assets
#TODO Need to add check if an account from latest_assets is already in self.assets! (keep track of num_updated and skip redraw if none updated
                for i in range(len(latest_assets)):
                    xlsm_asset = latest_assets.__getitem__(i)
                    self.cur_asset = copy.deepcopy(xlsm_asset)
                    self.assets.append(self.cur_asset[0])
                    self.assets[i] = copy.deepcopy(xlsm_asset)
                if self.cur_asset.name:
                    self.SetTitle("PyAsset: Asset %s" % total_name_in)
                self.redraw_all(-1)
                return
            else:
                d = wx.MessageDialog(self, error, wx.OK | wx.ICON_INFORMATION)
                d.ShowModal()
                d.Destroy()
                return

    def export_text(self, *args):
        d = wx.FileDialog(self, "Save", "", "", "*.txt", wx.SAVE)
        if d.ShowModal() == wx.ID_OK:
            fname = d.GetFilename()
            dir = d.GetDirectory()
            self.cur_asset.write_txt(os.path.join(dir, fname))
        return

    def archive(self, *args):
        d = wx.TextEntryDialog(self,
                               "Archive transactions before what date (mm/dd/yy)?",
                               "Archive Date")
        if d.ShowModal() == wx.ID_OK:
            date = Date(d.GetValue())
        else:
            date = None
        d.Destroy()
        if not date: return
        archive = Asset()
        newcb_starttransaction = Transaction()
        newcb_starttransaction.amount = 0
        newcb_starttransaction.payee = "Starting Balance"
        newcb_starttransaction.memo = "Archived by PyAsset"
        newcb_starttransaction.cleared = 1
        newcb_starttransaction.date = date

        newcb = Asset()
        newcb.filename = self.cur_asset.filename
        newcb.name = self.cur_asset.name
        newcb.append(newcb_starttransaction)
        archtot = 0

        for transaction in self.cur_asset:
            if transaction.date < date and transaction.cleared:
                archive.append(transaction)
                archtot += transaction.amount
            else:
                newcb.append(transaction)
        newcb_starttransaction.amount = archtot
        self.cur_asset = newcb
        while 1:
            d = wx.FileDialog(self, "Save Archive As", "", "", "*.qif", wx.SAVE)
            if d.ShowModal() == wx.ID_OK:
                fname = d.GetFilename()
                dir = d.GetDirectory()
            d.Destroy()
            if fname: break
        archive.write_qif(os.path.join(dir, fname))
        self.redraw_all(-1)
        self.edited = 1
        return

    def newentry(self, *args):
        self.edited = 1
        self.cur_asset.append(Asset())
        self.cbgrid.AppendRows()
        nassets = self.cbgrid.GetNumberRows()
        self.cbgrid.SetGridCursor(nassets - 1, 0)
        self.cbgrid.MakeCellVisible(nassets - 1, 1)

    def sort(self, *args):
        self.edited = 1
        self.cur_asset.sort()
        self.redraw_all(-1)

    def deleteentry(self, *args):
        index = self.cbgrid.GetGridCursorRow()
        if index < 0: return
        d = wx.MessageDialog(self,
                             "Really delete this asset?",
                             "Really delete?", wx.YES_NO)
        if d.ShowModal() == wx.ID_YES:
            del self.cur_asset[index]
        self.redraw_all(index - 1)  # only redraw cells [index-1:]
        return

    def about(self, *args):
        d = wx.MessageDialog(self,
                             "Python Asset Manager\n"
                             "Copyright (c) 2016, Joseph J. Gorak\n"
                             "Based on idea from Python Checkbook (pyCheckbook)\n"
                             "written by Richard P. Muller\n"
                             "Released under the Gnu GPL\n",
                             "About PyAsset",
                             wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()
        return

    def gethelp(self, *args):
        d = HelpDialog(self, -1, "Help", __doc__)
        val = d.ShowModal()
        d.Destroy()
        return
