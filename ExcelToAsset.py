#!/usr/bin/env /usr/local/bin/pythonw
"""
INSTALLATION/REQUIREMENTS
PyAsset requires Python (>=3.7) and wxPython.

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
#  04/02/2023     Version v1.0
#  01/01/2024     Version v1.1       JJG Rewrote ProcessTranactionSheet to handle comments and be more efficient

# TO-DOs
#


from openpyxl.reader.excel import load_workbook

from AssetList import AssetList
from TransactionList import TransactionList
from Transaction import Transaction
from BillList import BillList
import wx

class ExcelToAsset(wx.Frame):
    def __init__(self, parent, title="ExcelToAsset", ignore_sheets=[]):
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
        ws = self.wb.get_sheet_by_name("Assets")
        for row in ws.rows:
            cv = row[0].value
            if cv == None or "Bills" in cv or "Total" in cv or "Cash Flow" in cv:
                continue
            elif "Accounts" in cv or "Other" in cv:
                print(row)
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
                        asset_name = new_asset.get_name()
                        if "HOUSE" in asset_name.upper():
                            new_asset.set_type("House")
                        elif "CAR" in asset_name.upper():
                            new_asset.set_type("Car")
                        elif "Checking" in asset_name:
                            new_asset.set_type("Checking")
                        elif "Savings" in asset_name:
                            new_asset.set_type("Savings")
                        elif "Money Market" in asset_name:
                            new_asset.set_type("Money Market")
                        elif "Overdraft" in asset_name:
                            new_asset.set_type("Overdraft")
                        elif "TSP" in asset_name or "Annuity" in asset_name or "Life" in asset_name:
                            new_asset.set_type("Retirement")
                        elif "Discover" in asset_name or "Visa" in asset_name or "MC" in asset_name or "Master Card" in asset_name or "Blue" in asset_name or "Credit Card" in asset_name:
                            new_asset.set_type("Credit Card")
                        elif "Sears" in asset_name or "Macy's" in asset_name:
                            new_asset.set_type("Store Card")
                        elif "Loan" in asset_name:
                            new_asset.set_type("Loan")
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
        return AssetsFound

    def GetTransactionSheetNames(self):
        return_sheets = []
        if self.wb == None:
            return return_sheets
        sheets = self.wb.get_sheet_names()
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
        ws = self.wb.get_sheet_by_name(SheetName)
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
                        cv =  row[placeIndex[headingUpper]].value
                        if cv == None: continue
                        if "PMT METHOD" == headingUpper:
                            new_transaction.set_pmt_method(cv)
                        elif "CHK #" == headingUpper:
                            pmt_method = new_transaction.get_pmt_method()
                            if pmt_method != None:
                                new_transaction.set_check_num(cv)
                        elif "PAYEE" == headingUpper:
                            new_transaction.set_payee(cv)
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
                    new_transaction.parent = self.parent                # make sure transaction gets attached to asset and not EXCEL object!  JJG 1/15/2023
                    TransactionsFound.insert(new_transaction)
        return TransactionsFound

    def ProcessBillsSheet(self, bills):
        MAX_COLS_TO_PROCESS = 8             # Only these columns have data we want! JJG 4/1/2023
        BillsFound = BillList()
        BillPlaces = dict()
        if self.wb == None:
            return BillsFound
        ws = self.wb.get_sheet_by_name("Bills")

        row_num = 0
        Finished = False
        cur_type = "Unknown"
        for row in ws.rows:
            row_num += 1
            if row_num == 1:
                continue
            col_num = 0
            for cell in row:
                cv = cell.value
                col_num += 1
                if col_num > MAX_COLS_TO_PROCESS:
                    break
                if cv == None: continue
                if col_num == 1 and ("Checking and Savings" in cv or "Credit Card" in cv or "Loans" in cv or "Expenses" in cv):
                    cur_type = cv
                    break
                else:
                    cv = cell.value
                    if col_num == 1:
                        if "TOTALS" in cv: 
                            Finished = True
                            break
                    if row_num == 2:
                        BillPlaces[col_num] = cv
                    else:
                        if col_num == 1:
                            new_bill = BillsFound.append(cv)
                        if new_bill != None:
                            heading = BillPlaces.get(col_num, "None")
                            new_bill.set_type(cur_type)
                            if heading != None and cv != None:
                                heading = heading.upper()
                                if heading == "PAYEE":
                                    new_bill.set_payee(cv)
                                elif heading == "AMOUNT":
                                    new_bill.set_amount(cv)
                                elif heading == "MIN DUE":
                                    new_bill.set_min_due(cv)
                                elif heading == "DUE DATE":
                                    new_bill.set_due_date(cv)
                                elif heading == "SCHED DATE":
                                    new_bill.set_sched_date(cv)
                                elif heading == "PMT ACCT":
                                    new_bill.set_pmt_acct(cv)
                                elif heading == "PMT METHOD":
                                    new_bill.set_pmt_method(cv)
                                elif heading == "FREQUENCY":
                                    new_bill.set_pmt_frequency(cv)
            if Finished:
                break
        return BillsFound

    def MsgBox(self, message):
        d = wx.MessageDialog(self, message, "error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()
