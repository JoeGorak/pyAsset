#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2016-2024 Joseph J. Gorak. All rights reserved.
This code is in development -- use at your own risk. Email
comments, patches, complaints to joe.gorak@gmail.com

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
#  06/11/2016     Initial version v0.1
#  08/07/2021     Version v0.2
#  04/15/2022     Version v0.3         Added support for Bills

# To Do list (possible new features?):
# Speed redraw_all: break o redraw_all, redraw_range, redraw_totals
# Save a backup version of files
# Read and save CBB files?
# Undo?
# Plot balance vs day
# Search functions
# goto date

import wx
import csv
import os
import copy
from wx import Button
from wx.core import AcceleratorEntry
from qif import qif
from Asset import Asset
from AssetList import AssetList
from BillFrame import BillFrame
from BillList import BillList
from AssetGrid import AssetGrid
from PropertiesForm import PropertyFrameWithForm
from Date import Date
from wx.core import DateTime
from TransactionFrame import TransactionFrame
from Transaction import Transaction
from HelpDialog import HelpDialog
from ExcelToAsset import ExcelToAsset
from iMacrosToAsset import iMacrosToAsset

class AssetFrame(wx.Frame):
    global_curr_paydate = "mm/dd/yyyy"                      # JJG 12/29/2023 Set this way to get spacing right!
    global_next_paydate = "mm/dd/yyyy"                      # JJG 12/29/2023 Set this way to get spacing right!

    def __init__(self, parent, title="PyAsset", cfgFile="", assetFile=""):
        self.parent = parent
        self.frame = self
        self.assets = AssetList(self)
        self.bills = BillList()
        self.qif = qif(self)
        self.cur_asset = Asset(name=assetFile)
        self.edited = False
        self.cfgFile = copy.deepcopy(cfgFile)
        self.assetFile = copy.deepcopy(assetFile)
        self.CreateParams()
        super(AssetFrame, self).__init__(parent, title=title)
        self.make_widgets()
        if self.readConfigFile(cfgFile):
            self.curr_date = Date.set_curr_date(Date)["str"]
            self.proj_date = Date.set_proj_date(Date, "")
            Date.set_global_curr_date(self, self.curr_date)
            Date.set_global_proj_date(self, self.proj_date)
            self.set_curr_paydate()
            self.set_next_paydate()
            oldDateFormat = ""                                       # JJG 1/1/2024 Force date format to be set the first time
            newDateFormat = Date.get_global_date_format(Date)
            self.update_date_grid_dates(oldDateFormat, newDateFormat)
            oldDateFormat = newDateFormat
            oldRefDate = self.ref_date
            oldDateSep = Date.get_global_date_sep(self)
 
            if self.assetFile:
                latest_assets = qif.load_file(self, self.assetFile)
                self.process_asset_list(latest_assets)
        else:
            curr_date = Date(parent)
            self.curr_date = curr_date.curr_date["str"]
            self.proj_date = self.curr_date
            self.dateFormat = Date.get_global_date_format(Date)
            Date.set_global_curr_date(self, self.curr_date)
            Date.set_global_proj_date(self, self.proj_date)
            if self.payType == "" or self.payType == None:
                self.payType = "every 2 weeks"                                 # JJG 12/23/2023   added default if no payType given
        oldDateFormat = Date.get_global_date_format(Date)
        oldPayType = self.getPayType()
        oldRefDate = self.getRefDate()
        oldNetPay = self.getNetPay()
        oldPayDepositAcct = self.getPayDepositAcct()
        print(oldNetPay, oldPayType, oldDateFormat, oldRefDate, oldPayDepositAcct)
        self.curr_date = self.proj_date = Date.set_curr_date(self)
        currDate = Date.parse_date(self, self.curr_date, Date.get_global_date_format(Date))
        self.projDate = currDate
        self.properties(self, oldDateFormat, oldPayType, oldRefDate, oldNetPay, oldPayDepositAcct)

    def get_display_date(self, in_date):
        if type(in_date) is not str:
            return in_date["str"]
        else:
            return in_date

    def get_date_format(self):
        return Date.get_global_date_format(Date)

    def get_pay_types(self):
        return ["every week", "every 2 weeks", "monthly"]

    def get_default_pay_type(self):
        return "every 2 weeks"

    def get_pay_incr(self):
        payType = ""
        incr = None
        if type(self.payType) is int:
            payType = self.get_pay_types()[self.payType]
        else:
           if type(self.payType) is not str:
              MsgBox(self, "Bad payType "+self.payType+" in get_pay_incr")
        if payType == "every week":
            incr = wx.DateSpan(weeks=1)
        elif payType == "every 2 weeks":
            incr = wx.DateSpan(weeks=2)
        elif payType == "every month":
            incr = wx.DateSpan(months=1)
        return incr

    def set_curr_paydate(self):
        retVal = ""
        if self.ref_date != None:
            if type(self.ref_date) is DateTime:
                ref_date = self.ref_date
            else:
                ref_date = Date.parse_date(Date, self.ref_date, Date.get_global_date_format(Date))["dt"]
            test_curr_paydate = ref_date
            incr = self.get_pay_incr()
            if incr != None and test_curr_paydate != None:
                today = Date.get_today_date(Date)["dt"]
                if test_curr_paydate <= ref_date:
                    while test_curr_paydate <= today:
                        test_curr_paydate.Add(incr)
                    if test_curr_paydate > today:
                        test_curr_paydate.Subtract(incr)
                else:
                    while test_curr_paydate >= today:
                        test_curr_paydate.Subtract(incr)
                    if test_curr_paydate < today:
                        test_curr_paydate.Add(incr)
                self.curr_paydate = test_curr_paydate.Format(Date.get_global_date_format(Date))
                retVal = self.curr_paydate
        self.global_curr_paydate = retVal
        self.currPayDateOutput.LabelText = retVal
        return retVal

    def get_curr_paydate(self):
        return self.global_curr_paydate
    
    def set_next_paydate(self):
        retVal = ""
        if self.ref_date != None:
            next_paydate = self.get_curr_paydate()
            if type(next_paydate) is not DateTime:
                next_paydate = Date.parse_date(Date, next_paydate, Date.get_global_date_format(Date))["dt"]
            incr = self.get_pay_incr()
            if incr != None:
                next_paydate.Add(incr)
                self.next_paydate = next_paydate.Format(self.get_date_format())
                retVal = self.next_paydate
        self.global_next_paydate = retVal
        self.nextPayDateOutput.LabelText = retVal
        return retVal

    def get_next_paydate(self):
        return self.global_next_paydate

    def get_paydates_in_range(self, start_date, end_date):
        paydates = None
        dateFormat = self.get_date_format()
        if self.ref_date != None:
            start_date_parsed = Date.parse_date(self, start_date, dateFormat)
            if start_date_parsed != None:
                start_date = wx.DateTime.FromDMY(start_date_parsed["day"], start_date_parsed["month"]-1, start_date_parsed["year"])
                end_date_parsed = Date.parse_date(self, end_date, dateFormat)
                if end_date_parsed != None:
                    end_date = wx.DateTime.FromDMY(end_date_parsed["day"], end_date_parsed["month"]-1, end_date_parsed["year"])
                    paydates = []
                    if end_date < start_date:
                        start_date, end_date = end_date, start_date
                    incr = self.get_pay_incr()
                    if incr != None:
                        ref_date_parsed = Date.parse_date(self, self.ref_date, dateFormat)
                        if ref_date_parsed != None:
                            test_paydate = wx.DateTime.FromDMY(ref_date_parsed['day'], ref_date_parsed['month']-1, ref_date_parsed['year'])
                            if test_paydate > start_date:
                                while test_paydate > start_date:
                                    test_paydate.Subtract(incr)
                                if test_paydate < start_date:
                                    test_paydate.Add(incr)
                            elif test_paydate < start_date:
                                while test_paydate < start_date:
                                    test_paydate.Add(incr)
                            if test_paydate == start_date:
                                pay_date = test_paydate.Format(self.dateFormat)
                                paydates.append(pay_date)
                                test_paydate.Add(incr)
                            while test_paydate <= end_date:
                                pay_date = test_paydate.Format(self.dateFormat)
                                paydates.append(pay_date)
                                test_paydate.Add(incr)
        return paydates

    def updatePayDates(self):
        self.set_curr_paydate()
        self.set_next_paydate()
        print("Curr paydate: %s, Next paydate: %s" % (self.global_curr_paydate, self.global_next_paydate))

    def CreateParams(self):
        self.payType = ""
        self.ref_date = ""
        self.netpay = ""
        self.payDepositAcct = ""

    def clear_all_assets(self):
        self.assets = AssetList(self)
        self.redraw_all(-1)

    def readConfigFile(self, cfgFile):
        if cfgFile == "":
            d = wx.FileDialog(self, "", "", "", "*.cfg", wx.FD_OPEN)
            if d.ShowModal() == wx.ID_OK:
                fname = d.GetFilename()
                dir = d.GetDirectory()
                total_name_in = os.path.join(dir, fname)
                self.cfgFile = total_name_in
        else:
            self.cfgFile = cfgFile
        try:
            file = open(self.cfgFile, 'r')
            lines = file.readlines()
            self.dateFormat = lines.pop(0).replace('\n', '')
            dateFormat = self.dateFormat
            Date.set_global_date_format(Date, dateFormat)
            self.payType = self.get_pay_types().index(lines.pop(0).replace('\n', ''))
            in_ref_date = lines.pop(0).replace('\n', '')
            ref_date = Date.parse_date(self, in_ref_date, self.dateFormat)
            self.ref_date = ref_date["dt"]
            self.netpay = lines.pop(0).replace('\n', '')
            payDepositAcct = lines.pop(0).replace('\n', '')
            self.payDepositAcct = payDepositAcct
            file.close()
            return True
        except:
            return False

    def writeConfigFile(self):
        if self.cfgFile == "":
            d = wx.FileDialog(self, "", "", "", "*.cfg", wx.FD_OPEN)
            if d.ShowModal() == wx.ID_OK:
                fname = d.GetFilename()
                dir = d.GetDirectory()
                total_name_in = os.path.join(dir, fname)
                self.cfgFile = total_name_in
        if self.cfgFile != "":
            file = open(self.cfgFile, 'w')
            dateFormat = self.get_date_format()
            file.write("%s\n" % dateFormat)
            payType = self.getPayType()
            payTypes = self.get_pay_types()
            file.write("%s\n" % payTypes[payType])
            ref_date = self.getRefDate()
            ref_date= self.get_display_date(ref_date)
            file.write("%s\n" % ref_date)
            file.write("%s\n" % self.netpay)
            file.write("%s\n" % self.payDepositAcct)
            file.close()

    def DisplayMsg(self, str):
        d = wx.MessageDialog(self, str, "Error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()

    def make_widgets(self):
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)
        self.make_filemenu()
        self.make_editmenu()
        self.make_helpmenu()
        self.setup_layout()

    def make_filemenu(self):
        self.filemenu = wx.Menu()
        ID_EXPORT_TEXT = wx.NewId()
        ID_ARCHIVE = wx.NewId()
        ID_IMPORT_CSV = wx.NewId()
        ID_IMPORT_XLSX = wx.NewId()
        ID_UPDATE_FROM_NET = wx.NewId()
        ID_PROPERTIES = wx.NewId()
        self.filemenu.Append(wx.ID_OPEN, "Open\tCtrl-o",
                             "Open a new transction file", wx.ITEM_NORMAL)
        self.filemenu.Append(wx.ID_SAVE, "Save\tCtrl-s",
                             "Save the current transactions in the same file", wx.ITEM_NORMAL)
        self.filemenu.Append(wx.ID_SAVEAS, "Save As",
                             "Save the current transactions under a different name", wx.ITEM_NORMAL)
        self.filemenu.Append(wx.ID_CLOSE, "Close\tCtrl-w",
                             "Close the current file", wx.ITEM_NORMAL)
        self.filemenu.Append(ID_EXPORT_TEXT, "Export Text",
                             "Export the current transaction register as a text file",
                             wx.ITEM_NORMAL)
        self.filemenu.Append(ID_ARCHIVE, "Archive",
                             "Archive transactions older than a specified date",
                             wx.ITEM_NORMAL)
        self.filemenu.AppendSeparator()
        self.filemenu.Append(ID_IMPORT_CSV, "Import CSV\tCtrl-c",
                             "Import transactions from a CSV file",
                             wx.ITEM_NORMAL)
        self.filemenu.Append(ID_IMPORT_XLSX, "Import XLSX file\tCtrl-i",
                             "Import transactions from an EXCEL file",
                             wx.ITEM_NORMAL)
        self.filemenu.Append(ID_UPDATE_FROM_NET, "Update Accounts from Net\tCtrl-u",
                             "Update accounts using pre-defined iMacros",
                            wx.ITEM_NORMAL)
        self.filemenu.AppendSeparator()
        self.filemenu.Append(ID_PROPERTIES, "Properties\tCtrl-p",
                             "Display and/or edit Number and Data/Time display properties, pay frequencies",
                            wx.ITEM_NORMAL)
        self.filemenu.AppendSeparator()
        self.filemenu.Append(wx.ID_EXIT, "Quit\tCtrl-q",
                             "Exit PyAsset", wx.ITEM_NORMAL)
        self.menubar.Append(self.filemenu, "&File")
        self.Bind(wx.EVT_MENU, self.load_file, None, wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.save_file, None, wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.save_as_file, None, wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.close, None, wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.export_text, None, ID_EXPORT_TEXT)
        self.Bind(wx.EVT_MENU, self.archive, None, ID_ARCHIVE)
        self.Bind(wx.EVT_MENU, self.import_CSV_file, None, ID_IMPORT_CSV)
        self.Bind(wx.EVT_MENU, self.import_XLSX_file, None, ID_IMPORT_XLSX)
        self.Bind(wx.EVT_MENU, self.update_from_net, None, ID_UPDATE_FROM_NET)
        self.Bind(wx.EVT_MENU, self.properties, None, ID_PROPERTIES)
        self.Bind(wx.EVT_MENU, self.quit, None, wx.ID_EXIT)

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
        self.Bind(wx.EVT_MENU, self.newentry, None, wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.deleteentry, None, ID_DELETE_ENTRY)
        self.Bind(wx.EVT_MENU, self.sort, None, ID_SORT)

    def make_helpmenu(self):
        ID_HELP = wx.NewId()
        self.helpmenu = wx.Menu()
        self.helpmenu.Append(wx.ID_ABOUT, "About",
                             "About PyAsset", wx.ITEM_NORMAL)
        self.helpmenu.Append(ID_HELP, "Help\tCtrl-h",
                             "PyAsset Help", wx.ITEM_NORMAL)

        self.menubar.Append(self.helpmenu, "&Help")
        self.Bind(wx.EVT_MENU, self.about, None, wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.gethelp, None, ID_HELP)

    def make_bill_button(self, panel):
        self.billButton = Button(panel, label = "Bills")
        self.billButton.Bind(wx.EVT_LEFT_DOWN, self.onBillButtonClick)

    def onBillButtonClick(self, evt):
        try:
