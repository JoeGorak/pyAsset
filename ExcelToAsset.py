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

#  Version information
#  6/25/2016     Initial version v0.1

# TO-DOs
#
#TODO: Write ProcessTransactionSheet
#TODO: Finish ProcessBillsSheet

from openpyxl.reader.excel import load_workbook

from AssetList import AssetList
from BillList import BillList

class ExcelToAsset:
    def OpenXLSMFile(self, FileName):
        self.wb = load_workbook(FileName, data_only=True, guess_types=False)

    def ProcessAssetsSheet(self):
        AccountWithTransactions = self.wb.get_sheet_names()
        AccountWithTransactions.remove("Bills")
        AssetsFound = AssetList()
        AssetPlaces = dict()
        ColumnHeaders = dict()

        ws = self.wb.get_sheet_by_name("Assets")

        # First, determine all assets being tracked by parsing first column

        for col in ws.columns:
            row_num = 1
            asset_num = 0
            for cell in col:
                cv = cell.value
                if cv != None:
                    new_asset = None
                    if cv in AccountWithTransactions:
                        new_asset = AssetsFound.append(cv)
                        AssetPlaces[asset_num] = (cv, row_num)
                        asset_num += 1
                    elif not ("Bills" in cv or "Accounts" in cv or "Cash" in cv or "Assets" in cv or "Total" in cv):
                        new_asset = AssetsFound.append(cv)
                        AssetPlaces[asset_num] = (cv, row_num)
                        asset_num += 1
                    if new_asset != None:
                        asset_name = new_asset.name
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
                        else:
                            new_asset.set_type("Other")
                row_num += 1
            break

        # Next, get column header locations by locating longest row with labels

        max_len = 0
        max_row = 0
        row_num = 1
        row_len = 0
        for row in ws.rows:
            col_num = 1
            for cell in row:
                cv = cell.value
                if cv != None:
                    row_len += 1
                col_num += 1
            if row_len > max_len:
                max_len = row_len
                max_row = row_num
            row_num += 1
            row_len = 0
        row_num = 1
        for row in ws.rows:
            if row_num == max_row:
                col_num = 1
                for cell in row:
                    cv = cell.value
                    if cv != None and col_num != 1:
                        ColumnHeaders[col_num] = cv
                    col_num += 1
                break
            row_num += 1

        # Finally, get data on assets

        for asset_num in range(0, len(AssetsFound)):
            asset_row_num = AssetPlaces.get(asset_num, "None")[1]
            row_num = 1
            for row in ws.rows:
                if row_num == asset_row_num:
                    col_num = 1
                    asset = AssetsFound[asset_num]
                    for cell in row:
                        heading = ColumnHeaders.get(col_num, "None")
                        if heading != "None":
                            cv = cell.value
                            if "Value (Curr)" in heading:
                                asset.set_total(cv)
                            elif "Value (Proj)" in heading:
                                asset.set_value_proj(cv)
                            elif heading == "last pulled":
                                asset.set_last_pull_date(cv)
                            elif heading == "Limit":
                                asset.set_limit(cv)
                            elif heading == "Avail (Online)":
                                asset.set_avail(cv)
                            elif heading == "Avail (Proj)":
                                asset.set_avail_proj(cv)
                            elif heading == "Rate":
                                asset.set_rate(cv)
                            elif heading == "Payment":
                                asset.set_payment(cv)
                            elif heading == "Due Date":
                                asset.set_due_date(cv)
                            elif heading == "Sched":
                                asset.set_sched(cv)
                            elif heading == "Min Pmt":
                                asset.set_min_pay(cv)
                            elif "Cash Limit" in heading:
                                asset.set_cash_limit(cv)
                            elif "Cash used" in heading:
                                asset.set_cash_used(cv)
                            elif "Cash avail" in heading:
                                asset.set_cash_avail(cv)
                            else:
                                pass
                        col_num += 1
                    break
                row_num += 1

        #print AssetsFound
        return AssetsFound

#TODO: Rewrite ProcessBillsSheet to use correct fields  -- NOT CURRENTLY CALLED FROM AssetFrame.py TO AVOID GENERATING ERRORS!  01/14/2017  JJG
    def ProcessBillsSheet(self, bills):
        bills = BillsFound = BillList()
        BillPlaces = dict()

        ws = self.wb.get_sheet_by_name("Bills")

        col_num = 1
        for col in ws.columns:
            print "Processing col", col
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
        print BillsFound
        return BillsFound
