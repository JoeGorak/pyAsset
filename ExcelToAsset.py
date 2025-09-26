#!/usr/bin/env /usr/local/bin/pythonw
"""
INSTALLATION/REQUIREMENTS
PyAsset requires Python (>=3.7) and wxPython.

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
#  06/11/2016     Initial version v0.1
#  08/07/2021     Version v0.2
#  04/02/2023     Version v1.0
#  01/01/2024     Version v1.1       JJG Rewrote ProcessTranactionSheet to handle comments and be more efficient

# TO-DOs
#

from math import e
from os import error
from openpyxl.reader.excel import load_workbook

from Asset import Asset
from AssetList import AssetList
from TransactionList import TransactionList
from Transaction import Transaction
from BillList import BillList
from Bill import Bill
from Date import Date

import wx

class ExcelToAsset(wx.Frame):
    def __init__(self, parent, title="ExcelToAsset", ignore_sheets=[]):
        self.parent = parent
        if parent != None:
             super(ExcelToAsset, self).__init__(parent, title=title)
        self.wb = None
        self.ignore_sheets = ignore_sheets

    def OpenXLSMFile(self, FileName):
        try:
            self.wb = load_workbook(FileName, read_only=True, data_only=True)
        except:
            error = "No such file or directory: " + FileName
            self.MsgBox(error)

    def ProcessAssetsSheet(self, parent, ignoredHeadings = ['Who']):
        self.parent = parent
        AssetsFound = AssetList(parent)
        if self.wb == None:
            return AssetsFound
        ws = self.wb["Assets"]
        for row in ws.rows:
            cv = row[0].value
            if cv == None or "Bills" in cv or "Total" in cv or "Cash Flow" in cv:
                continue
            elif "Accounts" in cv or "Other" in cv:
                ColumnHeaders = dict()
                col_num = 1
                for cell in row:
                    cv = cell.value
                    if cv != None:
                        if col_num == 1:
                            headerValue = "Name"
                        else:
                            headerValue = cv
                        ColumnHeaders[col_num] = headerValue
                        col_num += 1
                    else:
                        break
                    if len(ColumnHeaders) == 1:
                        continue
#               print(ColumnHeaders)
            else:
                col_num = 1
                for cell in row:
                    cv = cell.value
                    if col_num == 1:
                        # First column means this is a new asset... save name and pointer to the new asset location for later
                        # Also set type of asset using clues from the account name
                        new_asset = AssetsFound.get_asset_by_name(cv)
                        if new_asset == None:
                            new_asset = Asset(name = cv)
                            AssetsFound.append_by_object(new_asset)
                        asset_name = new_asset.get_name()
                        asset_name_upper = asset_name.upper()
                        if "HOUSE" in asset_name_upper:
                            new_asset.set_type("House")
                        elif "CAR" in asset_name_upper:
                            new_asset.set_type("Car")
                        elif "CHECKING" in asset_name_upper:
                            new_asset.set_type("Checking and Savings")
                        elif "SAVINGS" in asset_name_upper:
                            new_asset.set_type("Checking and Savings")
                        elif "MONEY MARKET" in asset_name_upper:
                            new_asset.set_type("Money Market")
                        elif "OVERDRAFT" in asset_name_upper:
                            new_asset.set_type("Overdraft")
                        elif "TSP" in asset_name_upper or "ANNUITY" in asset_name_upper or "LIFE" in asset_name_upper or "ROTH" in asset_name_upper or "IRA" in asset_name_upper:
                            new_asset.set_type("Retirement")
                        elif "DISCOVER" in asset_name_upper or "VISA" in asset_name_upper or "MC" in asset_name_upper or "MASTER CARD" in asset_name_upper or "BLUE" in asset_name_upper or "CREDIT CARD" in asset_name_upper:
                            new_asset.set_type("Credit Card")
                        elif "SEARS" in asset_name_upper or "MACY'S" in asset_name_upper:
                            new_asset.set_type("Store Card")
                        elif "LOAN" in asset_name_upper or "MORTGAGE" in asset_name_upper:
                            new_asset.set_type("Loan")
                        elif "EMERGENCY" in asset_name_upper:
                            new_asset.set_type("Emergency Fund")
                        else:
                            new_asset.set_type("Other")
                    else:  # 2nd and remaining columns are more data for the current asset...
                           # determine what field and update the object appropriately

                        heading = ColumnHeaders.get(col_num, "None")
                        if heading != "None":
                            if "Value (Curr)" in heading:
                                new_asset.set_value(cv)
                            elif "Value (Proj)" in heading:
                                new_asset.set_value_proj(cv)
                            elif "last pulled" in heading:
                                new_asset.set_last_pull_date(cv)
                            elif "Credit Limit" in heading:
                                new_asset.set_limit(cv)
                            elif "Avail (Online)" in heading:
                                new_asset.set_avail(cv)
                            elif "Avail (Proj)" in heading:
                                new_asset.set_avail_proj(cv)
                            elif "Estimate Method" in heading:
                                new_asset.set_est_method(cv)
                            elif "Rate" in heading:
                                new_asset.set_rate(cv)
                            elif "Payment" in heading:
                                new_asset.set_payment(cv)
                            elif "Due Date" in heading:
                                new_asset.set_due_date(cv)
                            elif "Sched" in heading:
                                new_asset.set_sched_date(cv)
                            elif "Min Pmt" in heading:
                                new_asset.set_min_pay(cv)
                            elif "Stmt Bal" in heading:
                                new_asset.set_stmt_bal(cv)
                            elif "Amt Over" in heading:
                                new_asset.set_amt_over(cv)
                            elif "Cash Limit" in heading:
                                new_asset.set_cash_limit(cv)
                            elif "Cash used" in heading:
                                new_asset.set_cash_used(cv)
                            elif "Cash avail" in heading:
                                new_asset.set_cash_avail(cv)
                            else:
                                found = False
                                for ignore in ignoredHeadings:
                                    if ignore in heading:
                                        found = True
                                if not found:
                                    print("ProcessAssetSheets: Unknown field " + heading + " ignored!")
                    col_num += 1
                    if col_num > len(ColumnHeaders):
                        break
        # if self.parent == None, this is the test code and we didn't set up the menus so don't change the menu choices
        test_parent = self.parent
        if AssetsFound != None and test_parent != None:
            self.Parent.fileMenuItem["Open"].Enable(False)
            self.Parent.fileMenuItem["ImportCSV"].Enable(False)
            self.Parent.fileMenuItem["ImportXLSX"].Enable(False)
            self.Parent.fileMenuItem["Save"].Enable(False)              # JJG 08/04/2024 Prevent accidentally overwriting .xlsx if they forget to change filename!
            self.Parent.fileMenuItem["SaveAs"].Enable(True)
            self.Parent.fileMenuItem["Close"].Enable(True)
            self.Parent.fileMenuItem["Export"].Enable(True)
            self.Parent.fileMenuItem["Archive"].Enable(True)
        return AssetsFound

    def GetTransactionSheetNames(self):
        return_sheets = []
        if self.wb == None:
            return return_sheets
        sheets = list(self.wb.sheetnames)
        for sheet in sheets:
            if sheet in self.ignore_sheets:
                continue
            else:
                return_sheets.append(sheet)
        return return_sheets

    def ProcessTransactionSheet(self, whichAsset, SheetName):
        TransactionsFound = TransactionList(whichAsset)
        if self.wb == None:
            return TransactionsFound
        ws = self.wb[SheetName]
        SheetName = str(SheetName).upper()
        if "CHECKING" in SheetName:
            ColumnHeaders = ["Pmt Method", "Chk #", "Payee", "Amt", "B", "Sched date", "Due date", "Comment"]
        else:
            ColumnHeaders = ["Pmt Method", "Payee", "Amt", "B", "Sched date", "Due date", "Comment"]
        placeIndex = {}
        row_num = -1
        for row in ws.rows:
            row_num += 1
            if row_num == 0:
                for index in range(len(ColumnHeaders)):
                    foundIndex = -1
                    for cell in row:
                        if cell.data_type != 's': continue
                        if ColumnHeaders[index].upper() == cell.value.upper():
                            foundIndex = cell.column-1
                            break
                    if foundIndex != -1:
                        placeIndex[ColumnHeaders[index].upper()] = foundIndex
                    else:
                        placeIndex[ColumnHeaders[index].upper()] = -1
            else:
                cv = row[0].value                           # JJG 1/1/2024 Don't waste time on rows without headers
                if cv == None:
                    continue
                else:
                    new_transaction = Transaction(self)
                    for heading in ColumnHeaders:
                        headingUpper = heading.upper()
                        if placeIndex[headingUpper] == -1: continue
                        cv =  row[placeIndex[headingUpper]].value
                        if cv == None: continue
                        if "PMT METHOD" == headingUpper:
                            new_transaction.set_pmt_method(cv)
                        elif "CHK #" == headingUpper:
                            pmt_method = new_transaction.get_pmt_method()
                            if pmt_method != None:
                                new_transaction.set_check_num(cv)
                        elif "PAYEE" == headingUpper:
                            payee = cv
                            new_transaction.set_payee(payee)
                            if payee[0:len("Paydown")]=="Paydown" or payee[0:len("Xfer")]=="Xfer":
                                new_transaction.set_action("+")
                            else:
                                new_transaction.set_action("-")
                        elif "AMT" == headingUpper:
                            new_transaction.set_amount(cv)
                        elif "B" == headingUpper:
                            if cv != "":
                                new_transaction.set_action(cv)
                        elif "SCHED DATE" == headingUpper:
                            if cv != "":
                                new_transaction.set_sched_date(cv)
                        elif "DUE DATE" == headingUpper:
                            if cv != "":
                                new_transaction.set_due_date(cv)
                        elif "COMMENT" == headingUpper:
                            if cv != "" and cv != None:
                                new_transaction.set_comment(cv)
                        else:
                           print("ProcessTransactionSheet: Unknown field " + headingUpper + " on sheet " + SheetName + " ignored!")

                    # At this point we have filled in all the necessaty fields so just make sure the new transaction hasa a scheduled date
                    # Don't add transactions that don't have scheduled date
                    if new_transaction.get_sched_date() == None or new_transaction.get_sched_date() == '':
                        continue

                    new_transaction.parent = self.parent                # make sure transaction gets attached to asset and not EXCEL object!  JJG 1/15/2023

                    # JJG 7/15/2025 Determine transaction state since it is not part of spreadsheet
                    if new_transaction.get_sched_date() != None and new_transaction.get_pmt_method() != "TBD":
                        new_transaction.set_state("scheduled")
                    if new_transaction.get_pmt_method() == "processing":
                        new_transaction.set_state("pending")
                    if new_transaction.get_pmt_method() == "TBD" and new_transaction.get_state() == "unknown" and new_transaction.get_amount() != 0.0:
                        new_transaction.set_comment("Need to schedule this ASAP!")
                    TransactionsFound.insert(new_transaction)
        return TransactionsFound

    def ProcessBillsSheet(self, haveParent=True):
        MAX_COLS_TO_PROCESS = 8             # Only these columns have data we want! JJG 4/1/2023
        BillsFound = BillList()
        BillPlaces = dict()
        if self.wb == None:
            return BillsFound
        ws = self.wb["Bills"]

        row_num = 0
        cur_type = "unknown"
        if haveParent:
            self.parent = wx.GetTopLevelParent(self).Parent
            title = self.GetTitle()
            super(ExcelToAsset, self).__init__(self.parent, title=title)
            new_bill = Bill(self.parent)
        else:
            new_bill = Bill(None)
        wb = None

        ExcelReadStates = ["SectionHeader", "HeaderRow", "DataRow"]             # These are the states we can be in reading the excel file
        ExcelReadState = "SectionHeader"                                        # Start out expecting a section header

        Finished = False

        for row in list(ws.rows):
            if Finished:                                                        # Check for early termination of the state machine JJG 9/23/2025
                break
            row_num += 1
            if row_num == 1:                                                   # Ignore the first row which is just the title
                continue
            col_num = 0
            for cell in row:
                # Read the next column in the current row and update our internal column counter
                cv = cell.value
                col_num += 1

                # If we are beyond the number of columns we want in the current row, go get the next row
                if col_num > MAX_COLS_TO_PROCESS:

                    # DEBUG TO TEST ERROR HANDLING
                    #ExcelReadState = "BadState"
                    # END DEBUG

                    # If we are reading data rows, Insert the bill that got constructed from the last row

                    if ExcelReadState == "DataRow":
                        BillsFound.insert(new_bill)
                        if self.parent != None:
                            new_bill = Bill(self.parent)
                        else:
                            new_bill = Bill(None)
                    elif ExcelReadState == "HeaderRow":
                        ExcelReadState = "DataRow"
                    else:
                        if ExcelReadState == "SectionHeader":
                            ExcelReadState = "HeaderRow"
                        else:
                            error = "Internal error in ExcelToAsset.ProcessBillsSheet: Unexpected ExcelReadState "
                            error += ExcelReadState + "\nValid ExecReadStates are " + str(ExcelReadStates)
                            self.MsgBox(error)
                            return None
                    break                                    # Since we have read all the data we need on the current row, go get the next row

                # If the column we just read has no data, go get the next column
                if cv == None: continue

                # If the column we just read is has a string value, convert it to all lower case to simply the rest of our processing
                if type(cv) is str:
                    cv = cv.lower()

                # if this is a section header line, record the type and go get the next row (which should be the header row)
                if ExcelReadState == "SectionHeader":
                    # Sections headers in EXCEL files are a superset of the bill types so extract the appropriate part and use that as the bill type  JJG 9/22/2025
                    bill_types = ["checking and savings", "credit card", "loan", "expense"]
                    for cur_type in bill_types:
                        bill_type = cv[:len(cur_type)]
                        try:
                            bill_type_index = bill_types.index(bill_type)
                        except:
                            bill_type_index = -1
                        if col_num == 1 and bill_type_index != -1:
                            cur_type = new_bill.set_type(bill_types[bill_type_index])
                            break                                   # Found the type, no need to keep looking
                        # If we didn't find a valid section header (bill_type) check if this is the "TOTALS" line in which case we don't want to process anymore
                        if bill_type_index == -1:
                            error = "ProcessBillsSheet: Unknown section header " + cv + " on row " + str(row_num) + " ignored!"
                            self.MsgBox(error)
                    ExcelReadState = "HeaderRow"                    # After a section header, we expect a header row next
                    break                                               # Go get the next row, which should be the header row   
                else:
                    # If we are expecting a header row, make a record of where the columns we want are
                    if ExcelReadState == "HeaderRow":
                        BillPlaces[col_num] = cv
                    else:                                           
                        if cv == "totals":
                            Finished = True
                            break                                   # A "SectionHeader" of Totals means we are done since we don't want the TOTALS (yet!)
                        heading = BillPlaces.get(col_num, "None").lower()

                        # if we just processed the header column, go get the next column!       JJG 9/22/2025
                        if heading == cv:
                            continue
                        if heading != None and cv != None:
                            if heading == "payee":
                                new_bill.set_payee(cv)
                            elif heading == "amount":
                                new_bill.set_amount(cv)
                            elif heading == "min due":
                                new_bill.set_min_due(cv)
                            elif heading == "due date":
                                new_bill.set_due_date(cv)
                            elif heading == "sched date":
                                new_bill.set_sched_date(cv)
                            elif heading == "pmt acct":
                                new_bill.set_pmt_acct(cv)
                            elif heading == "pmt method":
                                new_bill.set_pmt_method(cv)
                            elif heading == "frequency":
                                new_bill.set_pmt_frequency(cv)

        # At this point bills were inserted in the order they were found in the Bill sheet.
        # Now do a multi-level sort on the list of bills.  JJG 1/25/2025
        BillsFound.sort_by_fields(BillList.getSortOrder(self))
        return BillsFound

    def MsgBox(self, message):
        if self.parent != None:
            d = wx.MessageDialog(self, message, "error", wx.OK | wx.ICON_INFORMATION)
            d.ShowModal()
            d.Destroy()
        else:
            d = wx.MessageDialog(None, message, "error", wx.OK | wx.ICON_INFORMATION)
            d.ShowModal()
            d.Destroy()


if __name__ == '__main__':
    import sys
    import wx
    from AssetFrame import AssetFrame

    class testFrame(wx.Frame):
        test_filename = 'C:\\Users\\joego\\Desktop\\Finances for budgeting.xlsm';
        ignore_sheets = ['Assets', 'Bills'];

        def __init__(self):
            super().__init__(parent=None, title="ExceltoAsset tester")
            self.assetFrame = AssetFrame(self, 'PyAsset', "", "")
            self.assetFrame.Show(False)                             # We don't need (or want!) to see the Asset Frame JJG 9/22/2025
            self.Bind(wx.EVT_CLOSE,self.close)
            
            panel = wx.Panel(self)

            # The widget that will receive the keystrokes
            self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        
            # A button to trigger the testing
            button = wx.Button(panel, label='do tests')
            button.Bind(wx.EVT_BUTTON, self.doTests)

            # Layout
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 5)
            sizer.Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
            panel.SetSizer(sizer)

            self.Show()


        def testAssets(self):
            etoa = ExcelToAsset(None, self.ignore_sheets)
            etoa.OpenXLSMFile(self.test_filename)
            AssetsFound = etoa.ProcessAssetsSheet(None)
            if AssetsFound != None:
                print("Found " + str(len(AssetsFound)) + " assets!")
                for asset in AssetsFound:
                    print(asset)
            self.AssetList = AssetsFound

        def testTransactions(self):
            etoa = ExcelToAsset(None, self.ignore_sheets)
            etoa.OpenXLSMFile(self.test_filename)
            SheetsFound = etoa.GetTransactionSheetNames()
            print("Found " + str(len(SheetsFound)) + " transaction sheets!")
            for sheet in SheetsFound:
                if sheet in self.ignore_sheets:
                    print("Ignoring sheet ", sheet)
                    continue
                print("Processing sheet " + sheet)
                TransactionsFound = etoa.ProcessTransactionSheet(self.AssetList.get_asset_by_name(sheet), sheet)
                if TransactionsFound != None:
                    print("Found " + str(len(TransactionsFound)) + " transactions on sheet " + sheet + "!")
                    if len(TransactionsFound) != 0:
                        for transaction in TransactionsFound:
                            print(transaction)
    
        def testBills(self):
            etoa = ExcelToAsset(None, self.ignore_sheets)
            etoa.OpenXLSMFile(self.test_filename)
            BillsFound = etoa.ProcessBillsSheet(False)
            if BillsFound != None:
                print("Found " + str(len(BillsFound)) + " bills!")
                for bill in BillsFound:
                    print(bill)

        def doTests(self, event):
            print("Testing loading assets\n\n")
            self.testAssets()
            print("\nTesting loading transactions\n\n")
            self.testTransactions()
            print("\nTesting loading bills\n\n")
            self.testBills()
            print("\nExcelToAsset testing done!")

        def close(self, event):
            self.assetFrame.Destroy()
            self.Destroy()

    app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
    app.frame = testFrame()
    app.frame.Show()
    app.MainLoop()
