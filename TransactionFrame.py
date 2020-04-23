#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2016,2017,2019,2020 Joseph J. Gorak. All rights reserved.
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
#  6/25/2016     Initial version v0.1

# To Do list:
# Speed redraw_all: break into redraw_all, redraw_range, redraw_totals
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
from TransactionList import TransactionList
from Date import Date
from Transaction import Transaction


class TransactionFrame(wx.Frame):
    def __init__(self, style, parent, my_id, title="PyAsset:Transaction", myfile=None, **kwds):
        self.transactions = TransactionList()
        self.cur_transaction = None
        self.edited = 0

        if style == None:
            style = wx.DEFAULT_FRAME_STYLE
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, parent, my_id, title, **kwds)

        self.make_widgets()

        if myfile:
            self.cur_transaction.read_qif(myfile)
            self.redraw_all(-1)
            if self.cur_transaction.get_name() != None:
                self.SetTitle("PyAsset:Transaction %s" % self.cur_transaction.get_name())
        return

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
        ID_MARK_ENTRY = wx.NewId()
        ID_VOID_ENTRY = wx.NewId()
        ID_DELETE_ENTRY = wx.NewId()
        ID_RECONCILE = wx.NewId()
        self.editmenu = wx.Menu()
        self.editmenu.Append(wx.ID_NEW, "New Entry\tCtrl-n",
                             "Create a new transaction in the register",
                             wx.ITEM_NORMAL)
        self.editmenu.Append(ID_SORT, "Sort Entries",
                             "Sort entries", wx.ITEM_NORMAL)
        self.editmenu.Append(ID_MARK_ENTRY, "Mark Cleared\tCtrl-m",
                             "Mark the current transaction cleared",
                             wx.ITEM_NORMAL)
        self.editmenu.Append(ID_VOID_ENTRY, "Void Entry\tCtrl-v",
                             "", wx.ITEM_NORMAL)
        self.editmenu.Append(ID_DELETE_ENTRY, "Delete Entry",
                             "Delete the current transaction", wx.ITEM_NORMAL)
        self.editmenu.Append(ID_RECONCILE, "Reconcile\tCtrl-r",
                             "Reconcile your Asset", wx.ITEM_NORMAL)
        self.menubar.Append(self.editmenu, "&Edit")
        wx.EVT_MENU(self, wx.ID_NEW, self.newentry)
        wx.EVT_MENU(self, ID_SORT, self.sort)
        wx.EVT_MENU(self, ID_MARK_ENTRY, self.markcleared)
        wx.EVT_MENU(self, ID_VOID_ENTRY, self.voidentry)
        wx.EVT_MENU(self, ID_DELETE_ENTRY, self.deleteentry)
        wx.EVT_MENU(self, ID_RECONCILE, self.reconcile)
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
        self.SetTitle("PyAsset")
        self.statusbar.SetStatusWidths([-1])
        statusbar_fields = [""]
        for i in range(len(statusbar_fields)):
            self.statusbar.SetStatusText(statusbar_fields[i], i)
        self.cbgrid.CreateGrid(0, 7)
        self.cbgrid.SetRowLabelSize(40)
        self.cbgrid.SetColLabelSize(20)
        self.cbgrid.SetColLabelValue(0, "Date")
        self.cbgrid.SetColSize(0, 60)
        self.cbgrid.SetColLabelValue(1, "Number")
        self.cbgrid.SetColSize(1, 150)               # was 50 JJG
        self.cbgrid.SetColLabelValue(2, "Payee")
        self.cbgrid.SetColSize(2, 500)              # was 150  JJG
        self.cbgrid.SetColLabelValue(3, "X")
        self.cbgrid.SetColSize(3, 20)
        self.cbgrid.SetColLabelValue(4, "Memo")
        self.cbgrid.SetColSize(4, 150)
        self.cbgrid.SetColLabelValue(5, "Amount")
        self.cbgrid.SetColSize(5, 60)
        self.cbgrid.SetColLabelValue(6, "Balance")
        self.cbgrid.SetColSize(6, 60)
        self.cbgrid.SetSize((1830, 600))             # was (610, 300) JJG

    def do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.cbgrid, 1, wx.EXPAND, 0)
        self.SetAutoLayout(1)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        self.Layout()

    def redraw_all(self, index=None):
        nrows = self.cbgrid.GetNumberRows()
        if nrows: self.cbgrid.DeleteRows(0, nrows)
        ntransactions = len(self.cur_transaction)
        total = 0
        self.cbgrid.AppendRows(ntransactions)
        for i in range(ntransactions):
            transaction = self.cur_transaction[i]
            self.cbgrid.SetCellValue(i, 0, transaction.date.formatUS())
            if transaction.number: self.cbgrid.SetCellValue(i, 1, '%d' % transaction.number)
            self.cbgrid.SetCellValue(i, 2, transaction.payee)
            if transaction.cleared:
                self.cbgrid.SetCellValue(i, 3, 'x')
            if transaction.memo: self.cbgrid.SetCellValue(i, 4, transaction.memo)
            self.cbgrid.SetCellValue(i, 5, '%.2f' % transaction.amount)
            total += transaction.amount
            self.cbgrid.SetCellValue(i, 6, '%.2f' % total)

        if index == -1:
            self.cbgrid.SetGridCursor(ntransactions - 1, 0)
            self.cbgrid.MakeCellVisible(ntransactions - 1, 1)
        elif index > 0:
            self.cbgrid.SetGridCursor(index, 0)
            self.cbgrid.MakeCellVisible(index, 1)
        return

    def cellchange(self, evt):
        doredraw = 0
        row = evt.GetRow()
        col = evt.GetCol()
        if row < 0: return
        if row >= len(self.cur_transaction):
            print "Warning: modifying incorrect cell!"
            return
        self.edited = 1
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
        self.cur_transaction = Transaction()
        self.edited = 0
        d = wx.FileDialog(self, "Open", "", "", "*.qif", wx.OPEN)
        if d.ShowModal() == wx.ID_OK:
            fname = d.GetFilename()
            dir = d.GetDirectory()
            self.cur_transaction.read_qif(os.path.join(dir, fname))
            self.redraw_all(-1)
        if self.cur_transaction.name: self.SetTitle("PyAsset: %s" % self.cur_transaction.name)
        return

    def save_file(self, *args):
        for cur_transaction in self.transactions:
            if not cur_transaction.filename:
                self.save_as_file()
            else:
                self.edited = 0
            self.cur_transaction.write_qif()
        return

    def save_as_file(self, *args):
        d = wx.FileDialog(self, "Save", "", "", "*.qif", wx.SAVE)
        if d.ShowModal() == wx.ID_OK:
            fname = d.GetFilename()
            dir = d.GetDirectory()
            self.cur_transaction.write_qif(os.path.join(dir, fname))
        if self.cur_transaction.name: self.SetTitle("PyAsset: %s" % self.cur_transaction.name)
        return

    def close(self, *args):
        if self.edited:
            d = wx.MessageDialog(self, 'Save file before closing', 'Question',
                                 wx.YES_NO)
            if d.ShowModal() == wx.ID_YES: self.save_file()
        nrows = self.cbgrid.GetNumberRows()
        if nrows: self.cbgrid.DeleteRows(0, nrows)
        self.edited = 0
        self.cur_transaction = Asset()
        return

    def quit(self, *args):
        self.close()
        self.Close(wx.true)

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
            # print total_name_in, total_name_def, total_name_qif
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
            else:
                d = wx.MessageDialog(self, error, wx.OK | wx.ICON_INFORMATION)
                d.ShowModal()
                d.Destroy()
                return
        if self.cur_transaction.name: self.SetTitle("PyAsset: %s" % self.cur_transaction.name)
        return

    def export_text(self, *args):
        d = wx.FileDialog(self, "Save", "", "", "*.txt", wx.SAVE)
        if d.ShowModal() == wx.ID_OK:
            fname = d.GetFilename()
            dir = d.GetDirectory()
            self.cur_transaction.write_txt(os.path.join(dir, fname))
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
        newcb.filename = self.cur_transaction.filename
        newcb.name = self.cur_transaction.name
        newcb.append(newcb_starttransaction)
        archtot = 0

        for transaction in self.cur_transaction:
            if transaction.date < date and transaction.cleared:
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
        self.edited = 1
        return

    def newentry(self, *args):
        self.edited = 1
        self.cur_transaction.append(Transaction())
        self.cbgrid.AppendRows()
        ntransactions = self.cbgrid.GetNumberRows()
        self.cbgrid.SetGridCursor(ntransactions - 1, 0)
        self.cbgrid.MakeCellVisible(ntransactions - 1, 1)

    def sort(self, *args):
        self.edited = 1
        self.cur_transaction.sort()
        self.redraw_all(-1)

    def voidentry(self, *args):
        index = self.cbgrid.GetGridCursorRow()
        if index < 0: return
        d = wx.MessageDialog(self,
                             "Really void this transaction?",
                             "Really void?", wx.YES_NO)
        if d.ShowModal() == wx.ID_YES:
            self.edited = 1
            transaction = self.cur_transaction[index]
            today = Date()
            transaction.amount = 0
            transaction.payee = "VOID: " + transaction.payee
            transaction.memo = "voided %s" % today.formatUS()
        self.redraw_all(index)  # redraw only [index:]
        return

    def deleteentry(self, *args):
        index = self.cbgrid.GetGridCursorRow()
        if index < 0: return
        d = wx.MessageDialog(self,
                             "Really delete this transaction?",
                             "Really delete?", wx.YES_NO)
        if d.ShowModal() == wx.ID_YES:
            del self.cur_transaction[index]
        self.redraw_all(index - 1)  # only redraw cells [index-1:]
        return

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

        cleared_balance = self.get_cleared_balance()
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
            if d.ShowModal() == wx.ID_YES: self.adjust_balance(difference)
            d.Destroy()
        return

    def adjust_balance(self, diff):
        self.edited = 1
        transaction = Transaction()
        transaction.payee = "Balance Adjustment"
        transaction.amount = diff
        transaction.cleared = 1
        transaction.memo = "Adjustment"
        self.cur_transaction.append(transaction)
        self.redraw_all(-1)  # only redraw [-1]?
        return

    def get_cleared_balance(self):
        total = 0.
        for transaction in self.cur_transaction:
            if transaction.cleared:
                total = total + transaction.amount
        return total

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

    def markcleared(self, *args):
        index = self.cbgrid.GetGridCursorRow()
        if index < 0: return
        if not self.cur_transaction[index].cleared: self.edited = 1
        self.cur_transaction[index].cleared = 1
        self.cbgrid.SetCellValue(index, 3, 'x')
        return
