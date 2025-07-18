#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2016-2025 Joseph J. Gorak. All rights reserved.
This code is in development -- use at your own risk. Email
comments, patches, complaints to joegorak808@outlook.com

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
#  05/25/2024     Version v0.4         fixed bugs with Bill support and projected date logic

# To Do list (possible new features?):
# Speed redraw_all: break o redraw_all, redraw_range, redraw_totals
# Save a backup version of files
# Read and save CBB files?
# Undo?
# Plot balance vs day
# Search functions
# goto date

from ast import Pass
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
from Bill import Bill
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
    global_curr_paydate = "%m/%d/%Y"
    global_next_paydate = "%m/%d/%Y"

    def __init__(self, parent, title="PyAsset", cfgFile="", assetFile=""):
        self.parent = parent
        self.frame = self
        self.assets = AssetList(self)
        self.bills = None
        self.bills_frame = None
        self.qif = qif(self)
        self.cur_asset = Asset(name=assetFile)
        self.cfgFile = copy.deepcopy(cfgFile)
        self.assetFile = copy.deepcopy(assetFile)
        self.CreateParams()
        super(AssetFrame, self).__init__(parent, title=title)
        self.make_widgets()

        self.curr_date = Date.set_curr_date(Date)
        self.proj_date = self.curr_date                         # JJG 5/13/2024 Set proj date to curr date initially
        Date.set_global_curr_date(self, self.curr_date)
        Date.set_global_proj_date(self, self.proj_date)

        self.checkForConfigFile(self.cfgFile)
        oldDateFormat = Date.get_global_date_format(Date)

        self.processConfigFile(self.cfgFile)
        self.set_curr_paydate()
        self.set_next_paydate()

        newDateFormat = Date.get_global_date_format(Date)
        self.update_date_dates(oldDateFormat, newDateFormat)
        self.update_all_Date_Formats(oldDateFormat, newDateFormat)
        oldDateFormat = newDateFormat
        oldRefDate = self.ref_date
        oldDateSep = Date.get_global_date_sep(self)

        self.redraw = False
        if self.assetFile:
            ext_loc = self.assetFile.find(".")
            ext = self.assetFile[ext_loc:]
            self.edited = False
            if ext == ".qif":
                latest_assets = qif.load_file(self, self.assetFile)
                if latest_assets != None:
                    self.process_asset_list(latest_assets, 'add')
                    self.redraw = True
            elif ext == ".xlsx":
                latest_assets = self.process_XLSX_file(self.assetFile)
                if latest_assets != None:
                    self.redraw = True
            else:
                error = "Can't determine type of assetFile: " + self.assetFile + " - skipping"
                self.MsgBox(error)
        if self.redraw:
            self.redraw_all()

        oldDateFormat = Date.get_global_date_format(Date)
        oldPayType = self.getPayType()
        oldRefDate = self.getRefDate()
        oldNetPay = self.getNetPay()
        oldPayDepositAcct = self.getPayDepositAcct()
        self.curr_date = self.proj_date = Date.set_curr_date(self)
        currDate = Date.parse_date(self, self.curr_date, Date.get_global_date_format(Date))
        self.projDate = currDate
        self.edited = False

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

    def get_curr_date(self):
        return self.curr_date

    def get_proj_date(self):
        return self.proj_date

    def set_curr_paydate(self):
        retVal = ""
        if self.ref_date != None:
            if type(self.ref_date) is DateTime:
                ref_date = self.ref_date
            else:
                if type(self.ref_date) is str:
                    self.ref_date = Date.parse_date(Date, self.ref_date, Date.get_global_date_format(Date))
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
            else:
                self.next_paydate = ""
        self.global_next_paydate = retVal
        self.nextPayDateOutput.LabelText = retVal
        return retVal

    def get_next_paydate(self):
        return self.global_next_paydate

    def process_paydates_in_range(self, start_date, end_date):
        paydates = None
        dateFormat = self.get_date_format()
        if self.ref_date != None:
            start_date = Date.parse_date(self, start_date, dateFormat)
            start_date = wx.DateTime.FromDMY(start_date['day'], start_date['month']-1, start_date['year'])
            end_date = Date.parse_date(self, end_date, dateFormat)
            end_date = wx.DateTime.FromDMY(end_date['day'], end_date['month']-1, end_date['year'])
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
                        pay_date = test_paydate.Format(dateFormat)
                        paydates.append(pay_date)
                        test_paydate.Add(incr)
                    while test_paydate <= end_date:
                        pay_date = test_paydate.Format(dateFormat)
                        paydates.append(pay_date)
                        test_paydate.Add(incr)
                    if self.getPayDepositAcct() != "":
                        payDepositAccount = self.assets.get_asset_by_name(self.getPayDepositAcct())
                        payDepositAccountTransations = payDepositAccount.get_transactions()
                        for paydate in paydates:
