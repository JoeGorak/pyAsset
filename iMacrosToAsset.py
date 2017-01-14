#!/usr/bin/env /usr/local/bin/pythonw
"""
INSTALLATION/REQUIREMENTS
PyAsset requires Python (>=2.1) and wxPython.

COPYRIGHT/LICENSING
Copyright (c) 2017, Joseph J. Gorak. All rights reserved.
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
#  1/7/2017     Initial version v0.1

# TO-DOs
#
#TODO: Clean up some debugs and add Dialog boxes for production

from AssetList import AssetList

class iMacrosToAsset:
    def Month_int(self, month_str):
        months = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        mon_int = 0
        i = 1
        while i < len(months) and mon_int == 0:
            if months[i] == month_str:
                mon_int = i
            i += 1
        return mon_int

    def get_asset_type(self, asset_name):
        if "Checking" in asset_name:
            return("Checking")
        elif "Savings" in asset_name:
            return("Savings")
        elif "Money Market" in asset_name:
            return("Money Market")
        elif "Overdraft" in asset_name:
            return("Overdraft")
        elif "TSP" in asset_name or "Annuity" in asset_name:
            return("Retirement")
        elif "Visa" in asset_name or "MC" in asset_name:
            return("Credit Card")
        elif "Store Card" in asset_name:
            return("Store Card")
        else:
            return("Other")

    def Init(self):
        import win32com.client
        self.iim = win32com.client.Dispatch("imacros")
        self.iim.iimInit("", 1)

    def GetNetInfo(self, net_asset_code):
        from datetime import datetime
        AssetsFound = AssetList()
        net_asset_macro_name = "Retrieve_" + net_asset_code[0] + "_balances"
        print "Running " + net_asset_macro_name
        iret = self.iim.iimPlay(net_asset_macro_name)
        if (iret != 1):
            print "Bad status", iret, "returned from", net_asset_macro_name, "Error text:", self.iim.iimGetErrorText()
        else:
            if net_asset_code[1] != -1:
                InpDate = self.iim.iimGetExtract(1).split(" ")
                month = self.Month_int(InpDate[0])
                if len(InpDate) < 4:
                    InpDate = self.iim.iimGetExtract(1).split("/")
                    month = int(InpDate[0])
                day = int(InpDate[1][:2])
                year = int(InpDate[2])
                try:
                    InpTime = InpDate[3].split(":")
                    ampm = InpDate[4]
                    hour = int(InpTime[0])
                    min = int(InpTime[1])
                    sec = int(InpTime[2])
                    if (ampm == "pm"):
                        hour += 12
                    elif (ampm == "am") and (hour == 12):
                        hour -= 12
                    NewDate = datetime(year, month, day, hour, min, sec)
                except:
                    NewDate = datetime.now()
                extract_index = 2
            else:
                NewDate = datetime.now()
                extract_index = 1
            account_index = 0
            account_negative_flag = net_asset_code[2]
#            print account_negative_flag
            while "NODATA" not in self.iim.iimGetExtract(extract_index):
                assetName = self.iim.iimGetExtract(extract_index)
                extract_index += 1
                asset = AssetsFound.append(assetName)
                asset.set_type(self.get_asset_type(assetName))
#                print "Checking account index", account_index
                account_total = self.iim.iimGetExtract(extract_index).replace("$", "").replace(",", "").replace("(","").replace(")","")
                if account_negative_flag[account_index] == True:
                    asset.set_total("-" + account_total)
                else:
                    asset.set_total(account_total)
                account_index += 1
                extract_index += 1
                asset.set_last_pull_date(NewDate)
        return AssetsFound

    def Finish(self):
        iret = self.iim.iimClose()
        print "Updates Finished, iret = ", iret
        return iret