#            print(self.frame.latest_bills)
            self.bills_frame = BillFrame(None, self, -1, self.frame.latest_bills)
        except:
            self.DisplayMsg("No bills in the system yet")

    def get_bills_frame(self):
        return self.bills_frame

    def make_date_grid(self, panel):
        self.currDateLabel = wx.StaticText(panel, label="Curr Date")
        dates = Date(self, self.ref_date, Date.get_global_date_format(Date), self.payType)
        curr_date = dates.get_curr_date()
        if type(curr_date) is wx.DateTime:
            curr_date = curr_date.Format(self.get_date_format())
        self.currDateInput = wx.StaticText(panel, label=curr_date)
        self.projDateLabel = wx.StaticText(panel, label="Proj Date")
        displayDateFormat =  Date.get_global_date_format(Date).replace("%m", "mm").replace("%d", "dd").replace("%y","yy").replace("%Y", "yyyy")
        self.projDateInput = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, value= displayDateFormat)
        self.currPayDateLabel = wx.StaticText(panel, label="Current Pay Date")
        self.currPayDate = self.get_curr_paydate()
        self.currPayDateOutput = wx.StaticText(panel, label=str(self.currPayDate))
        self.nextPayDateLabel = wx.StaticText(panel, label="Next Pay Date")
        self.nextPayDate = self.get_next_paydate()
        self.nextPayDateOutput = wx.StaticText(panel, label=str(self.nextPayDate))
        self.projDateInput.Bind(wx.EVT_TEXT_ENTER,self.onProjDateEntered)

    def update_date_grid_dates(self, oldDateFormat, newDateFormat):
        if type(self.curr_date) is str:
            curr_date_label = self.curr_date
            if curr_date_label == "":
                curr_date_label =  Date.get_global_date_format(Date).replace("%m", "mm").replace("%d", "dd").replace("%y","yy").replace("%Y", "yyyy")
        else:
            curr_date_label = self.curr_date["str"]
        self.currDateInput.LabelText = curr_date_label
        self.currDateInput.Refresh()
        if type(self.proj_date) is str:
            proj_date_label = self.curr_date
            if proj_date_label == "":
                proj_date_label =  Date.get_global_date_format(Date).replace("%m", "mm").replace("%d", "dd").replace("%y","yy").replace("%Y", "yyyy")
        else:
            proj_date_label = self.proj_date["str"]
        self.projDateInput.LabelText = proj_date_label
        self.projDateInput.Refresh()
        self.updatePayDates()
        if oldDateFormat in Date.getDateFormats(self):
            self.curr_paydate = self.currPayDate
        self.currPayDateOutput.LabelText = self.get_curr_paydate()
        self.currPayDateOutput.Refresh()
        if oldDateFormat in Date.getDateFormats(self):
            next_paydate=self.next_paydate
        self.nextPayDateOutput.LabelText = self.get_next_paydate()
        self.nextPayDateOutput.Refresh()

    def onProjDateEntered(self, evt):
        in_date = evt.String
        date_format = Date.get_global_date_format(Date)
        returned_date = Date.parse_date(self, in_date, date_format)
        if returned_date != None:
            self.proj_date = wx.DateTime.FromDMY(returned_date["day"], returned_date["month"] - 1, returned_date["year"])
            self.proj_year = returned_date["year"]
            self.proj_month = returned_date["month"]
            self.proj_day = returned_date["day"]
            print("Projected date %s, parse: Month: %02d, Day: %02d, Year: %04d" %
                  (self.proj_date.Format(self.dateFormat), self.proj_month, self.proj_day, self.proj_year))
            Date.set_proj_date(self, in_date)
            self.assets.update_proj_values(in_date)
            self.redraw_all()
            paydates = self.get_paydates_in_range(Date.get_global_curr_date(self), in_date)
            print("Pay dates in ramge %s-%s: %s" % (Date.get_global_curr_date(self), in_date, paydates))
        else:
            self.proj_date = None
            self.DisplayMsg("Bad projected date ignored: %s" % (in_date))

    def make_asset_grid(self, panel):
        self.assetGrid = AssetGrid(panel)
        self.needed_width = self.assetGrid.set_properties(self)

    def add_transaction_frame(self, row, col):
        name = self.assets[row].name
        transactions = self.assets[row].transactions
        self.trans_frame = TransactionFrame(None, self, -1, row, transactions, name)

    def get_transaction_frame(self):
        try:
            return self.trans_frame
        except:
            return None

    def setup_layout(self):
        self.panel = wx.Panel(self)

        self.make_bill_button(self.panel)
        self.make_date_grid(self.panel)
        self.make_asset_grid(self.panel)

        self.date_fgs = wx.FlexGridSizer(1, 9, 5, 5)
        self.date_fgs.AddMany([(self.billButton),
        (self.currDateLabel,1,wx.ALIGN_CENTER),
        (self.currDateInput,1,wx.EXPAND),
        (self.projDateLabel,1,wx.ALIGN_CENTER),
        (self.projDateInput,1,wx.EXPAND),
        (self.currPayDateLabel,1,wx.ALIGN_CENTER),
        (self.currPayDateOutput,1,wx.EXPAND),
        (self.nextPayDateLabel,1,wx.ALIGN_CENTER),
        (self.nextPayDateOutput,1,wx.EXPAND)])

        self.asset_fgs = wx.FlexGridSizer(2, 1, 0, 0)
        self.asset_fgs.Add(self.assetGrid, proportion=1, flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.EXPAND)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.date_fgs)
        self.mainSizer.Add(self.asset_fgs)

        self.panel.Fit()
        self.panel.SetSizer(self.mainSizer)
        self.date_fgs.SetSizeHints(self.panel)
        self.asset_fgs.SetSizeHints(self.panel)

        self.Fit()
        self.Layout()
        self.Show()

    def redraw_all(self, index=-1):
        self.edited = True
        nassets = len(self.assets)
        if index == -1:
            nrows = nassets + 1
            if nrows > 0 and (index == None or index == -1):
                self.assetGrid.DeleteRows(0, nrows)
                nrows = 0
            start_range = 0
            end_range = nassets
            if nrows < nassets:
                rows_needed = nassets - nrows
                self.assetGrid.AppendRows(rows_needed)
        else:
            start_range = index
            end_range =  start_range + 1
        for row in range(start_range, end_range):
            for col in range(self.assetGrid.getNumLayoutCols()):
                ret_val = wx.OK
                if row < 0 or row >= len(self.assets):
                    str = "Warning: skipping redraw on bad cell %d %d!" % (row, col)
                    ret_val = self.DisplayMsg(str)
                if ret_val != wx.OK:
                    continue

                # Logic to always display Value (Curr), Value (Proj), Avail(Proj), Amt Over, Cash Limit, Cash Used and Cash Avail for credit cards,store cards, and overdraft
                asset_type = self.assets[row].get_type()
                col_name = self.assetGrid.getColName(col)
                self.assetGrid.setColZeroSuppress(row, col, True)
                if (asset_type == "store card" or asset_type == "credit card" or asset_type == "overdraft") and ("Curr" in col_name or "Proj" in col_name or "Amt" in col_name or "Cash" in col_name):
                    self.assetGrid.setColZeroSuppress(row, col, False)
                cellValue = self.assetGrid.GridCellDefaultRenderer(row, col)
                cellType = self.assetGrid.getColType(col)
                if cellType == self.assetGrid.DOLLAR_TYPE:
                    self.assetGrid.GridCellDollarRenderer(row, col)
                elif cellType == self.assetGrid.RATE_TYPE:
                    self.assetGrid.GridCellPercentRenderer(row, col)
                elif cellType == self.assetGrid.DATE_TYPE:
                    self.assetGrid.GridCellDateRenderer(row, col)
                elif cellType == self.assetGrid.DATE_TIME_TYPE:
                    self.assetGrid.GridCellDateTimeRenderer(row, col)
                elif cellType == self.assetGrid.STRING_TYPE:
                    self.assetGrid.GridCellStringRenderer(row, col)
                else:
                    self.assetGrid.GridCellErrorRenderer(row, col)
        if index == -1:
            self.assetGrid.SetGridCursor(0, 0)              # was (nassets-1, 0)
            self.assetGrid.MakeCellVisible(0, True)         # was (nassets-1, 0)
        elif index > 0:
            self.assetGrid.SetGridCursor(index, 0)
            self.assetGrid.MakeCellVisible(index, True)

    def update_asset_grid_dates(self, oldDateFormat, newDateFormat):
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

    def assetchange(self, evt):
        row = evt.GetRow()
        col = evt.GetCol()
        val = evt.String
        modified = True
        colName = self.assetGrid.getColName(col)
        if colName == "Acct name":
            self.assets[row].set_name(val)
        elif colName == "Curr val":
            self.assets[row].set_value(val)
        elif colName == "Last pulled":
            self.assets[row].set_last_pull_date(val)
        elif colName == "Limit":
            self.assets[row].set_limit(val)
        elif colName == "Avail online":
            self.assets[row].set_avail(val)
        elif colName == "Rate":
            self.assets[row].set_rate(val)
        elif colName == "Payment amt":
            self.assets[row].set_payment(val)
        elif colName == "Due date":
            self.assets[row].set_due_date(val)
        elif colName == "Sched date":
            self.assets[row].set_sched_date(val)
        elif colName == "Min Pmt":
            self.assets[row].set_min_pay(val)
        elif colName == "Stmt Bal":
            self.assets[row].set_stme_bal(val)
        elif colName == "Amt Over":
            self.assets[row].set_amt_over(val)
        elif colName == "Cash Limit":
            self.assets[row].set_cash_limit(val)
        elif colName == "Cash Used":
            self.assets[row].set_cash_used(val)
        elif colName == "Cash Avail":
            self.assets[row].set_cash_avail(val)
        else:
            print("assetchange: Warning: modifying incorrect cell! row, ", row, " col ", col)
            modified = False

        if modified == True:
            self.edited = True

    def update_all_Date_Formats(self, oldDateFormat, newDateFormat):
        self.update_date_grid_dates(oldDateFormat, newDateFormat)
        self.update_asset_grid_dates(oldDateFormat, newDateFormat)

