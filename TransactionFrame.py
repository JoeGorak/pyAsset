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
#  06/25/2016     Initial version v0.1
#  08/07/2021     Version v0.2

# To Do list:
# Speed redraw_all: break into redraw_all, redraw_range, redraw_totals
# Save a backup version of files
# Read and save CBB files?
# Undo?
# Plot balance vs day
# Search functions
# goto date

import wx
import wx.grid as gridlib
import csv
import os
from qif import qif
from Asset import Asset
from Date import Date
from HelpDialog import HelpDialog
from Transaction import Transaction
from TransactionList import TransactionList
from TransactionGrid import TransactionGrid

class TransactionFrame(wx.Frame):
    def __init__(self, parent, asset_index, transactions, title="PyAsset:Transaction", filename=None, **kwds):
        self.asset_index = asset_index
        self.transactions = transactions
        self.parent = parent
        self.filename = filename

        if len(self.transactions) > 0:
            self.cur_transaction = self.transactions[0]
        else:
            self.cur_transaction = None

        super(TransactionFrame, self).__init__(parent, title=title)
        self.make_widgets()

        self.Bind(wx.EVT_CLOSE,self.close)
        self.edited = False

        if filename:
            self.cur_transaction.read_qif(filename)

        self.SetTitle("PyAsset:Transactions for %s" % title)
        self.title = title
        self.redraw_all()

    def getTransactions(self):
        return self.transactions.transactions

    def getTitle(self):
        return self.title

    def make_widgets(self):
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)
        self.make_filemenu()
        self.make_editmenu()
        self.make_helpmenu()
        self.do_layout()

    def make_filemenu(self):
        self.filemenu = wx.Menu()
        self.ID_IMPORT_CSV = wx.NewId()
        self.ID_IMPORT_XLSX = wx.NewId()
        self.ID_EXPORT_TEXT = wx.NewId()
        self.ID_ARCHIVE = wx.NewId()
        self.filemenu.Append(wx.ID_OPEN, "Open\tCtrl-o",
                             "Open a new transction file", wx.ITEM_NORMAL)
        self.filemenu.Append(wx.ID_SAVE, "Save\tCtrl-s",
                             "Save the current transactions in the same file", wx.ITEM_NORMAL)
        self.filemenu.Append(wx.ID_SAVEAS, "Save As",
                             "Save the current transactions under a different name", wx.ITEM_NORMAL)
        self.filemenu.Append(self.ID_IMPORT_CSV, "Import CSV\tCtrl-c",
                             "Import transactions from a CSV file",
                             wx.ITEM_NORMAL)
        self.filemenu.Append(self.ID_IMPORT_XLSX, "Import XLSX\tCtrl-X",
                             "Import transactions from an EXCEL file",
                             wx.ITEM_NORMAL)
        self.filemenu.Append(self.ID_EXPORT_TEXT, "Export Text",
                             "Export the current transaction register as a text file",
                             wx.ITEM_NORMAL)
        self.filemenu.Append(self.ID_ARCHIVE, "Archive",
                             "Archive transactions older than a specified date",
                             wx.ITEM_NORMAL)
        self.filemenu.Append(wx.ID_CLOSE, "Close\tCtrl-w",
                             "Close the current file", wx.ITEM_NORMAL)
        self.filemenu.Append(wx.ID_EXIT, "Exit\tCtrl-q",
                             "Exit PyAsset", wx.ITEM_NORMAL)
        self.menubar.Append(self.filemenu, "&File")
        self.Bind(wx.EVT_MENU, self.load_file, None, wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.save_file, None, wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.save_as_file, None, wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.import_CSV_file, None, self.ID_IMPORT_CSV)
        #self.Bind(wx.EVT_MENU, self.export_text, None, self.ID_EXPORT_TEXT)
        self.Bind(wx.EVT_MENU, self.archive, None, self.ID_ARCHIVE)
        self.Bind(wx.EVT_MENU, self.close, None, wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.quit, None, wx.ID_EXIT)

    def make_editmenu(self):
        self.ID_SORT = wx.NewId()
        self.ID_MARK_ENTRY = wx.NewId()
        self.ID_VOID_ENTRY = wx.NewId()
        self.ID_DELETE_ENTRY = wx.NewId()
        self.ID_RECONCILE = wx.NewId()
        self.editmenu = wx.Menu()
        self.editmenu.Append(wx.ID_NEW, "New Entry\tCtrl-n",
                             "Create a new transaction in the register",
                             wx.ITEM_NORMAL)
        self.editmenu.Append(self.ID_SORT, "Sort Entries",
                             "Sort entries", wx.ITEM_NORMAL)
        self.editmenu.Append(self.ID_MARK_ENTRY, "Mark Cleared\tCtrl-m",
                             "Mark the current transaction cleared",
                             wx.ITEM_NORMAL)
        self.editmenu.Append(self.ID_VOID_ENTRY, "Void Entry\tCtrl-v",
                             "", wx.ITEM_NORMAL)
        self.editmenu.Append(self.ID_DELETE_ENTRY, "Delete Entry",
                             "Delete the current transaction", wx.ITEM_NORMAL)
        self.editmenu.Append(self.ID_RECONCILE, "Reconcile\tCtrl-r",
                             "Reconcile your Asset", wx.ITEM_NORMAL)
        self.menubar.Append(self.editmenu, "&Edit")
        self.Bind(wx.EVT_MENU, self.newentry, None, wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.sort, None, self.ID_SORT)
        self.Bind(wx.EVT_MENU, self.markcleared, None, self.ID_MARK_ENTRY)
        self.Bind(wx.EVT_MENU, self.voidentry, None, self.ID_VOID_ENTRY)
        self.Bind(wx.EVT_MENU, self.deleteentry, None, self.ID_DELETE_ENTRY)
        self.Bind(wx.EVT_MENU, self.reconcile, None, self.ID_RECONCILE)
        return

    def make_helpmenu(self):
        self.ID_HELP = wx.NewId()
        self.helpmenu = wx.Menu()
        self.helpmenu.Append(wx.ID_ABOUT, "About",
                             "About PyAsset", wx.ITEM_NORMAL)
        self.helpmenu.Append(self.ID_HELP, "Help\tCtrl-h",
                             "PyAsset Help", wx.ITEM_NORMAL)

        self.menubar.Append(self.helpmenu, "&Help")
        self.Bind(wx.EVT_MENU, self.about, None, wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.gethelp, None,self. ID_HELP)

    def make_trans_grid(self, panel):
        self.trans_grid = TransactionGrid(self, panel, self.transactions)
        return self.trans_grid

    def get_trans_grid(self):
        try:
            trans_grid = self.trans_grid
        except:
            trans_grid = self.make_trans_grid(self.panel)
        self.trans_grid = trans_grid
        return self.trans_grid

    def do_layout(self):
        self.panel = wx.Panel(self)

        self.make_trans_grid(self.panel)
        self.trans_grid.set_properties(self)

        self.grid_sizer = wx.FlexGridSizer(1, self.trans_grid.getNumLayoutCols(), 0, 0)
        self.grid_sizer.Add(self.trans_grid, proportion=1, flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.EXPAND)

        self.panel.Fit()
        self.panel.SetSizer(self.grid_sizer)
        self.grid_sizer.SetSizeHints(self.panel)

        self.Fit()
        self.Layout()
        self.Show()

    def update_transaction_grid_dates(self, oldDateFormat, newDateFormat):
        self.edited = True
        ntransactions = len(self.transactions)
        for row in range(ntransactions):           
            for col in range(self.trans_grid.getNumLayoutCols()):
                cellValue = self.trans_grid.GridCellDefaultRenderer(row, col)
                if cellValue != None and cellValue != 'None':
                    cellType = self.trans_grid.getColType(col)
                    if cellType == self.trans_grid.DATE_TYPE and oldDateFormat != None and newDateFormat != None:
                        tableValue = Date.convertDateFormat(Date, cellValue, oldDateFormat, newDateFormat)["str"]
                        if tableValue != "":
                            curr_trans = self.trans_grid.getCurrTrans(row, col)
                            curr_trans.setDateFormat(newDateFormat)
                            if self.trans_grid.setColMethod(row, col, tableValue) != "??":
                                self.trans_grid.GridCellDateRenderer(row, col)
                                self.trans_grid.Refresh()
                            else:
                                print("update_transaction_grid_dates: Warning: unknown method for cell! row, ", row, " col ", col, " Skipping!")

    def DisplayMsg(self, str):
        d = wx.MessageDialog(self, str, "Error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()
        return wx.CANCEL

    def redraw_all(self, index=None):
        if index == None:
            index = -1
        ntransactions = len(self.transactions)
        start_range = 0
        end_range = ntransactions
        if index == -1:
            trans_grid = self.get_trans_grid()
        else:
            start_range = index
            end_range = start_range + 1

        # JJG 7/12/2025 Make sure current window is big enough and increase size if not!
        trans_grid = self.get_trans_grid()
        if trans_grid.GetNumberRows() < ntransactions:
            trans_grid.InsertRows(pos=ntransactions-1, numRows=ntransactions-trans_grid.GetNumberRows()+6)

        # Make sure current balances are corrent from the starting range for the rest of the transactions!
        proj_value = self.transactions.update_current_and_projected_values(start_range)
        self.transactions.parent.set_value_proj(proj_value)

        self.transactions.sort()

        # Display the transactions
        for row in range(start_range, end_range):
            for col in range(self.trans_grid.getNumLayoutCols()):
                ret_val = wx.OK
                if row < 0 or row >= ntransactions:
                    str = "Warning: skipping redraw on bad cell %d %d!" % (row, col)
                    ret_val = self.DisplayMsg(str)
                if ret_val != wx.OK:
                    continue

                cellType = self.trans_grid.getColType(col)
                if cellType == self.trans_grid.DOLLAR_TYPE:
                    self.trans_grid.GridCellDollarRenderer(row, col)
                elif cellType == self.trans_grid.RATE_TYPE:
                    self.trans_grid.GridCellPercentRenderer(row, col)
                elif cellType == self.trans_grid.DATE_TYPE:
                    self.trans_grid.GridCellDateRenderer(row, col)
                elif cellType == self.trans_grid.DATE_TIME_TYPE:
                    self.trans_grid.GridCellDateTimeRenderer(row, col)
                elif cellType == self.trans_grid.STRING_TYPE:
                    self.trans_grid.GridCellStringRenderer(row, col)
                else:
                    self.trans_grid.GridCellErrorRenderer(row, col)

        self.Show()

        cursorCell = index
        if index == -1:
            if ntransactions > 0:
                cursorCell = ntransactions - 1
            else:
                cursorCell = 0
        else:
            if index > ntransactions:
                cursorCell = ntransactions - 1
            else:
                cursorCell = index
        self.trans_grid.SetGridCursor(cursorCell, 0)
        self.trans_grid.MakeCellVisible(cursorCell, True)

    def cellchange(self, evt):
        doredraw = 0
        row = evt.GetRow()
        col = evt.GetCol()
        if row < 0: return
        if row >= len(self.cur_transaction):
            print("Warning: modifying incorrect cell!")
            return
        self.edited = True
        transaction = self.cur_transaction[row]
        val = self.cbgrid.GetCellValue(row, col)
        if col == 0:
            transaction.setdate(val)
        elif col == 1:
            transaction.setnumber(val)
        elif col == 2:
            transaction.setpayee(val)
        elif col == 3:
            if val:
                transaction.set_state("cleared")
        elif col == 4:
            transaction.setmemo(val)
        elif col == 5:
            doredraw = 1
            transaction.setamount(val)
        else:
            print("Warning: modifying incorrect cell!")
            return
        if doredraw: self.redraw_all(row)  # only redraw [row:]
        return

    def load_file(self, *args):
        self.close()
        self.cur_transaction = Transaction()
        self.edited = False
        d = wx.FileDialog(self, "Open", "", "", "*.qif", wx.OPEN)
        if d.ShowModal() == wx.ID_OK:
            fname = d.GetFilename()
            dir = d.GetDirectory()
            self.cur_transaction.read_qif(os.path.join(dir, fname))
            self.redraw_all(-1)
        if self.cur_transaction.name: self.SetTitle("PyAsset: %s" % self.cur_transaction.name)
        return

    def save_file(self, *args):
        filename = self.filename
        for cur_transaction in self.transactions:
            if filename != None or filename != "":
                if not self.save_as_file():
                    break
            else:
                qif.write_qif(self, filename)
        self.edited = False
        return

    def save_as_file(self, *args):
        ret_val = True
        d = wx.FileDialog(self, "Save", "", "", "*.qif", wx.FD_OPEN)
        if d.ShowModal() == wx.ID_OK:
            fname = d.GetFilename()
            dir = d.GetDirectory()
            qif.write_qif(self,os.path.join(dir, fname))
        else:
            ret_val = False
        return ret_val

    def process_transaction_list(self, function, transactionList):
        ntransactions = len(transactionList.transactions)
        if ntransactions > 0:
            if function == 'writeAccountHeaders' or function == 'writeAccountDetails':
               qif.write_qif(self, self.filename, function, lines)
            else:
                for i in range(ntransactions):
                    if function == 'add':
                        cur_asset = transactionList.transactions[i]
                        cur_name = cur_asset.get_payee()
                        j = self.transactions.index(cur_name)
                        if j != -1:
                            self.transactioons[j] = cur_asset           # For now, just replace, when dates are working, save later date JJG 1/22/2022
                        else:            
                          self.transactions.append_by_object(cur_asset)
                    elif function == 'delete':
                        del transactionList.transactions[0]             # Since we are deleting the entire list, we can just delete the first one each time!
                    elif function == 'print':
                        print(transactionList.transactions[i])
                    else:
                        pass                                            # JJG 1/26/24  TODO add code to print error if unknown function parameter passed to process_asset_list
                if function == 'delete':
                    self.trans_grid.ClearGrid()
                    del self.trans_grid
                    self.trans_grid = None
        self.redraw_all()

    def close(self, event):
        if self.edited:
            d = wx.MessageDialog(self, 'Save file before closing?', 'Question',
                                 wx.YES_NO)
            if d.ShowModal() == wx.ID_YES:
                self.save_file()
        self.edited = False
        self.get_trans_grid().close()
#        del self.trans_grid
        del self.panel
        trans_frame = self.parent.getTransactionFrame(self.asset_index, False)
        if trans_frame != None:
            self.parent.removeTransactionFrame(self.asset_index)
        return

    def quit(self, event):
        self.close(event)
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
        next(csvdeff, None)

        for settings in csvdeff:
            date_ = int(settings[0])  # convert to int
            amount_ = int(settings[2])  # How much was the transaction
            memo_ = int(settings[3])  # discription of the transaction
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
                self.cur_transaction.read_qif(total_name_qif)
                fromfile.close()
                deffile.close()
                self.redraw_all(-1)

                if self.cur_transaction.name:
                    title = "PyAsset: %s" % self.cur_transaction.name
                else:
                    title = "Pyasset"
                self.SetTitle(title)

            else:
                d = wx.MessageDialog(self, error, wx.OK | wx.ICON_INFORMATION)
                d.ShowModal()
                d.Destroy()

    def export_text(self, *args):
        d = wx.FileDialog(self, "Save", "", "", "*.txt", wx.SAVE)
        if d.ShowModal() == wx.ID_OK:
            fname = d.GetFilename()
            dir = d.GetDirectory()
            self.cur_transaction.write_txt(os.path.join(dir, fname))
        return

    def archive(self, *args):
        d = wx.TextEntryDialog(self,
                               "Archive transactions before what date?",
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
        newcb_starttransaction.state = "cleared"
        newcb_starttransaction.date = date

        newcb = Asset()
        newcb.filename = self.cur_transaction.filename
        newcb.name = self.cur_transaction.name
        newcb.append(newcb_starttransaction)
        archtot = 0

        for transaction in self.cur_transaction:
            if transaction.date < date and transaction.state == "cleared":
                archive.append(transaction)
                archtot += transaction.amount
            else:
                newcb.append(transaction)
        newcb_starttransaction.amount = archtot
        self.cur_transaction = newcb
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
        index = self.trans_grid.GetGridCursorRow()
        ntransactions = len(self.transactions)
        new_transaction = self.transactions.append(Transaction(self))
        self.trans_grid.AppendRows()
        for i in range(ntransactions, index, -1):
            self.transactions[i] = self.transactions[i-1]
        self.transactions[index] = new_transaction
        self.trans_grid.SetGridCursor(index, 0)
        self.trans_grid.MakeCellVisible(index, 1)
        self.redraw_all(-1)

    def sort(self, *args):
        self.edited = True
        self.transactions.sort()
        self.redraw_all(-1)

    def voidLabelUpdate(self, index):
        transaction = self.transactions[index]
        void_id = self.editmenu.FindItemById(self.ID_VOID_ENTRY).Id
        if transaction.get_payee()[:6] == "VOID: ":
            new_label = "Unvoid Entry\tCtrl-v"
        else:
            new_label = "Void Entry\tCtrl-v"
        self.editmenu.SetLabel(void_id, new_label)

    def voidentry(self, *args):
        index = self.trans_grid.GetGridCursorRow()
        if index < 0:
            errorMsg = "index out of bounds in void - %d: ignored" % (index)
            self.DisplayMsg(errorMsg)
        else:
            transaction = self.transactions[index]
            if transaction.get_state() != "void":
                msg = "Really void this entry?"
                title = "Really void?"
                void = True
            else:
                msg = "Really unvoid this entry?"
                title = "Really unvoid?"
                void = False
            d = wx.MessageDialog(self,
                                 msg,
                                 title, wx.YES_NO)
            if d.ShowModal() == wx.ID_YES:
                self.edited = True
                today_date = Date.get_curr_date(self.parent)
                # Get payee and date of transaction for later use
                original_payee = transaction.get_payee()
                original_date = transaction.get_due_date()
                # Toggle values so if it was void make it active and if active make it void
                if void:
                    transaction.set_payee("VOID:" + transaction.get_payee())
                    transaction.set_memo("voided %s" % today_date["str"])
                    transaction.set_prev_state(transaction.get_state())
                    transaction.set_state("void")
                    new_label = "Unvoid Entry\tCtrl-v"
                else:
                    new_payee = transaction.get_payee()[5:]
                    transaction.set_payee(new_payee)
                    transaction.set_memo("")
                    new_state = transaction.get_prev_state()
                    transaction.set_state(new_state)
                    new_label = "Void Entry\tCtrl-v"
                void_id = self.editmenu.FindItemById(self.ID_VOID_ENTRY).Id
                self.editmenu.SetLabel(void_id, new_label)
                proj_value = self.transactions.update_current_and_projected_values(0)
                self.update_asset_projected_value(index)
                # TODO: If we voided or unvoided a payment or paydown, we need to void or unvoid the corresponding payment or paydown
                if self.starts_with(original_payee, "Payment") or self.starts_with(original_payee, "VOID:Payment"):
                    pass
                elif self.starts_with(original_payee, "Paydown") or self.starts_with(original_payee, "VOID:Paydown"):
                    pass

    def starts_with(self, string, substring):
        return string[:len(substring)] == substring

    def update_asset_projected_value(self, index=0):
        assets = self.parent.getAssets()
        new_value = assets[0].get_value_proj()
        asset_value_proj = new_value
        proj_index = 0
        proj_date = Date.get_global_proj_date(self)["dt"]
        for i in range(index,len(self.transactions)):
            self.trans_grid.setValue(i, "Value", str(round(self.transactions[i].get_current_value(),2)))
            new_value = self.transactions[i].get_current_value()
            if self.transactions[i].get_due_date() == None:
                continue
            due_date = self.transactions[i].get_due_date()["dt"]
            if due_date <= proj_date:
                asset_value_proj= new_value
                proj_index = i
        assets[self.asset_index].set_value_proj(asset_value_proj)
        self.parent.redraw_all()
        self.redraw_all()  # redraw only [index:]

    def deleteentry(self, *args):
        index = self.trans_grid.GetGridCursorRow()
        if index < 0:
            errorMsg = "index out of bounds in deleteentry - %d: ignored" % (index)
            self.DisplayMsg(errorMsg)
        else:
            d = wx.MessageDialog(self,
                                 "Really delete this transaction?",
                                 "Really delete?", wx.YES_NO)
            if d.ShowModal() == wx.ID_YES:
                trans_grid = self.get_trans_grid()
                transactions = trans_grid.frame.transactions.getTransactions
                payee = trans_grid.GetCellValue(index, trans_grid.TRANS_PAYEE_COL)
                due_date = trans_grid.GetCellValue(index, trans_grid.TRANS_DUE_DATE_COL)
                trans_list_index = self.transactions.index(payee, due_date)
                del self.transactions[trans_list_index]
                self.trans_grid.DeleteRows(pos=index)
                value_proj = self.transactions.update_current_and_projected_values()
                self.update_asset_projected_value()
 
    def reconcile(self, *args):
        d = wx.TextEntryDialog(self,
                               "What is the balance of your last statement?",
                               "Current Balance")
        if d.ShowModal() == wx.ID_OK:
            current_balance = float(d.GetValue())
        else:
            current_balance = None
        d.Destroy()
        if not current_balance: return

        _balance = self.get_celared_balance()
        difference = current_balance - cleared_balance
        if abs(difference) < 0.01:
            d = wx.MessageDialog(self,
                                 "Your Asset balances",
                                 "Balanced", wx.OK)
            d.ShowModal()
            d.Destroy()
        else:
            d = wx.MessageDialog(self,
                                 "Your Asset balance differs by "
                                 "$%.2f. Adjust balance?" % difference,
                                 "Adjust balance?", wx.YES_NO)
            if d.ShowModal() == wx.ID_YES:
                self.adjust_balance(difference)
            d.Destroy()
        return

    def adjust_balance(self, diff):
        self.edited = True
        transaction = Transaction(payee = "Balance Adjustment", amount = diff, state = "cleared", memo = "Adjustment")
        transactions = self.transactions.append(transaction)
        self.redraw_all(-1)  # only redraw [-1]?
        return

    def get_cleared_balance(self):
        value = 0.0
        for transaction in self.cur_transaction:
            if transaction.get_state() == "cleared":
                value = value + transaction.amount
        return value

    def about(self, *args):
        d = wx.MessageDialog(self,
                             "Python Asset Manager\n"
                             "Copyright (c) 2016-2025 Joseph J. Gorak\n"
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

    def markcleared(self, *args):
        index = self.trans_grid.GetGridCursorRow()
        if index < 0:
            errorMsg = "index out of bounds in markcleared - %d: ignored" % (index)
            self.DisplayMsg(errorMsg)
        else:
            self.edited = True
            prev_state = self.transactions[index].get_prev_state()
            cur_state = self.transactions[index].get_state()
            self.transactions[index].set_prev_state(cur_state)
            if cur_state == "cleared":
                self.transactions[index].set_state(cur_state)
                self.trans_grid.setValue(index, "State", cur_state)
            else:
                self.transactions[index].set_state(prev_state)
                self.trans_grid.setValue(index, "State", prev_state)
        return

    def assetchange(self, which_transaction, which_column, new_value):
        if type(which_column) is int:
            colName = self.trans_grid.getColName(which_column)
        else:
            colName = which_column
        transaction_changed = self.transactions[which_transaction]
        payee = transaction_changed.get_payee()
        modified = True
        print("TransactionFrame: Recieved notification that transaction ", payee, " column", colName, "changed, new_value", new_value)
        print("Transaction changed: ", transaction_changed)

        modified_transaction_index = -1
        if self.starts_with(payee, "Payment") or self.starts_with(payee, "VOID:Payment"):
            if self.starts_with(payee, "Payment"):
                payment_account = payee[len("Payment from "):]
            else:
                payment_account = payee[len("VOID:Payment from ")]
            asset_index = self.parent.assets.index(payment_account)
            modified_asset = self.parent.getAssets()[asset_index]
            modified_payee = "Paydown " + self.title + " from " + payment_account
        elif self.starts_with(payee, "Paydown") or self.starts_with(payee, "VOID:Paydown"):
            from_place = payee.index("from ")
            if self.starts_with(payee, "Paydown"):
                paydown_place = len("Paydown ")
            else:
                paydown_place = len("VOID:Paydown ")
            payment_account = payee[from_place+len("from "):]
            modified_asset_name = payee[paydown_place:from_place-1]
            modified_asset = self.parent.assets.get_asset_by_name(modified_asset_name)
            modified_payee = "Payment from " + payment_account
        modified_transactions = modified_asset.transactions
        modified_transaction_index = modified_transactions.index(modified_payee, transaction_changed.get_due_date()["str"])

        if colName == "Pmt Method":
            transaction_changed.set_pmt_method(new_value)
            if modified_transaction_index != -1:
               modified_transactions[modified_transaction_index].set_pmt_method(new_value)
        elif colName == "Chk #":
            transaction_changed.set_check_num(new_value)
            if modified_transaction_index != -1:
               modified_transactions[modified_transaction_index].set_check_num(new_value)
        elif colName == "Payee":
            transaction_changed.set_payee(new_value)
            if modified_transaction_index != -1:
               modified_transactions[modified_transaction_index].set_payee(new_value)
        elif colName == "Amount":
            transaction_changed.set_amount(new_value)
            if modified_transaction_index != -1:
               modified_transactions[modified_transaction_index].set_amount(new_value)
        elif colName == "Action":
            transaction_changed.set_action(new_value)
            if modified_transaction_index != -1:
               modified_transactions[modified_transaction_index].set_action(new_value)
        elif colName == "Value":
            transaction_changed.set_current_value(new_value)
            if modified_transaction_index != -1:
               modified_transactions[modified_transaction_index].set_current_value(new_value)
        elif colName == "Due Date":
            transaction_changed.set_due_date(new_value)
            if modified_transaction_index != -1:
               modified_transactions[modified_transaction_index].set_due_date(new_value)
        elif colName == "Sched Date":
            transaction_changed.set_sched_date(new_value)
            if modified_transaction_index != -1:
               modified_transactions[modified_transaction_index].set_sched_date(new_value)
        elif colName == "State":
            transaction_changed.set_state(new_value)
            if modified_transaction_index != -1:
               modified_transactions[modified_transaction_index].set_state(new_value)
        elif colName == "Comment":
            transaction_changed.set_comment(new_value)
            if modified_transaction_index != -1:
               modified_transactions[modified_transaction_index].set_comment(new_value)
        elif colName == "Memo":
            transaction_changed.set_memo(new_value)
            if modified_transaction_index != -1:
               modified_transactions[modified_transaction_index].set_memo(new_value)
        else:
            self.DisplayMsg("Unknown column " + colName + " ignored!")
            modified = False

        if modified == True:
            if modified_transaction_index != -1:
                self.update_asset_projected_value()
                try:
                    modified_transaction_frame = modified_asset.trans_frame
                except:
                    modified_transaction_frame = None
                if modified_transaction_frame != None:
                    modified_transaction_frame.redraw_all()
            self.redraw_all()
            self.parent.assets.update_proj_values(Date.get_global_proj_date(self))
            self.parent.redraw_all()
            self.edited = True