#                            print("Checking if a salary transaction for " + paydate + " exists in account " + payDepositAccount.get_name())
                            if not payDepositAccount.transaction_exists("Salary", paydate):
#                                print("We will insert a new salary transaction for " + paydate + " in accout " + payDepositAccount.get_name() + " here!")
                                new_transaction = Transaction(self.parent, payee="Salary", action="+", due_date=paydate, sched_date=paydate, pmt_method="Direct Deposit", amount=self.getNetPay(), state="outstanding")
                                payDepositAccount.transactions.insert(new_transaction)

        return paydates

    def process_bills_sched_in_range(self, start_date, end_date):
    #TODO : JJG 6/28/2025 Need to add code to iterate if sched_date for a bill that goes more than a month, quarter or year
        bills_sched = []
        if self.bills != None:
            bills = self.bills
            dateFormat = self.get_date_format()
            start_date = Date.parse_date(self, start_date, dateFormat)["dt"]
            end_date = Date.parse_date(self, end_date, dateFormat)["dt"]
            if end_date < start_date:
                start_date, end_date = end_date, start_date
            for bill in bills:
                sched_date = bill.get_sched_date()
                if sched_date != None:
                    sched_date_parsed = Date.parse_date(self, sched_date, dateFormat)
                    if sched_date_parsed != None:
                        sched_dt = wx.DateTime.FromDMY(sched_date_parsed['day'], sched_date_parsed['month'] - 1, sched_date_parsed['year'])
                        if start_date <= sched_dt <= end_date:
                            bills_sched.append(bill)
                            inc_value = Bill.get_bill_inc_value(bill.get_pmt_frequency())

            if bills_sched != []:
                bills_sched = BillList(bills_sched).sort_by_fields([['Sched Date', '>'], ['Frequency', '>']])
                for bill in bills_sched:
#                    print("Processing bill: %s, Sched date: %s, Frequency: %s" % (bill.get_payee(), bill.get_sched_date(), bill.get_pmt_frequency()))
                    pmt_acct = self.assets.get_asset_by_name(bill.get_pmt_acct())
                    if not pmt_acct.transaction_exists(bill.get_payee(), bill.get_due_date()):
                        new_transaction = Transaction(self.parent, payee=bill.get_payee(), action=bill.get_action(), due_date=bill.get_due_date(), sched_date=bill.get_sched_date(), pmt_method=bill.get_pmt_method(), amount=bill.get_amount(), state="outstanding")
                        pmt_acct.transactions.insert(new_transaction)
        return bills_sched

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

    def checkForConfigFile(self, cfgFile):
        if cfgFile == "":
#            d = wx.FileDialog(self, "", "", "", "*.cfg", wx.FD_OPEN)
#            if d.ShowModal() == wx.ID_OK:
                fname = "pyAsset.cfg"                       # JJG 6/28/2025  Force a known name for testing