# Updating transaction grid dates isn't working yet       TODO   JJG 1/13/2024
#        transaction_frame = self.get_transaction_frame()
#        if transaction_frame != None:
#            transaction_frame.update_transaction_grid_dates(oldDateFormat, newDateFormat)
        self.edited = True

    def load_file(self, assetFile):
        latest_assets = qif.load_file(self, "")
        if latest_assets != None:
            self.process_asset_list(latest_assets)

    def write_assets(self, file_name):
        assetList = self.assets.assets
        for cur_asset in assetList:
            cur_asset.write_qif(file_name)
        self.edited = False

    def save_file(self, *args):
        assetFile = copy.deepcopy(self.assetFile)
        if assetFile == "":
           d = wx.FileDialog(self, "", "", "", "*.qif", wx.FD_OPEN)
           if d.ShowModal() == wx.ID_OK:
               fname = d.GetFilename()
               dir = d.GetDirectory()
               total_name_in = os.path.join(dir, fname)
               self.assetFile = copy.deepcopy(total_name_in)
        else:
           self.assetFile = copy.deepcopy(assetFile)
        assetFile = copy.deepcopy(self.assetFile)
        file = open(assetFile, 'w')                             # Make sure file starts empty! JJG 1/17/2024
        file.close()
        if len(self.assets) != 0:
            if assetFile != "":
                self.write_assets(assetFile)

    def save_as_file(self, *args):
        self.assetFile = None
        self.save_file(self)

    def close(self, *args):
