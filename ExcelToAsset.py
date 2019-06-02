#!/usr/bin/env /usr/local/bin/pythonw
"""
INSTALLATION/REQUIREMENTS
PyAsset requires Python (>=2.1) and wxPython.

COPYRIGHT/LICENSING
Copyright (c) 2016,2017 Joseph J. Gorak. All rights reserved.
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

# TO-DOs
#
#TODO: Write ProcessTransactionSheet
#TODO: Finish ProcessBillsSheet

from openpyxl.reader.excel import load_workbook

from AssetList import AssetList
from BillList import BillList

class ExcelToAsset:
    def __init__(self, ignore_sheets=[]):
        self.wb = ''
        self.ignore_sheets = ignore_sheets

    def OpenXLSMFile(self, FileName):
        self.wb = load_workbook(FileName, read_only=True, data_only=True, guess_types=False)

    def GetTransactionSheetNames(self):
        sheets = self.wb.get_sheet_names()
        return_sheets = []
        if self.ignore_sheets != None:
            for sheet in sheets:
                if sheet not in self.ignore_sheets:
                    return_sheets.append(sheet)
        return return_sheets

    def ProcessAssetsSheet(self) -> object:
        AssetsFound = AssetList()

        ws = self.wb.get_sheet_by_name("Assets")

        for row in ws.rows:
            cv = row[0].value
            if cv == None or "Bills" in cv or "Total" in cv or "Cash Flow" in cv:
                continue
            elif "Accounts" in cv or "Other" in cv:
#                print(row)
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
#                print(ColumnHeaders)
            else:
                col_num = 1
                for cell in row:
                    cv = cell.value
                    if col_num == 1:

                        # First column means this is a new asset... save name and pointer to the new asset location for later
                        # Also set type of asset using clues from the account name
                        new_asset = AssetsFound.append(cv)
                        asset_name = new_asset.get_name()
                        if "Checking" in asset_name:
                            new_asset.set_type("Checking")
                        elif "Savings" in asset_name:
                            new_asset.set_type("Savings")
                        elif "Money Market" in asset_name:
                            new_asset.set_type("Money Market")
                        elif "Overdraft" in asset_name:
                            new_asset.set_type("Overdraft")
                        elif "TSP" in asset_name or "Annuity" in asset_name or "Life" in asset_name:
                            new_asset.set_type("Retirement")
                        elif "Visa" in asset_name or "MC" in asset_name:
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
                                new_asset.set_total(cv)
                            elif "Value (Proj)" in heading:
                                new_asset.set_value_proj(cv)
                            elif heading == "last pulled":
                                new_asset.set_last_pull_date(cv)
                            elif heading == "Limit":
                                new_asset.set_limit(cv)
                            elif heading == "Avail (Online)":
                                new_asset.set_avail(cv)
                            elif heading == "Avail (Proj)":
                                new_asset.set_avail_proj(cv)
                            elif heading == "Estimate Method":
                                new_asset.set_est_method(cv)
                            elif heading == "Rate":
                                new_asset.set_rate(cv)
                            elif heading == "Payment":
                                new_asset.set_payment(cv)
                            elif heading == "Due Date":
                                new_asset.set_due_date(cv)
                            elif heading == "Sched":
                                new_asset.set_sched(cv)
                            elif heading == "Min Pmt":
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
                                print("Unknown field " + heading + " ignored!")
                                pass

                    col_num += 1
                    if col_num > len(ColumnHeaders):
                        break

        return AssetsFound

#TODO: Rewrite ProcessBillsSheet to use correct fields  -- NOT CURRENTLY CALLED FROM AssetFrame.py TO AVOID GENERATING ERRORS!  01/14/2017  JJG
    def ProcessBillsSheet(self, bills):
        bills = BillsFound = BillList()
        BillPlaces = dict()

        ws = self.wb.get_sheet_by_name("Bills")

        col_num = 1
        for col in ws.columns:
            print("Processing col", col)
            row_num = 1
            heading = ""
            for cell in col:
                cv = cell.value
                if cv != None:
                    if col_num == 1:
                        if "TOTALS" in cv: break
                        if "Assets" in cv or "Payee" in cv or "Checking Account" in cv or "Credit Card" in cv or "Other Source" in cv \
                                or "Loan" in cv or "Expenses" in cv:
                            continue
                        new_bill = BillsFound.append(cv)
                        BillPlaces[row_num] = cv
                        if new_bill != None:
                            bill_name = new_bill.name
                            if "Checking" in bill_name:
                                new_bill.set_type("Checking")
                            elif "Savings" in bill_name:
                                new_bill.set_type("Savings")
                            elif "Money Market" in bill_name:
                                new_bill.set_type("Money Market")
                            elif "Overdraft" in bill_name:
                                new_bill.set_type("Overdraft")
                            elif "TSP" in bill_name or "Annuity" in bill_name:
                                new_bill.set_type("Retirement")
                            elif "Visa" in bill_name or "MC" in bill_name:
                                new_bill.set_type("Credit Card")
                            elif "Store Card" in bill_name:
                                new_bill.set_type("Store Card")
                            else:
                                new_bill.set_type("Other")
                    else:
                        if BillPlaces.get(row_num, "None") != "None":
                            if "Value (Curr)" in heading or "Estimated Value" in heading:
                                for i in range(len(BillsFound)):
                                    asset = BillsFound[i]
                                    if asset.name == BillPlaces[row_num]:
                                        asset.set_total(cv)
                                        break
                            elif heading == "last pulled":
                                for i in range(len(BillsFound)):
                                    asset = BillsFound[i]
                                    if asset.name == BillPlaces[row_num]:
                                        asset.set_last_pull_date(cv)
                                        break
                            elif heading == "Limit" and cv != 0:
                                for i in range(len(BillsFound)):
                                    asset = BillsFound[i]
                                    if asset.name == BillPlaces[row_num]:
                                        asset.set_limit(cv)
                                        break
                            elif heading == "Avail (Online)" and cv != 0:
                                for i in range(len(BillsFound)):
                                    asset = BillsFound[i]
                                    if asset.name == BillPlaces[row_num]:
                                        asset.set_avail(cv)
                                        break
                            elif heading == "Rate":
                                for i in range(len(BillsFound)):
                                    asset = BillsFound[i]
                                    if asset.name == BillPlaces[row_num]:
                                        asset.set_rate(cv)
                                        break
                            elif heading == "Payment":
                                for i in range(len(BillsFound)):
                                    asset = BillsFound[i]
                                    if asset.name == BillPlaces[row_num]:
                                        asset.set_payment(cv)
                                        break
                            elif heading == "Due Date":
                                for i in range(len(BillsFound)):
                                    asset = BillsFound[i]
                                    if asset.name == BillPlaces[row_num]:
                                        asset.set_due_date(cv)
                                        break
                            elif heading == "Sched":
                                for i in range(len(BillsFound)):
                                    asset = BillsFound[i]
                                    if asset.name == BillPlaces[row_num]:
                                        asset.set_sched(cv)
                                        break
                            elif heading == "Min Pmt":
                                for i in range(len(BillsFound)):
                                    asset = BillsFound[i]
                                    if asset.name == BillPlaces[row_num]:
                                        asset.set_rate(cv)
                                        break
                            else:
                                pass
        #                        print cv, row_num, heading, BillPlaces[row_num]
                        else:
                            if str(cv)[0] not in ['0','1','2','3','4','5','6','7','8','9','-']:
                                heading = cv
                row_num += 1
            col_num += 1
        print(BillsFound)
        return BillsFound
