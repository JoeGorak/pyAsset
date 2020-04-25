#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2016,2017,2019,2020 Joseph J. Gorak. All rights reserved.
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
from Asset import Asset
from AssetList import AssetList
from BillList import BillList
from AssetGrid import AssetGrid
from Date import Date
from TransactionFrame import TransactionFrame
from Transaction import Transaction
from HelpDialog import HelpDialog
from ExcelToAsset import ExcelToAsset
from iMacrosToAsset import iMacrosToAsset


class AssetFrame(wx.Frame):
    def __init__(self, style, parent, my_id, title="PyAsset:Asset", myfile=None, **kwds):
        self.assets = AssetList()
        self.bills = BillList()
        self.cur_asset = None
        self.edited = 0
        self.rowSize = 27
        self.colSize = 20

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

    def DisplayMsg(self, str):
        d = wx.MessageDialog(self, str, "Error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()
        return wx.CANCEL

    def make_widgets(self):
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)
        self.statusbar = self.CreateStatusBar(1, 0)
        self.make_filemenu()
        self.make_editmenu()
        self.make_helpmenu()
        self.make_asset_grid()
        self.set_properties()
        self.do_layout()

    def make_filemenu(self):
        self.filemenu = wx.Menu()
#        ID_EXPORT_TEXT = wx.NewId()
#        ID_ARCHIVE = wx.NewId()
#        ID_IMPORT_CSV = wx.NewId()
        ID_IMPORT_XLSM = wx.NewId()
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
#        self.filemenu.Append(ID_EXPORT_TEXT, "Export Text",
#                             "Export the current transaction register as a text file",
#                             wx.ITEM_NORMAL)
#        self.filemenu.Append(ID_ARCHIVE, "Archive",
#                             "Archive transactions older than a specified date",
#                             wx.ITEM_NORMAL)
        self.filemenu.AppendSeparator()