#        if self.edited:
#            self.save_file(self)                                            # Not sure if this is all we need to do however it'll do for now!  JJG 1/17/2024
        self.cur_asset = None
        del self.assets
        del self.bills
        self.assets = AssetList(self)
        self.bills = BillList()
        self.redraw_all()
        self.edited = False
        self.SetTitle("PyAsset: Asset")


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
#        next(csvdeff, None)

        for settings in csvdeff:
            date_ = int(settings[0])  # convert to
            amount_ = int(settings[2])  # How much was the transaction
            memo_ = int(settings[3])  # description of the transaction
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
            total_name_extension_place = total_name_in.find(".")
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
                self.cur_asset = self.qif.read_qif(total_name_qif)
                fromfile.close()
                deffile.close()
                self.redraw_all(-1)
                if self.cur_asset.name:
                    self.SetTitle("PyAsset: %s" % self.cur_asset.name)
            else:
                self.MsgBox(error)
                return

    def process_asset_list(self, assetList):
        for i in range(len(assetList.assets)):
            cur_asset = assetList.assets[i]
            cur_name = cur_asset.get_name()
            j = self.assets.index(cur_name)
            if  j != -1:
                self.assets.assets[j] = cur_asset           # For now, just replace, when dates are working, save later date JJG 1/22/2022
            else:            
                self.assets.append_by_object(cur_asset)
        self.redraw_all()

    def import_XLSX_file(self, *args):
        # Appends or Merges as appropriate the records from a .xlsx file to the current Asset
        d = wx.FileDialog(self, "Import", "", "", "*.xlsx", wx.FD_OPEN)
        if d.ShowModal() == wx.ID_OK:
            self.edited = True
            fname = d.GetFilename()
            dir = d.GetDirectory()
            total_name_in = os.path.join(dir, fname)
            error = ""
            try:
                fromfile = open(total_name_in, 'r')
                fromfile.close()
            except:
                error = total_name_in + ' does not exist / cannot be opened !!\n'

            if error == "":
                self.cur_assets = None
                xlsm = ExcelToAsset(ignore_sheets=['Assets', 'Bills', 'Shop Your Way transactions', 'Slate transactions', 'Slate old transactions'])
                xlsm.OpenXLSMFile(total_name_in)
                latest_assets = xlsm.ProcessAssetsSheet(self)
                self.process_asset_list(latest_assets)
                transaction_sheet_names = xlsm.GetTransactionSheetNames()
                for sheet in transaction_sheet_names:
                    sheet_index = self.assets.index(sheet)
                    if sheet_index != -1:
                        self.assets[sheet_index].transactions = xlsm.ProcessTransactionSheet(self.assets[sheet_index], sheet)
                        if self.assets[sheet_index].transactions:
                             proj_value = self.assets[sheet_index].transactions.update_current_and_projected_values()
                             self.assets[sheet_index].set_value_proj(proj_value)
                    else:
                        print(sheet + " not found in asset list")