#                dir = d.GetDirectory()
                dir = os.getcwd()                           # JJG 6/28/2025 Store cfg in current working directory for testing
                total_name_in = os.path.join(dir, fname)
                self.cfgFile = total_name_in
        else:
            self.cfgFile = cfgFile

    def processConfigFile(self, cfgFile):
        try:
            file = open(self.cfgFile, 'r')
            lines = file.readlines()
            self.dateFormat = lines.pop(0).replace('\n', '')
            Date.set_global_date_format(Date, self.dateFormat)
            self.payType = self.get_pay_types().index(lines.pop(0).replace('\n', ''))
            if self.payType == "" or self.payType == None:
                self.payType = "every 2 weeks"                                 # JJG 12/23/2023   added default if no payType given
            in_ref_date = lines.pop(0).replace('\n', '')
            ref_date = Date.parse_date(self, in_ref_date, self.dateFormat)
            self.setRefDate(ref_date)
            self.netpay = lines.pop(0).replace('\n', '')
            payDepositAcct = lines.pop(0).replace('\n', '')
            self.payDepositAcct = payDepositAcct
            file.close()
        except:
            self.properties()

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
            ref_date= Date.get_display_date(Date,ref_date)
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
        self.fileMenuItem = {}
        ID_EXPORT_TEXT = wx.NewId()
        ID_ARCHIVE = wx.NewId()
        ID_IMPORT_CSV = wx.NewId()
        ID_IMPORT_XLSX = wx.NewId()
        ID_UPDATE_FROM_NET = wx.NewId()
        ID_PROPERTIES = wx.NewId()
        self.fileMenuItem["Open"] = self.filemenu.Append(wx.ID_OPEN, "Open\tCtrl-o",
                             "Open a new asset file", wx.ITEM_NORMAL)
        self.fileMenuItem["Save"] = self.filemenu.Append(wx.ID_SAVE, "Save\tCtrl-s",
                             "Save the current asset in the same file", wx.ITEM_NORMAL)
        self.fileMenuItem["SaveAs"] = self.filemenu.Append(wx.ID_SAVEAS, "Save As",
                             "Save the current assets under a different name", wx.ITEM_NORMAL)
        self.fileMenuItem["Close"] = self.filemenu.Append(wx.ID_CLOSE, "Close\tCtrl-w",
                             "Close the current file", wx.ITEM_NORMAL)
        self.fileMenuItem["Export"] = self.filemenu.Append(ID_EXPORT_TEXT, "Export Text",
                             "Export the current assets as a text file",
                             wx.ITEM_NORMAL)
        self.fileMenuItem["Archive"] = self.filemenu.Append(ID_ARCHIVE, "Archive",
                             "Archive assets older than a specified date",
                             wx.ITEM_NORMAL)
        self.filemenu.AppendSeparator()
        self.fileMenuItem["ImportCSV"] = self.filemenu.Append(ID_IMPORT_CSV, "Import CSV\tCtrl-c",
                             "Import assets and transactions from a CSV file",
                             wx.ITEM_NORMAL)
        self.fileMenuItem["ImportXLSX"] = self.filemenu.Append(ID_IMPORT_XLSX, "Import XLSX file\tCtrl-i",
                             "Import assets and transactions from an EXCEL file",
                             wx.ITEM_NORMAL)