#        self.filemenu.Append(ID_IMPORT_CSV, "Import CSV\tCtrl-c",
#                             "Import transactions from a CSV file",
#                             wx.ITEM_NORMAL)
        self.filemenu.Append(ID_IMPORT_XLSM, "Import XLSM file\tCtrl-i",
                             "Import transactions from an EXCEL file with Macros",
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
#       wx.EVT_MENU(self, wx.ID_OPEN, self.load_file)
        self.Bind(wx.EVT_MENU, self.save_file, None, wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.save_as_file, None, wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.close, None, wx.ID_CLOSE)
#        self.Bind(wx.EVT_MENU, self.export_text, None, ID_EXPORT_TEXT)
#        self.Bind(wx.EVT_MENU, self.archive, None, ID_ARCHIVE)
#        self.Bind(wx.EVT_MENU, self.import_CSV_file, None, ID_IMPORT_CSV)
        self.Bind(wx.EVT_MENU, self.import_XLSM_file, None, ID_IMPORT_XLSM)
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

    def make_asset_grid(self):
        self.assetGrid = AssetGrid(self)

    def add_transaction_frame(self, row, col):
        name = self.assets[row].name
        transactions = self.assets[row].transactions
        transaction_frame = TransactionFrame(None, self, -1, transactions, name)

    def set_properties(self):
        self.total_width = self.assetGrid.set_properties(self)

    def do_layout(self):
        self.sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_1.Add(self.assetGrid, 1, wx.EXPAND, 0)
        self.SetSizer(self.sizer_1)
        self.SetAutoLayout(True)
        self.sizer_1.Fit(self)
        self.sizer_1.SetSizeHints(self)
        self.Layout()
        self.Show()

    def redraw_all(self, index=None):
        nassets = len(self.assets)
        if index == -1:
            nrows = self.assetGrid.GetNumberRows()
            if nrows > 0 and (index == None or index == -1):
                self.assetGrid.DeleteRows(0, nrows)
                nrows = 0
            start_range = 0
            end_range = nassets
            if nrows < nassets:
                rows_needed = nassets - nrows
                self.assetGrid.AppendRows(rows_needed)
        else:
            nrows = 1
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

                # Logic to always display Value (Curr), Value (Proj), Avail(Proj), Amt Over, Cash Limit, Cash Used and Cash Avail for credit cards and store cards
                asset_type = self.assets[row].get_type()
                col_name = self.assetGrid.getColName(col)
                self.assetGrid.setColZeroSuppress(row, col, True)
                if (asset_type == "store card" or asset_type == "credit card") and ("Curr" in col_name or "Proj" in col_name or "Amt" in col_name or "Cash" in col_name):
                    self.assetGrid.setColZeroSuppress(row, col, False)

#                cellValue = self.assetGrid.GridCellDefaultRenderer(row, col)
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
            self.assetGrid.SetGridCursor(nassets-1, 0)
            self.assetGrid.MakeCellVisible(nassets-1, True)
        elif index > 0:
            self.assetGrid.SetGridCursor(index, 0)
            self.assetGrid.MakeCellVisible(index, True)
        nassets = len(self.assets)
        self.SetSize(size=(self.total_width, nassets*self.rowSize))
        self.Show()

    def assetchange(self, evt):
        row = evt.GetRow()
        col = evt.GetCol()
        val = evt.String
        colName = self.assetGrid.getColName(col)
        if colName == "Acct name":
            self.assets[row].set_name(val)
        elif colName == "Curr val":
            self.assets[row].set_total(val)
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
            self.assets[row].set_sched(val)
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
        return

    def load_file(self, *args):
        self.close()
        self.cur_asset = Asset()
        self.edited = 0
        d = wx.FileDialog(self, "Open", "", "", "*.qif", wx.FD_OPEN)
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
        d = wx.FileDialog(self, "Save", "", "", "*.qif", wx.FD_SAVE)
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
        self.cur_asset = None
        nrows = self.assetGrid.GetNumberRows()
        if nrows > 0:
            self.assetGrid.DeleteRows(0, nrows)
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

    def process_asset_list(self, assetList):
        for i in range(len(assetList)):
            xlsm_asset = assetList.__getitem__(i)
            self.cur_asset = copy.deepcopy(xlsm_asset)
            cur_name = self.cur_asset.get_name()
            found = False
            for j in range(len(self.assets)):
                if self.assets[j].get_name() == cur_name:
                    self.assets[j] = copy.deepcopy(xlsm_asset)
                    found = True
                    break
            if not found:
                self.assets.append(self.cur_asset.get_name())
                self.assets[-1] = copy.deepcopy(xlsm_asset)
        self.redraw_all(-1)

    def import_XLSM_file(self, *args):
        # Appends or Merges as appropriate the records from a .xlsm file to the current Asset
        d = wx.FileDialog(self, "Import", "", "", "*.xlsm", wx.FD_OPEN)
        if d.ShowModal() == wx.ID_OK:
            self.edited = 1
            fname = d.GetFilename()
            dir = d.GetDirectory()
            total_name_in = os.path.join(dir, fname)
            error = ""
            try:
                fromfile = open(total_name_in, 'r')
            except:
                error = total_name_in + ' does not exist / cannot be opened !!\n'
            fromfile.close()

            if error == "":
                self.cur_assets = None
                xlsm = ExcelToAsset(ignore_sheets=['Assets', 'Bills', 'Shop Your Way transactions', 'Slate transactions'])
                xlsm.OpenXLSMFile(total_name_in)
                latest_assets = xlsm.ProcessAssetsSheet()
#                print(latest_assets)
                self.process_asset_list(latest_assets)
                transaction_sheet_names = xlsm.GetTransactionSheetNames()
#                print('process transaction sheets ' + str(transaction_sheet_names) + ' here')
                for sheet in transaction_sheet_names:
                    sheet_index = self.assets.index(sheet)
                    if sheet_index != -1:
                        self.assets[sheet_index].transactions = xlsm.ProcessTransactionSheet(sheet)
 #                       if len(self.assets[sheet_index].transactions) > 0:
 #                           print("latest transactions from " + sheet + " (sheet_index = " + str(sheet_index) + ")", end="")
 #                           print(str(self.assets[sheet_index].transactions))
 #                       else:
 #                           print("no transactions for " + sheet)
                    else:
                        print(sheet + " not found in  asset list")
#TODO: Process latest_bills
#                latest_bills = xlsm.ProcessBillsSheet(self.bills)
#                print(latest_bills)
                pass
            else:
                d = wx.MessageDialog(self, error, wx.OK | wx.ICON_INFORMATION)
                d.ShowModal()
                d.Destroy()

    def update_from_net(self, *args):
        w = iMacrosToAsset()
        w.Init()
        net_asset_codes = [("HFCU",1,[False,False,False,True]),
                           ("BOA",-1,[False,True]),
                           ("CITI",-1,[True]),
                           ("MACYS",-1,[True]),
                           ("SEARS",-1,[True]),
                           ("TSP",-1,[False,False,False,True]),
                           ("MET",1,[False])]
        for net_asset_code in net_asset_codes:
            latest_assets = w.GetNetInfo(net_asset_code)
    #        print latest_assets
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
                            break
                    if not found:
                        self.assets.append(latest_name)
                        net_index = -1
                    # Always update Value (Curr) column and type ... others check if non-zero value before update is done!
                    self.assets[net_index].set_total(net_asset.get_total())
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
                    if net_asset.get_due_date() != 0.0:
                        self.assets[net_index].set_due_date(net_asset.get_due_date())
                    if net_asset.get_sched() != 0.0:
                        self.assets[net_index].set_sched(net_asset.get_sched())
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
        self.redraw_all(-1)

    def properties(self, *args):
# TODO  properties
        self.DisplayMsg("properties called")

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
        self.assetGrid.AppendRows()
        nassets = self.assetGrid.GetNumberRows()
        self.assetGrid.SetGridCursor(nassets - 1, 0)
        self.assetGrid.MakeCellVisible(nassets - 1, 1)

    def sort(self, *args):
        self.edited = 1
        self.cur_asset.sort()
        self.redraw_all(-1)

    def deleteentry(self, *args):
        index = self.assetGrid.GetGridCursorRow()
        indices = self.assetGrid.SelectedCells
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
                             "Copyright (c) 2016,2017 Joseph J. Gorak\n"
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
