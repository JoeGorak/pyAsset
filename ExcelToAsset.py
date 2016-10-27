#!/usr/bin/env /usr/local/bin/pythonw
"""
INSTALLATION/REQUIREMENTS
PyAsset requires Python (>=2.1) and wxPython.

COPYRIGHT/LICENSING
Copyright (c) 2016, Joseph J. Gorak. All rights reserved.
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


from openpyxl.reader.excel import load_workbook

from AssetList import AssetList

class ExcelToAsset:
    def OpenXLSMFile(self, FileName):
        self.wb = load_workbook(FileName, data_only=True, guess_types=False)

    def ProcessAssetsSheet(self):
        AccountWithTransactions = self.wb.get_sheet_names()
        AssetsFound = AssetList()
        AssetPlaces = dict()

        ws = self.wb.get_sheet_by_name("Assets")

        col_num = 1
        for col in ws.columns:
            row_num = 1
            heading = ""
            for cell in col:
                cv = cell.value
                if cv != None:
                    if col_num == 1:
                        new_asset = None
                        if cv in AccountWithTransactions:
                            new_asset = AssetsFound.append(cv)
                            AssetPlaces[row_num] = cv
                        elif not ("Bills" in cv or "Accounts" in cv or "Cash" in cv or "Assets" in cv or "Total" in cv):
                            new_asset = AssetsFound.append(cv)
                            AssetPlaces[row_num] = cv
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
                            elif "TSP" in asset_name or "Annuity" in asset_name:
                                new_asset.set_type("Retirement")
                            elif "Visa" in asset_name or "MC" in asset_name:
                                new_asset.set_type("Credit Card")
                            elif "Store Card" in asset_name:
                                new_asset.set_type("Store Card")
                            else:
                                new_asset.set_type("Other")
                    else:
                        if AssetPlaces.get(row_num, "None") != "None":
                            if heading == "Value  (Curr)" or heading == "Estimated Value":
                                for i in range(len(AssetsFound)):
                                    asset = AssetsFound[i]
                                    if asset.name == AssetPlaces[row_num]:
                                        asset.set_total(cv)
                                        break
                            elif heading == "last pulled":
                                for i in range(len(AssetsFound)):
                                    asset = AssetsFound[i]
                                    if asset.name == AssetPlaces[row_num]:
                                        asset.set_last_pull_date(cv)
                                        break
                            elif heading == "Limit" and cv != 0:
                                for i in range(len(AssetsFound)):
                                    asset = AssetsFound[i]
                                    if asset.name == AssetPlaces[row_num]:
                                        asset.set_limit(cv)
                                        break
                            elif heading == "Avail (Online)" and cv != 0:
                                for i in range(len(AssetsFound)):
                                    asset = AssetsFound[i]
                                    if asset.name == AssetPlaces[row_num]:
                                        asset.set_avail(cv)
                                        break
                            elif heading == "Rate":
                                for i in range(len(AssetsFound)):
                                    asset = AssetsFound[i]
                                    if asset.name == AssetPlaces[row_num]:
                                        asset.set_rate(cv)
                                        break
                            elif heading == "Payment":
                                for i in range(len(AssetsFound)):
                                    asset = AssetsFound[i]
                                    if asset.name == AssetPlaces[row_num]:
                                        asset.set_payment(cv)
                                        break
                            elif heading == "Due Date":
                                for i in range(len(AssetsFound)):
                                    asset = AssetsFound[i]
                                    if asset.name == AssetPlaces[row_num]:
                                        asset.set_due_date(cv)
                                        break
                            elif heading == "Sched":
                                for i in range(len(AssetsFound)):
                                    asset = AssetsFound[i]
                                    if asset.name == AssetPlaces[row_num]:
                                        asset.set_sched(cv)
                                        break
                            elif heading == "Min Pmt":
                                for i in range(len(AssetsFound)):
                                    asset = AssetsFound[i]
                                    if asset.name == AssetPlaces[row_num]:
                                        asset.set_rate(cv)
                                        break
                            else:
                                pass
        #                        print cv, row_num, heading, AssetPlaces[row_num]
                        else:
                            if str(cv)[0] not in ['0','1','2','3','4','5','6','7','8','9','-']:
                                heading = cv
                row_num += 1
            col_num += 1
        #print AssetsFound
        return AssetsFound
