#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2022 Joseph J. Gorak. All rights reserved.
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

class qif(object):
    def __init__(self, parent, assetFile="", readmode="normal"):
        self.parent = parent
        self.assets = AssetList(self)
        self.filename = assetFile
        self.edited = False

        DateFormat = Date.get_global_date_format(self)

        if assetFile:
            self.read_qif(assetFile, readmode)
        else:
            error = assetFile + ' does not exist / cannot be opened!! - Aborting\n'
            self.DisplayMsg(error)

    def read_qif(self, filename, readmode="normal"):
        if readmode == 'normal':  # things not to do on 'import':
            name = filename.replace('.qif', '')
            self.filename = os.path.split(name)[1]
        Found_assets = AssetList(self)
        mffile = open(filename, 'r')
        lines = mffile.readlines()
        mffile.close()
        section = UNKNOWN
        for line in lines:
            input_type, rest = line[0], line[1:].strip()
            if input_type == "!":
                if rest == "Account":
                    section = ACCOUNT
                    cur_asset = Found_assets.append(name)
                else:
                    section = DETAIL
                    cur_transaction = Transaction(self)
            elif input_type == "^":
                if section == ACCOUNT:
                    print(cur_asset)
                    print(Found_assets)
                elif section == DETAIL:
                    cur_asset.transactions.append(cur_transaction)
                    cur_transaction = Transaction(self)
            elif input_type == "N":
                if section == ACCOUNT:
                    cur_asset.set_name(rest)
                elif section == DETAIL:
                    cur_transaction.set_check_num(rest)
            elif input_type == "T":
                kind = line[1:].strip()
                if section == ACCOUNT:
                    if kind == "Bank":
                        if cur_asset.get_name().upper().find("SAVINGS") != -1:
                            cur_asset.set_type("Savings")
                        elif cur_asset.get_name().upper().find("CHECKING") != -1:
                            cur_asset.set_type("Checking")
                    elif kind == "CCard":
                        cur_asset.set_type("Credit card")
                elif section == DETAIL:
                    cur_transaction.set_amount(rest)
            elif input_type == "U":
                if section == DETAIL:
                    cur_transaction.set_amount(rest)
            else:
                print("Unparsable line: ", line[:-1])
            pass
        return Found_assets

    def write_qif(self, filename):
        Found_assets = AssetList(self)
        # Write and process Assets and Transactions here!   JJG 1/17/2022
        return Found_assets

    def read_transaction_qif(self, filename):
        mffile = open(filename, 'r')
        lines = mffile.readlines()
        mffile.close()
        transaction = self.cur_asset.transactions;
        blank_transaction = True
        input_type = lines.pop(0)
        for line in lines:
            input_type, rest = line[0], line[1:].strip()
            if input_type == "D":
                transaction.set_due_date(rest)
                blank_transaction = False
            elif input_type == "T" or input_type == "U":
                transaction.set_amount(rest)
                blank_transaction = False
            elif input_type == "P":
                transaction.set_payee(rest)
                blank_transaction = False
            elif input_type == "C":
                transaction.set_state(rest)
                blank_transaction = False
            elif input_type == "N":
                transaction.set_check_num(rest)
                blank_transaction = False
            elif input_type == "L":
                transaction.set_comment(rest)
                blank_transaction = False
            elif input_type == "M":
                transaction.set_memo(rest)
                blank_transaction = False
            elif input_type == "A":
                total_payee = transaction.get_payee() + " " + rest
                transaction.set_payee(total_payee)
                blank_transaction = False
            elif input_type == "^":
                if not blank_transaction:
                    self.transactions.append(transaction)                   # JJG 08/22/2021 Not sure what this is doing????
                    #self.value = self.value + transaction.get_amount()
                    #transaction = Transaction(self.parent)
            else:
                print("Unparsable line: ", line[:-1])
        self.sort()
        return self.assets

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
        if self.edited:
            d = wx.MessageDialog(self, 'Save file before loading new file?', 'Question',
                                 wx.YES_NO)
            if d.ShowModal() == wx.ID_YES:
                qif.write_qif(self)
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
