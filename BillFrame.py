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
#  04/25/2023     Initial version v0.1

# To Do list:
# Speed redraw_all: break into redraw_all, redraw_range, redraw_totals
# Save a backup version of files
# Read and save CBB files?
# Undo?
# Plot balance vs day
# Search functions
# goto date

from platform import java_ver
import wx
import wx.grid
import csv
import os
from Asset import Asset
from Date import Date
from HelpDialog import HelpDialog
from Bill import Bill
from BillGrid import BillGrid
from BillList import BillList

class BillFrame(wx.Frame):
    def __init__(self, style, parent, my_id, bills, title="PyAsset:Bills", filename="", **kwds):
        self.bills = bills
        self.parent = parent
        self.dateFormat = Date.get_global_date_format(self)
        self.dateSep = Date.get_global_date_sep(self)

#        if self.bills != None and self.bills.bills != []:
#            self.cur_bill = self.bills.bills[0]
#        else:
#            self.cur_bill = None

        self.edited = False
        self.rowSize = 10
        self.colSize = 20

        if style == None:
            style = wx.DEFAULT_FRAME_STYLE
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, parent, my_id, title, **kwds)
        self.Bind(wx.EVT_CLOSE,self.close)

        self.make_widgets()

        self.filename = filename

        self.SetTitle(title)
        self.redraw_all()

    def make_widgets(self):
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)
        self.statusbar = self.CreateStatusBar(1, 0)
        self.make_filemenu()
        self.make_editmenu()
        self.make_helpmenu()
        self.make_bill_grid()
        self.set_properties()
        self.do_layout()

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
        self.menubar.Append(self.filemenu, "&File")
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
        self.menubar.Append(self.editmenu, "&Edit")
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

        self.menubar.Append(self.helpmenu, "&Help")
        self.Bind(wx.EVT_MENU, self.about, None, wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.gethelp, None, ID_HELP)

    def make_bill_grid(self):
        self.panel = wx.Panel(self)
        self.bill_grid = BillGrid(self, self.panel)
        self.rowSize = 150
        self.colSize = self.bill_grid.getNumColumns()
        self.bill_grid.CreateGrid(self.rowSize, self.colSize) 
        return self.bill_grid

    def get_bill_grid(self):
        return self.bill_grid

    def set_properties(self):
        self.total_width = self.bill_grid.set_properties(self)

    def do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.bill_grid, 1, wx.EXPAND)
        self.panel.SetSizer(sizer)
        self.Layout()

    def DisplayMsg(self, str):
        d = wx.MessageDialog(self, str, "Error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()
        return wx.CANCEL

    def redraw_all(self, index=None):
        if index == None:
            index = -1
        nbills = 0
        if self.bills != None:
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
            for col in range(self.bill_grid.getNumColumns()):
                ret_val = wx.OK
                if row < 0 or row >= nbills:
                    str = "Warning: skipping redraw on bad cell %d %d!" % (row, col)
                    ret_val = self.DisplayMsg(str)
                if ret_val != wx.OK:
                    continue

                cellType = self.bill_grid.getColType(col)
                if cellType == self.bill_grid.DOLLAR_TYPE:
                    self.bill_grid.GridCellDollarRenderer(row, col)
                elif cellType == self.bill_grid.RATE_TYPE:
                    self.bill_grid.GridCellPercentRenderer(row, col)
                elif cellType == self.bill_grid.DATE_TYPE:
                    self.bill_grid.GridCellDateRenderer(row, col)
                elif cellType == self.bill_grid.DATE_TIME_TYPE:
                    self.bill_grid.GridCellDateTimeRenderer(row, col)
                elif cellType == self.bill_grid.STRING_TYPE:
                    self.bill_grid.GridCellStringRenderer(row, col)
                else:
                    self.bill_grid.GridCellErrorRenderer(row, col)

        win_height = (nbills+3) * self.rowSize + 150                 # +3 for header lines + 150 for borders
        self.SetSize(self.total_width + 150, win_height)
        self.Show()

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
            new_bill = Bill()
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
        self.parent.redraw_all(-1)
        self.parent.SetTitle("PyAsset: %s" % self.filename)
        return

    def save_file(self, *args):
        self.edited = False
        billList = self.parent.getBillsList()
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
                self.bill_grid.ClearGrid()
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
        bill_grid = self.get_bill_grid()
        if bill_grid != None:
            bill_grid.close()
            del bill_grid
        if self.panel != None:
            del self.panel
        bill_frame = self.parent.getBillFrame()
        if bill_frame != None:
            self.parent.removeBillFrame()
        return

    def quit(self, *args):
        self.close()
        self.Close()

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
                self.SetTitle(title)

            else:
#                d = wx.MessageDialog(self, error, wx.OK | wx.ICON_INFORMATION)
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
        self.bills.append(Bill())
        self.bill_grid.AppendRows()
        nbills = self.bill_grid.GetNumberRows()
        self.bill_grid.SetGridCursor(nbills - 1, 0)
        self.bill_grid.MakeCellVisible(nbills - 1, 1)

    def sort(self, *args):
        self.edited = True
        self.bills.sort()
        self.redraw_all(-1)

    def voidentry(self, *args):
        index = self.bill_grid.GetGridCursorRow()
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
                for i in range(index,len(self.bills)):
                    self.bill_grid.setValue(i, "Value", str(round(self.bills[i].get_current_value(),2)))
                self.redraw_all()  # redraw only [index:]

    def deleteentry(self, *args):
        index = self.bill_grid.GetGridCursorRow()
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
                             "Python Asset Manager\n"
                             "Copyright (c) 2016-2024 Joseph J. Gorak\n"
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
        index = self.bill_grid.GetGridCursorRow()
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
                self.bill_grid.setValue(index, "State", cur_state)
            else:
                self.bills[index].set_state(prev_state)
                self.bill_grid.setValue(index, "State", prev_state)
        return

    def billchange(self, which_bill, which_column, new_value):
        colName = self.bill_grid.getColName(which_column)
        bill_changed = self.bills[which_bill]
        modified = True
        print("billFrame: Recieved notification that bill ", bill_changed.get_payee(), " column", colName, "changed, new_value", new_value)
        if colName == "Payee":
            bill_changed.set_payee(new_value)
        elif colName == "Amount":
            bill_changed.set_amount(new_value)
        elif colName == "Min Due":
            bill_changed.set_min_due(new_value)
        elif colName == "Due Date":
            bill_changed.set_due_date(new_value)
        elif colName == "Sched Date":
            bill_changed.set_sched_date(new_value)
        elif colName == "Pmt Acct":
            bill_changed.set_pmt_acct(new_value)
        elif colName == "Due Date":
            bill_changed.set_due_date(new_value)
        elif colName == "Pmt Method":
            bill_changed.set_pmt_method(new_value)
        elif colName == "Frequency":
            bill_changed.set_pmt_frequency(new_value)
        else:
            self.DisplayMsg("Unknown column " + colName + " ignored!")
            modified = False

        if modified == True:
            self.edited = True

    def MsgBox(self, message):
        d = wx.MessageDialog(self, message, "error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()