# JJG 6/28/2025 Need to determine new way to update asset from net since no more iMacros support
#        self.fileMenuItem["Update"] = self.filemenu.Append(ID_UPDATE_FROM_NET, "Update assets from Net\tCtrl-u",
#                             "Update assets using pre-defined iMacros",
#                            wx.ITEM_NORMAL)
        self.filemenu.AppendSeparator()
        self.fileMenuItem["Properties"] = self.filemenu.Append(ID_PROPERTIES, "Properties\tCtrl-p",
                             "Display and/or edit Number and Data/Time display properties, pay frequencies and direct deposit account",
                            wx.ITEM_NORMAL)
        self.filemenu.AppendSeparator()
        self.fileMenuItem["Quit"] = self.filemenu.Append(wx.ID_EXIT, "Quit\tCtrl-q",
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
#        self.Bind(wx.EVT_MENU, self.update_from_net, None, ID_UPDATE_FROM_NET)
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
        if self.bills != None:
           self.bills = BillList(self.bills)                               # JJG 1/26/2025 Create a new bill list if none exists
        if self.bills_frame == None:
            self.bills_frame = BillFrame(None, self, -1, self.bills)
        else:
            pass                                # TODO: Add code to bring frame into focus on top! JJG 1/26/2025

    def getBillFrame(self):
        return self.bills_frame

    def removeBillFrame(self):
        self.bills_frame.Destroy()
        self.bills_frame = None

    def make_date_grid(self, panel):
        self.currDateLabel = wx.StaticText(panel, label="Curr Date")
        dates = Date(self, self.ref_date, Date.get_global_date_format(Date), self.payType)
        curr_date = dates.get_curr_date()
        if type(curr_date) is wx.DateTime:
            curr_date = curr_date.Format(self.get_date_format())
        self.currDateInput = wx.StaticText(panel, label=curr_date["str"])
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

    def update_date_dates(self, oldDateFormat, newDateFormat):
        if type(self.curr_date) is str:
            curr_date_label = Date.parse_date(Date, self.curr_date["str"], oldDateFormat)["str"]
        else:
            dt = self.curr_date["dt"]
            curr_date_label = wx.DateTime.FromDMY(dt.day, dt.month, dt.year).Format(Date.get_global_date_format(Date))
        self.currDateInput.LabelText = curr_date_label
        self.currDateInput.Refresh()
        if type(self.proj_date) is str:
            proj_date_label = Date.parse_date(Date, self.proj_date["str"], oldDateFormat)["str"]
        else:
            dt = self.proj_date["dt"]
            proj_date_label = wx.DateTime.FromDMY(dt.day, dt.month, dt.year).Format(Date.get_global_date_format(Date))
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
        parsed_proj_date = Date.parse_date(self, in_date, date_format)
        if parsed_proj_date != None:
            self.proj_date = wx.DateTime.FromDMY(parsed_proj_date["day"], parsed_proj_date["month"] - 1, parsed_proj_date["year"])
            self.proj_year = parsed_proj_date["year"]
            self.proj_month = parsed_proj_date["month"]
            self.proj_day = parsed_proj_date["day"]
            print("Projected date %s, parse: Month: %02d, Day: %02d, Year: %04d" %
                  (self.proj_date.Format(date_format), self.proj_month, self.proj_day, self.proj_year))
            Date.set_proj_date(self, in_date)
            paydates = self.process_paydates_in_range(Date.get_global_curr_date(self), parsed_proj_date)
#            print("Pay dates in range %s-%s: %s" % (Date.get_global_curr_date(self)["str"], in_date, paydates))
            billsdue = self.process_bills_sched_in_range(Date.get_global_curr_date(self), parsed_proj_date)
#            print("Bills sched in range %s-%s: %s" % (Date.get_global_curr_date(self)["str"], in_date, BillList(billsdue)))
            self.assets.update_proj_values(in_date)
            self.redraw_all()
        else:
            self.proj_date = None
            self.DisplayMsg("Bad projected date ignored: %s" % (in_date))

    def make_asset_grid(self, panel):
        self.assetGrid = AssetGrid(panel)
        self.needed_width = self.assetGrid.set_properties(self)

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
        if self.assets == None:
            return
        nassets = len(self.assets.assets)
        if index == -1:
            start_range = 0
            end_range = nassets
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
            self.assetGrid.SetGridCursor(0, 0)
            self.assetGrid.MakeCellVisible(0, True)
        elif index > 0:
            self.assetGrid.SetGridCursor(index, 0)
            self.assetGrid.MakeCellVisible(index, True)

    def addTransactionFrame(self, row, autoCreate=True):
        retVal = None
        name = self.assets.assets[row].name
        transactions = self.assets[row].transactions
        if autoCreate:
            retVal = self.assets.assets[row].trans_frame = TransactionFrame(None, self, -1, row, transactions, name)
        return retVal

    def getTransactionFrame(self, row, autoCreate = True):
        try:
            trans_frame = self.assets.assets[row].trans_frame
        except:
            trans_frame = None
        if trans_frame == None:
            if autoCreate:
                return self.addTransactionFrame(row, autoCreate)
        return trans_frame

    def removeTransactionFrame(self, row):
        self.assets.assets[row].trans_frame.Destroy()
        self.assets.assets[row].trans_frame = None

    def update_asset_dates(self, oldDateFormat, newDateFormat):
        if self.assets == None:
            return
        self.edited = True
        nassets = len(self.assets)
        for row in range(nassets):
            curr_asset = self.assets.assets[row]
            last_pull_date = curr_asset.get_last_pull_date()
            if last_pull_date != None:
                curr_asset.set_last_pull_date(Date.convertDateTimeFormat(Date, last_pull_date, oldDateFormat, newDateFormat))
            due_date = curr_asset.get_due_date()
            if due_date != None:
                curr_asset.set_due_date(Date.convertDateFormat(Date, due_date, oldDateFormat, newDateFormat))
            sched_date = curr_asset.get_sched_date()
            if sched_date != None:
                curr_asset.set_sched_date(Date.convertDateFormat(Date, sched_date, oldDateFormat, newDateFormat))
            if self.assets.assets[row].transactions != None:
                self.assets.assets[row].transactions.update_transaction_dates(oldDateFormat, newDateFormat)
                tframe = self.getTransactionFrame(row, False)
                if tframe != None:
                    tframe.redraw_all()

    def update_bill_dates(self, oldDateFormat, newDateFormat):
        if self.bills != None:
            self.edited = True
            nbills = len(self.bills)
            for row in range(nbills):
                curr_bill = self.bills[row]
                due_date = curr_bill.get_due_date()
                if due_date != None:
                    curr_bill.set_due_date(Date.convertDateFormat(Date, due_date, oldDateFormat, newDateFormat))
                sched_date = curr_bill.get_sched_date()
                if sched_date != None:
                    curr_bill.set_sched_date(Date.convertDateFormat(Date, sched_date, oldDateFormat, newDateFormat))
            if self.bills_frame != None:
                self.bills_frame.redraw_all()

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
        self.update_asset_dates(oldDateFormat, newDateFormat)
        self.update_bill_dates(oldDateFormat, newDateFormat)
        self.update_date_dates(oldDateFormat, newDateFormat)
        self.redraw_all()
        self.edited = True

    def load_file(self, *args):
        assetFile = copy.deepcopy(self.assetFile)
        latest_assets = qif.load_file(self, assetFile)
        if latest_assets != None:
            self.process_asset_list(latest_assets, 'add')
            self.assets.update_proj_values(Date.get_proj_date(Date))
        self.redraw_all()

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
        if assetFile != "" and len(self.assets.assets) != 0:
            file = open(assetFile, 'w')                             # Make sure file starts empty! JJG 1/17/2024
            file.close()
            lines = ["!Account"]
            self.process_asset_list(self.assets, "writeAccountsToQIF", lines)

    def save_as_file(self, *args):
        self.assetFile = ""                                         # JJG 6/24/2024 Force a file path to be selected
        self.save_file(self)

    def close(self, *args):
        if self.edited:
            d = wx.MessageDialog(self,
                                 "",
                                 "Update file before closing?", wx.YES_NO)
            if d.ShowModal() == wx.ID_YES:
                self.save_file(self)
        self.process_asset_list(self, 'delete')
        self.cur_asset = None
        for cur_asset in self.assets.assets:
            trans_frame = getTransactionFrame(cur_asset[self.asset_index],False)
            if trans_frame != None:
                trans_frame.close()
            del cur_asset
        del self.assets
        del self.bills
        self.assets = AssetList(self)
        self.bills = None
        self.edited = False
        self.SetTitle("PyAsset: Asset")
        self.fileMenuItem["Open"].Enable(True)
        self.fileMenuItem["ImportCSV"].Enable(True)
        self.fileMenuItem["ImportXLSX"].Enable(True)
        self.fileMenuItem["Save"].Enable(False)
        self.fileMenuItem["SaveAs"].Enable(False)
        self.fileMenuItem["Close"].Enable(False)
        self.fileMenuItem["Export"].Enable(False)
        self.fileMenuItem["Archive"].Enable(False)
        self.assetFile = ""
        return

    def quit(self, *args):
        self.close()
        self.Close()

    def write_file(self, date_, amount_, memo_, payee_, filelocation_):
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

    def read_csv(self, inf_, outf_, deff_):  # will need to receive input csv and def file
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

    def process_asset_list(self, assetList, function, lines = None):
        if lines != None:
            with open(self.assetFile, 'a') as file:
                fileLines = '\n'.join(lines)
                file.writelines("%s" % fileLines)
                file.write('\n')
        nassets = len(assetList.assets)
        if nassets > 0:
            for i in range(nassets):
                if function == 'writeAccountsToQIF':
                    qif.write_qif(self, self.assetFile, "writeAccountHeader", assetList.assets[i])
                    qif.write_qif(self, self.assetFile, "writeAccountDetail", assetList.assets[i])
                elif function == 'add':
                    cur_asset = assetList.assets[i]
                    cur_name = cur_asset.get_name()
                    j = self.assets.index(cur_name)
                    if j != -1:
                        self.assets.assets[j] = cur_asset           # For now, just replace, when dates are working, save later date JJG 1/22/2022
                    else:            
                        self.assets.append_by_object(cur_asset)
                elif function == 'delete':
                    try:
                        transFrame = assetList.assets.assets[0].trans_frame
                    except:
                        transFrame = None
                    if transFrame != None:
                        transFrame.Destroy()
                    del assetList.assets[0]                         # Since we are deleting the entire list, we can just delete the first one each time!
                else:
                    pass                                            # JJG 1/26/24  TODO add code to print error if unknown function parameter passed to process_asset_list
            if function == 'delete':
                    self.assetGrid.ClearGrid()
        if function != 'add':
            self.redraw_all()

    def process_XLSX_file(self, total_filename):
        self.cur_assets = None
        xlsm = ExcelToAsset(self, ignore_sheets=['Assets', 'Bills'])
        xlsm.OpenXLSMFile(total_filename)
        latest_assets = xlsm.ProcessAssetsSheet(self)
        self.process_asset_list(latest_assets, 'add')
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
        self.bills = xlsm.ProcessBillsSheet(self.bills)
        return latest_assets

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
                latest_assets = self.process_XLSX_file(total_name_in)
                if latest_assets != None:
                    self.redraw_all()
            else:
                self.DisplayMsg(error)

    def update_from_net(self, *args):
        w = iMacrosToAsset()
        w.Init()
        net_asset_codes = [
                           ("HFCU",1,[False,False,False,True], "Hickam "),
                           #("NFCU",-1,[False,True], "Navy Fed "),
                           #("SOFI",-1.[False,True], "SoFi "),
                           #("AMEX",-1,[True,True], "Am Ex Blue "),
                           #("CITI",-1,[True], "Citi MC "),
                           #("SYW",-1,[True], "Shop Your Way MC "),
                           #("TSP",-1,[False,False,False,True], "TSP "),
                           #("MET",1,[False], "Met Life annuity ")
                           ]
        for net_asset_code in net_asset_codes:
            latest_assets = w.GetNetInfo(net_asset_code)
            #print latest_assets
            for i in range(len(latest_assets)):
                net_asset = latest_assets.__getitem__(i)
                if net_asset != None:
                    latest_name = net_asset_code[3] + net_asset.get_name()
                    found = False
                    for j in range(len(self.assets)):
                        cur_name = self.assets[j].get_name()
                        if "(" in cur_name:
                            cur_name = cur_name.split("(")[1].split(")")[0]
                        if latest_name in cur_name:
                            net_index = j
                            found = True
                            break
                    if not found:
                        self.assets.append_by_name(latest_name)
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

    def setDateFormat(self, new_DateFormat):
        self.dateFormat = new_DateFormat

    def setPayType(self, new_type):
        self.payType = new_type

    def setRefDate(self, new_ref_date):
        if type(new_ref_date) is str:
            new_ref_date = Date.parse_date(Date, new_ref_date, Date.get_global_date_format(Date))
            new_ref_date_str = wx.DateTime.FromDMY(new_ref_date['day'], new_ref_date['month'], new_ref_date['year'])
            new_ref_date["str"] = new_ref_date_str.Format(Date.get_date_format(Date))
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
        d = wx.FileDialog(self, "Save", "", "", "*.txt", wx.FD_OPEN)
        if d.ShowModal() == wx.ID_OK:
            fname = d.GetFilename()
            dir = d.GetDirectory()
            self.cur_asset.write_txt(os.path.join(dir, fname))

    def archive(self, *args):
        d = wx.TextEntryDialog(self,
                               "Archive transactions before what date?",
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
        index = self.assetGrid.GetGridCursorRow()
        nassets = len(self.assets)
        new_asset = self.assets.append_by_name("")
        self.assetGrid.AppendRows()
        for i in range(nassets, index, -1):
            self.assets[i] = self.assets[i-1]
        self.assets[index] = new_asset
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
                self.assetGrid.DeleteRows()
            self.redraw_all()  # TODO: Can we make a self.redraw(index-1)  so that only the assets[index-1:] get updated?  JJG 07/09/2021

    def about(self, *args):
        d = wx.MessageDialog(self,
                             "Python Asset Manager\n"
                             "Copyright (c) 2016-2025 Joseph J. Gorak\n"
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