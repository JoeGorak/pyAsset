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
            input_type, rest = line[0], line[1:].strip().replace(",","")
            if input_type == "!":
                if rest == "Account":
                    section = ACCOUNT
                else:
                    section = DETAIL
                    cur_transaction = Transaction(self)
            elif input_type == "^":
                if section == DETAIL:
                    cur_asset.transactions.append(cur_transaction)
                    cur_transaction = Transaction(self)
            elif input_type == "L":
                if section == ACCOUNT:
                    cur_asset.set_limit(rest)
            elif input_type == "N":
                if section == ACCOUNT:
                    cur_asset = Found_assets.append_by_name(rest)
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
        print("In writing ", filename, " as .qif file. Found_assets = ", Found_assets)
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
        if self.edited:
            d = wx.MessageDialog(self, 'Save file before loading new file?', 'Question',
                                 wx.YES_NO)
            if d.ShowModal() == wx.ID_YES:
                qif.write_qif(self, self.filename)
                assetFile = ""
        self.clear_all_assets()
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
