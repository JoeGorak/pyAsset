#!/usr/bin/env /usr/local/bin/pythonw
"""
INSTALLATION/REQUIREMENTS
PyAsset requires Python (>=3.7) and wxPython.

COPYRIGHT/LICENSING
Copyright (c) 2017-2025 Joseph J. Gorak. All rights reserved.
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

# 7/12/25 JJG As iMacros is no longer supported, this code is being removed from the base PyAsset code and will not be included in the PyAsset 1.0 release.

# TO-DOs
#
#TODO: Clean up some debugs and add Dialog boxes for production
#TODO: See if we can use datetime module?

from AssetList import AssetList
from Date import Date
import csv
import re

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
        elif "Agency" in asset_name or "Employee" in asset_name or "Matching" in asset_name or "TSP" in asset_name or "Annuity" in asset_name:
            return("Retirement")
        elif "General Purpose" in asset_name:
            return("Loan")
        elif "Mortgage" in asset_name:
            return("Mortgage")
        elif "Visa" in asset_name or "MC" in asset_name or "Mastercard" in asset_name:
            return("Credit Card")
        elif "Store Card" in asset_name or "Macy's" in asset_name or "Sears" in asset_name:
            return("Store Card")
        else:
            return("Other")

    def Init(self):
        import win32com.client
        self.iim = win32com.client.Dispatch("imacros")
        self.iim.iimInit("-cr", 1)              # -cr starts Chrome, -ie starts Internet Explorer, -fx starts Firefox, more flags at https://wiki.imacros.net/iimInit()
        self.macro_path = 'E:\\Dropbox\\Private\\Programming\\iMacros'          # TODO: Eliminate hard-coded path! JJG 1/25/2025

    def GetNetInfo(self, net_asset_code):
        from datetime import datetime
        AssetsFound = AssetList(self)
        net_asset_macro_name = "Retrieve_" + net_asset_code[0] + "_balances.iim"
        print("Running " + net_asset_macro_name)
        net_asset_macro_name = self.macro_path + net_asset_macro_name
        iret = self.iim.iimPlay(net_asset_macro_name)

        # JJG 3/31/24 For some reason. extract isn't working so parse the .csv file that is created.
#
#        LastExtract = []
#        with open(self.macro_path + net_asset_code[0] +'.csv', 'r') as f:
#            reader = csv.reader(f)
#            LastExtract = list(reader)
#        print(LastExtract)
 
        if (iret != 1):
            print("Bad status", iret, "returned from", net_asset_macro_name, "Error text:", self.iim.iimGetErrorText())
        else:
            LastExtract = LastExtract[0]
            extract_index = -1                                          # Must initialize all variables! JJG 3/31/24
            date_pat = r"(\d{8,14} ?(\d{0,6}))([aApP}mM])?"
            if net_asset_code[1] != -1:
                date = re.search(date_pat, LastExtract[0])
                if date == None:
                    NewDate = Date.get_today_date_time(Date)
                    extract_index = 1
                else:
                    if len(date.group(0)) == 14:
                        InpDate = date.group(0)[:2] + "/"+ date.group(0)[2:4] + "/" + date.group(0)[4:8] + " " + date.group(0)[8:] + date.group(2)
                    InpDate = InpDate.split(" ")                    #InpDate = self.iim.iimGetExtract(1).split(" ")
                    try:
                        month = int(InpDate[0][:2])
                    except:
                        month = self.Month_int(InpDate[0])
                    if len(InpDate) < 4:
                        InpDate = InpDate[0].split("/")         #InpDate = self.iim.iimGetExtract(1).split("/")
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
                    extract_index = 1
            else:
                NewDate = Date.get_today_date_time(Date)
                extract_index = 1
            account_index = 0
            account_negative_flag = net_asset_code[2]
            while True:
                assetName = LastExtract[extract_index]              #assetName = self.iim.iimGetExtract(extract_index)
                extract_index += 1
                asset = AssetsFound.append_by_name(assetName)
                asset.set_type(self.get_asset_type(assetName))
                # if account_negative_flag is set for current index, store the negative of the returned balance. In other words, if balance is negative and flag is set, store positive.  If balance is positive and flag is set, store negative.
                # if account_negatve flag is not set, store balance retrieved
                account_value = round(float(LastExtract[extract_index].replace("$", "").replace(",", "").replace("(","").replace(")","").replace("- ","-")),2)
                if account_negative_flag[account_index] == True:
                    if account_value < 0:
                        asset.set_value(str(-account_value))
                    elif account_value > 0:
                        asset.set_value("-" + str(account_value))
                    else:
                        asset.set_value("0.0")
                else:
                    asset.set_value(str(account_value))
                asset.set_last_pull_date(NewDate)
                account_index += 1
                extract_index += 1
                if extract_index == len(LastExtract):                #self.iim.iimGetExtract(extract_index) == "NODATA":
                    break
        return AssetsFound

    def Finish(self):
        iret = self.iim.iimClose()
        print("Updates Finished, iret = ", iret)
        return iret

if __name__=='__main__':
    w = iMacrosToAsset()
    w.Init()
    net_asset_codes = [
                       ("HFCU",1,[False,False,False,True]),
                       #("NFCU",-1,[False,True]),
                       #("AMEX",-1,[True,True]),
                       #("CITI",-1,[True]),
                       #("SYW",-1,[True]),
                       #("TSP",-1,[False,False,False,True]),
                       #("MET",1,[False])
                       ]
    for net_asset_code in net_asset_codes:
        latest_assets = w.GetNetInfo(net_asset_code)
        print(net_asset_code,": ",latest_assets)
    iret = w.Finish()
    print("All done, iret = ", iret)

