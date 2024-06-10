#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2022-2024 Joseph J. Gorak. All rights reserved.
This code is in development -- use at your own risk. Email
comments, patches, complaints to joe.gorak@gmail.com

This program is free software you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""

#  Version information
#  01/17/2022     Version v1.0

import os
import wx
import copy

from Date import Date
from Asset import SAVINGS, Asset
from AssetList import AssetList
from Date import Date
from Transaction import Transaction
from TransactionList import TransactionList

# Section types
UNKNOWN = -1
ACCOUNT = 0
DETAIL = 1
SPLIT = 2

class qif(object):
    def __init__(self, parent, assetFile="", readmode="normal"):
        self.parent = parent
        self.assets = AssetList(self)
        self.filename = assetFile
        self.edited = False

        if assetFile:
            self.read_qif(assetFile, readmode)

    def read_qif(self, filename, readmode="normal"):
        if readmode == 'normal':  # things not to do on 'import':
            name = filename.replace('.qif', '')
            self.filename = os.path.split(name)[1]
        Found_assets = AssetList(self)
        mffile = open(filename, 'r')
        lines = mffile.readlines()
        mffile.close()
        section = UNKNOWN
        old_section = UNKNOWN
        last_transaction = None
        cur_value = 0.0
        split_text = ""
        split_value = 0.0
        for line in lines:
            input_type, rest = line[0], line[1:].strip().replace(",","")
            if input_type == "!":
                if rest == "Account":
                    section = ACCOUNT
                elif (rest.__contains__("Type")) or (rest.__contains__("Clear:Autoswitch")):
                    section = DETAIL
                    cur_transaction = Transaction(self)
                else:
                    if section == ACCOUNT:
                        section = "account"
                    elif section == DETAIL:
                        section = "detail"
                    else:
                        section = "unknown"
                    print("in", section, "section got unknown ! line: ", line[:-1])                   
            elif input_type == "^":
                if section == DETAIL:
                    if len(Found_assets.assets) == 0:
                        asset_name_parts = self.filename.split('\\')
                        asset_name = asset_name_parts[-1].split('.')[0]
                        cur_asset = Found_assets.get_asset_by_name(asset_name)
                        cur_asset_name = cur_asset.get_name().upper()
                        if cur_asset_name.find("SAVINGS") != -1:
                            cur_asset.set_type("savings")
                        elif cur_asset_name.find("CHECKING") != -1:
                            cur_asset.set_type("checking")
                        elif cur_asset_name.find("DISCOVER") != -1 or cur_asset_name.find("CREDIT CARD") != -1 or cur_asset_name.find("MASTERCARD") != -1 or cur_asset_name.find("AM EX") != -1:
                            cur_asset.set_type("credit card")

                    else:
                        cur_asset.transactions.append(cur_transaction)
                    last_transaction = cur_transaction
                    cur_transaction = Transaction(self)
                elif section == SPLIT:
                    if split_value != split_total:
                        print("in split section value = ", split_value, " and split_total = ", split_total)
                    cur_transaction.set_memo(split_text)
                    section = old_section
                    split_text = ""
                    split_value = 0.0
                    cur_asset.transactions.append(cur_transaction)
                    last_transaction = cur_transaction
                    cur_transaction = Transaction(self)
            elif input_type == "C":
                if section == DETAIL:
                    if rest == "*" or rest == "C":
                        cur_transaction.set_state("cleared")
                    elif rest == "X" or rest == "R":
                        cur_transaction.set_state("reconciled")
                    else:
                        cur_transaction.set_state("unknown")
            elif input_type == "D":
                if section == DETAIL:
                    formatted_date = Date.parse_date(Date, rest, "%m/%d/%y")
                    formatted_date['month'] = formatted_date['month'] - 1
                    cur_transaction.set_due_date(formatted_date)
            elif input_type == "E":
                if section == SPLIT:
                    if split_text == "":
                        split_text = copy.deepcopy(rest)
                    else:
                        split_text += " " + rest
            elif input_type == "L":
                if section == ACCOUNT:
                    cur_asset.set_limit(rest)
                elif section == DETAIL:
                    if last_transaction == None:                    # JJG 1/21/2024 Special handling of first L line to support Quicken qif exported files
                        asset_name_parts = filename.split('\\')
                        asset_name = asset_name_parts[-1].split('.')[0]
                        cur_asset = Found_assets.get_asset_by_name(asset_name)
                        cur_asset_name = cur_asset.get_name().upper()
                        if cur_asset_name.find("SAVINGS") != -1:
                            cur_asset.set_type("savings")
                        elif cur_asset_name.find("CHECKING") != -1:
                            cur_asset.set_type("checking")
                        elif cur_asset_name.find("DISCOVER") != -1 or cur_asset_name.find("CREDIT CARD") != -1 or cur_asset_name.find("MASTERCARD") != -1 or cur_asset_name.find("AM EX") != -1:
                            cur_asset.set_type("credit card")
                    cur_transaction.set_memo(rest)
            elif input_type == "M":
                if section == ACCOUNT:
                    cur_asset.set_memo(rest)
            elif input_type == "N":
                if section == ACCOUNT:
                    cur_asset = Found_assets.get_asset_by_name(rest)
                elif section == DETAIL:
                    cur_transaction.set_check_num(rest)
            elif input_type == "P" or input_type == "M":                # JJG 1/22/2022  Seems some use M lines incorrectly (payee vice a strict memo)! 1/21/2024 merge vice simply copy latest stuff!
                if section == DETAIL:
                    payee = cur_transaction.get_payee()
                    if payee == None:
                        payee = rest
                    else:
                        payee += " " + rest
                    cur_transaction.set_payee(payee)
            elif input_type == "S":
                if section != SPLIT:
                    split_total = cur_transaction.get_amount()
                    old_section = section
                section = SPLIT
                if split_text == "":
                    split_text = rest
                else:
                    split_text += " " + rest
            elif input_type == "T":
                type = line[1:].strip()
                if section == ACCOUNT:
                    cur_asset_name = cur_asset.get_name().upper()
                    if type == "Bank":
                        cur_asset_name = cur_asset.get_name().upper()
                        if cur_asset.name.find("SAVINGS") != -1:
                            cur_asset.set_type("Savings")
                        elif cur_asset.name.find("CHECKING") != -1:
                            cur_asset.set_type("Checking")
                    elif type == "CCard":
                        cur_asset.set_type("Credit card")
                elif section == DETAIL or section == SPLIT:
                    cur_transaction.set_amount(rest)
                    if section == SPLIT:
                        split_total = round(float(rest), 2)
            elif input_type == "U":
                if section == DETAIL:
                    cur_transaction.set_amount(rest)
                    if last_transaction == None:
                        cur_transaction.set_current_value(rest)
                    else:
                        amount = cur_transaction.get_amount()
                        type = cur_asset.get_type()
                        if type == "checking" or type == "savings":
                            if amount < 0:
                                amount = -amount
                                cur_transaction.set_action('-')
                            else:
                                cur_transaction.set_action('+')
                        elif type == "credit card":
                            cur_transaction.set_action('+')
                        last_value = last_transaction.get_current_value()
                        if cur_transaction.get_action() == '+':
                            cur_value = last_value + amount
                        else:
                            cur_value = last_value - amount
                        cur_transaction.set_current_value(cur_value)
            elif input_type == "$" or input_type == "%":
                if section == SPLIT:
                    split_text += " " + rest
                    if input_type == "%":
                        split_text += "%"
                    cur_split_value = round(float(rest), 2)
                    if input_type == "%":
                        cur_split_value = split_total * cur_split_value / 100.00
                    split_value += cur_split_value
            else:
                if section == ACCOUNT:
                    section = "account"
                elif section == DETAIL:
                    section = "detail"
                elif section == SPLIT:
                    section = "split"
                else:
                    section = "unknown"
                print("in", section, "section got unparsable line: ", line[:-1])
        return Found_assets

    def write_qif(self, filename, function, lines):
        filelines = '\n'.join(lines)
        with open(filename, 'a') as file:
            file.writelines("%s" % filelines)
        Found_assets = self.assets.assets
        for asset in Found_assets:
            if function == 'writeAccountHeaders':
                asset.write_qif(filename)
            elif function == 'writeAccountDetails':
                lines = []
                lines.append("N%s\m" % asset.get_name())
                for transaction in asset.transactions.transactions:
                    lines.append(transaction.qif_repr())
                lines.append("^\n")
                filelines = '\n'.join(lines)
                with open(filename, 'a') as file:
                    file.writelines("%s" % filelines)

        return True

    def save_as_file(self):
        self.filename = None
        d = wx.FileDialog(self, "Save", "", "", "*.qif", wx.FD_SAVE)
        if d.ShowModal() == wx.ID_OK:
            fname = d.GetFilename()
            dir = d.GetDirectory()
            self.filename = os.path.join(dir, fname)
            self.write_qif(self.filename)
        if self.filename:
            self.SetTitle("PyAsset: %s" % self.filename)

    def load_file(self, assetFile):
        if assetFile != "" and self.edited:
            d = wx.MessageDialog(self, 'Save file before loading new file?', 'Question',
                                 wx.YES_NO)
            if d.ShowModal() == wx.ID_YES:
                qif.write_qif(self, self.filename)
                assetFile = ""
#        self.clear_all_assets()
        if assetFile != "":
            self.SetTitle("PyAsset: %s" % self.filename)
            return qif.read_qif(self, self.filename)
        else:
            d = wx.FileDialog(self, "Save", "", "", "*.qif", wx.FD_SAVE)
            if d.ShowModal() == wx.ID_OK:
                fname = d.GetFilename()
                dir = d.GetDirectory()
                self.filename = os.path.join(dir, fname)
                self.SetTitle("PyAsset: %s" % self.filename)
                return qif.read_qif(self, self.filename)
            else:
                return None