#                self.latest_bills = xlsm.ProcessBillsSheet(self.bills)             # TODO JJG 1/7/2024 Fix this to do dates correctly!
            else:
                self.DisplayMsg(error)

    def update_from_net(self, *args):
        w = iMacrosToAsset()
        w.Init()
        net_asset_codes = [
                           ("HFCU",1,[False,False,False,True]),
                           #("BOA",-1,[False,True]),
                           #("AMEX",-1,[True,True]),
                           #("CITI",-1,[True]),
                           #("MACYS",-1,[True]),
                           #("SYW",-1,[True]),
                           #("TSP",-1,[False,False,False,True]),
                           #("MET",1,[False])
                           ]
        for net_asset_code in net_asset_codes:
            latest_assets = w.GetNetInfo(net_asset_code)
            #print latest_assets
            for i in range(len(latest_assets)):
                net_asset = latest_assets.__getitem__(i)
                if net_asset != None:
                    latest_name = net_asset.get_name()
                    found = False
                    for j in range(len(self.assets)):
                        cur_name = self.assets[j].get_name()
                        if "(" in cur_name:
                            cur_name = cur_name.split("(")[1].split(")")[0]
                        if cur_name in latest_name:
                            net_index = j
                            found = True
                            found = Tr
                            break
                    if not found:
                        self.assets.append(latest_name)
                        net_index = -1
                    # Always update Value (Curr) column and type ... others check if non-zero value before update is done!
                    self.assets[net_index].set_value(net_asset.get_value())
                    self.assets[net_index].set_type(net_asset.get_type())
                    if net_asset.get_value_proj() != 0.0:
                        self.assets[net_index].set_value_proj(net_asset.get_value_proj())
                    if net_asset.get_last_pull_date() != 0.0:
                        self.assets[net_index].set_last_pull_date(net_asset.get_last_pull_date())
                    if net_asset.get_limit() != 0.0:
                        self.assets[net_index].set_limit(net_asset.get_limit())
                    if net_asset.get_avail() != 0.0:
                        self.assets[net_index].set_avail(net_asset.get_avail())
                    if net_asset.get_avail_proj() != 0.0:
                        self.assets[net_index].set_avail_proj(net_asset.get_avail_proj())
                    if net_asset.get_rate() != 0.0:
                        self.assets[net_index].set_rate(net_asset.get_rate())
                    if net_asset.get_payment() != 0.0:
                        self.assets[net_index].set_payment(net_asset.get_payment())
                    if net_asset.get_due_date() != None:
                        self.assets[net_index].set_due_date(net_asset.get_due_date())
                    if net_asset.get_sched_date() != None:
                        self.assets[net_index].set_sched_date(net_asset.get_sched_date())
                    if net_asset.get_min_pay() != 0.0:
                        self.assets[net_index].set_min_pay(net_asset.get_min_pay())
                    if net_asset.get_stmt_bal() != 0.0:
                        self.assets[net_index].set_stmt_bal(net_asset.get_stmt_bal())
                    if net_asset.get_amt_over() != 0.0:
                        self.assets[net_index].set_amt_over(net_asset.get_amt_over())
                    if net_asset.get_cash_limit() != 0.0:
                        self.assets[net_index].set_cash_limit(net_asset.get_cash_limit())
                    if net_asset.get_cash_used() != 0.0:
                        self.assets[net_index].set_cash_used(net_asset.get_cash_used())
                    if net_asset.get_cash_avail() != 0.0:
                        self.assets[net_index].set_cash_avail(net_asset.get_cash_avail())
        w.Finish()
        self.redraw_all()

    def properties(self, *args):
        oldDateFormat = Date.get_global_date_format(Date)
        ref_date_parsed = Date.parse_date(self, self.getRefDate(), oldDateFormat)
        if ref_date_parsed != None:
            ref_date_dt = ref_date_parsed["dt"]
        else:
            curr_date = wx.DateTime.Today()
            ref_date_dt = Date.parse_date(self, curr_date, oldDateFormat)["dt"]         # Set reference date to current date if none given JJG 12/25/2023 Merry Christmas!
        self.setRefDate(wx.DateTime.FromDMY(ref_date_dt.day, ref_date_dt.month, ref_date_dt.year).Format(oldDateFormat))
        frame = PropertyFrameWithForm(self, oldDateFormat, self.payType, self.ref_date, self.netpay, self.payDepositAcct)
        frame.ShowModal()
        if self.cfgFile != "":
            self.writeConfigFile()
        self.updatePayDates()
        self.pay_dates = self.get_paydates_in_range(self.curr_date, self.proj_date)
        print("Pay dates in range %s-%s: %s" % (self.get_display_date(self.curr_date), self.get_display_date(self.proj_date), self.pay_dates))
        newDateFormat = Date.get_global_date_format(Date)
        self.update_all_Date_Formats(oldDateFormat, newDateFormat)
        #TO DO: Add logic to update Salary transactions and Bill transactions for pay_dates
        Date.set_global_date_format(Date, newDateFormat)


    def setDateFormat(self, new_DateFormat):
        self.dateFormat = new_DateFormat

    def setPayType(self, new_type):
        self.payType = new_type

    def setRefDate(self, new_ref_date):
        self.ref_date = new_ref_date

    def setNetPay(self, new_netpay):
        self.netpay = new_netpay

    def setPayDepositAcct(self, new_PayDepositAcct):
        self.payDepositAcct = new_PayDepositAcct

    def getDateFormat(self):
        return self.dateFormat

    def getPayType(self):
        return self.payType

    def getRefDate(self):
        return self.ref_date

    def getNetPay(self):
        return self.netpay

    def getPayDepositAcct(self):
        return self.payDepositAcct

    def export_text(self, *args):
        d = wx.FileDialog(self, "Save", "", "", "*.txt", wx.SAVE)
        if d.ShowModal() == wx.ID_OK:
            fname = d.GetFilename()
            dir = d.GetDirectory()
            self.cur_asset.write_txt(os.path.join(dir, fname))

    def archive(self, *args):
        d = wx.TextEntryDialog(self,
                               "Archive transactions before what date (mm/dd/yy)?",
                               "Archive Date")
        if d.ShowModal() == wx.ID_OK:
            date = Date(d.GetValue())
        else:
            date = None
        d.Destroy()
        if not date:
            return
        archive = Asset()
        newcb_starttransaction = Transaction()
        newcb_starttransaction.amount = 0
        newcb_starttransaction.payee = "Starting Balance"
        newcb_starttransaction.memo = "Archived by PyAsset"
        newcb_starttransaction.state = "cleared"
        newcb_starttransaction.date = date

        newcb = Asset()
        newcb.filename = self.cur_asset.filename
        newcb.name = self.cur_asset.name
        newcb.append(newcb_starttransaction)
        archtot = 0

        for transaction in self.cur_asset:
            if transaction.date < date and transaction.state == "cleared":
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
        self.edited = True

    def newentry(self, *args):
        self.edited = True
        self.assets.assets.append("New Asset")
        self.assetGrid.AppendRows()
        nassets = self.assetGrid.GetNumberRows()
        self.assetGrid.SetGridCursor(nassets - 1, 0)
        self.assetGrid.MakeCellVisible(nassets - 1, 1)
        self.redraw_all()

    def sort(self, *args):
        self.edited = True
        self.assets.sort()
        self.redraw_all()

    def deleteentry(self, *args):
        index = self.assetGrid.GetGridCursorRow()
        indices = self.assetGrid.SelectedCells
        if index >= 0:
            d = wx.MessageDialog(self,
                                 "Really delete this asset?",
                                 "Really delete?", wx.YES_NO)
            if d.ShowModal() == wx.ID_YES:
                del self.assets[index]
            self.redraw_all()  # TODO: Can we make a self.redraw(index-1)  so that only the assets[index-1:] get updated?  JJG 07/09/2021

    def about(self, *args):
        d = wx.MessageDialog(self,
                             "Python Asset Manager\n"
                             "Copyright (c) 2016-2024 Joseph J. Gorak\n"
                             "Released under the Gnu GPL\n",
                             "About PyAsset",
                             wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()

    def gethelp(self, *args):
        d = HelpDialog(self, -1, "Help", __doc__)
        val = d.ShowModal()
        d.Destroy()

    def MsgBox(self, message):
        d = wx.MessageDialog(self, message, "error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()

    def set_global_curr_paydate(self, curr_paydate):
        global_curr_paydate = curr_paydate

    def get_global_curr_paydate(self):
        return Date.global_curr_paydate

    def set_global_next_paydate(self, next_paydate):
        global_projnext_paydate = next_paydate

    def get_global_next_paydate(self):
        return Date.global_next_paydate