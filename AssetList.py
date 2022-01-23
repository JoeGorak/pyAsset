#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2016-2022 Joseph J. Gorak. All rights reserved.
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

from Asset import Asset
import copy

class AssetList():
    def __init__(self, parent):
        # type: () -> object
        self.parent = parent
        self.assets = []
        self.defaultPaymentAccounts = ['none', 'TBD', 'cash']
        self.numDefaultPaymentAccounts = len(self.defaultPaymentAccounts)

    def __len__(self):
        return len(self.assets)

    def __getitem__(self, i):
        return self.assets[i]

    def __setitem__(self, i, val):
        self.assets[i] = val

    def __str__(self):
        ret_str = ""
        for i in range(len(self.assets)):
            cur_asset = self.assets[i]
            ret_str += "%s: Value (curr) $%.2f Value (proj) $%.2f last pulled %s type %s" % (cur_asset.get_name(), cur_asset.get_value(), cur_asset.get_value_proj(), cur_asset.get_last_pull_date(), cur_asset.get_type())
            limit = cur_asset.get_limit()
            if limit != 0:
                ret_str += " Limit $%.2f Avail (online) $%.2f Avail (proj) $%.2f" % (limit, cur_asset.get_avail(), cur_asset.get_avail_proj())
            rate = cur_asset.get_rate()
            if rate != 0:
                ret_str += " Rate %.3f%%" % (rate*100)
            payment = cur_asset.get_payment()
            if payment != 0:
                ret_str += " Payment $%.2f" % (payment)
            due_date = cur_asset.get_due_date()
            if due_date != None:
                ret_str += " Due date %s" % (due_date)
            sched_date = cur_asset.get_sched_date()
            if sched_date != None:
                ret_str += " Sched date %s" % (sched_date)
            min_pay = cur_asset.get_min_pay()
            if min_pay != 0:
                ret_str += " Min pmt $%.2f" % (min_pay)
            stmt_bal = cur_asset.get_stmt_bal()
            if stmt_bal != 0:
                ret_str += " Stmt Bal $%.2f" % (stmt_bal)
            amt_over = cur_asset.get_amt_over()
            if amt_over != 0:
                ret_str += " Amt Over $%.2f" % (amt_over)
            cash_limit = cur_asset.get_cash_limit()
            if cash_limit != 0:
                ret_str += " Cash Limit $%.2f" % (cash_limit)
            cash_used = cur_asset.get_cash_used()
            if cash_used != 0:
                ret_str += " Cash used $%.2f" % (cash_used)
            cash_avail = cur_asset.get_cash_avail()
            if cash_avail != 0:
                ret_str += " Cash avail $%.2f" % (cash_avail)
            ret_str += "\n"
        return ret_str

    def __delitem__(self, i):
        del self.assets[i]

    def index(self, name):
        ret_index = -1
        for i in range(len(self.assets)):
            if (self.assets[i].get_name() == name):
                ret_index = i
                break
        return ret_index

    def append_by_name(self, name):
        self.assets.append(Asset(name))
        return self.assets[len(self.assets)-1]
 
    def append_by_object(self, asset_in):
        self.assets.append(asset_in)
        return self.assets[len(self.assets)-1]

    def sort(self):
        return self.assets.sort()

    def getPaymentAccounts(self):
        paymentAccts = copy.deepcopy(self.defaultPaymentAccounts)
        for cur_asset in self.assets:
            cur_asset_type = cur_asset.get_type()
            if cur_asset_type in [
                "checking",
                "savings",
                "money market",
                "credit card",
                "store card"
            ]:
                paymentAccts.append(cur_asset.get_name())
        return paymentAccts
