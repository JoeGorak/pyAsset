#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2016-2020 Joseph J. Gorak. All rights reserved.
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

import os
import wx
from Date import Date
from Transaction import Transaction

# Asset Types
CHECKING = 0
SAVINGS = 1
MONEY_MARKET = 2
OVERDRAFT = 3
CREDIT_CARD = 4
STORE_CARD = 5
RETIREMENT = 6
LOAN = 7
MORTGAGE = 8
OTHER = 9

from TransactionList import TransactionList
from Transaction import Transaction

class Asset(object):
    def __init__(self,name = "", type = "OTHER", last_pull_date = 0, value = 0.0, value_proj = 0.0, est_method = "", limit = 0.0, avail = 0.0, avail_proj = 0.0, rate = 0.0,
                payment = 0.0, due_date = None, sched_date = None, min_pay = 0.0, stmt_bal = 0.0, amt_over = 0.0, cash_limit = 0.0, cash_used = 0.0, cash_avail = 0.0):
        self.dateFormat = Date.get_global_date_format(self)
        self.dateSep = Date.get_global_date_sep(self)
        self.name = name
        if name != "":
            self.filename = self.name + ".qif"
        self.set_type(type)
        self.last_pull_date = last_pull_date
        self.limit = limit
        self.avail = avail
        self.avail_proj = avail_proj
        self.rate = rate
        self.payment = payment
        self.due_date = due_date
        self.sched_date = sched_date
        self.min_pay = min_pay
        self.value = value
        self.value_proj = value_proj
        self.est_method = est_method
        self.amt_over = amt_over
        self.stmt_bal = stmt_bal
        self.cash_limit = cash_limit
        self.cash_used = cash_used
        self.cash_avail = cash_avail
        self.transactions = TransactionList(self, limit)
        return

    def __len__(self):
        return len(self.transactions)

    def __getitem__(self, i):
        return self.transactions[i]

    def __setitem__(self, i, val):
        self.transactions[i] = val

    def __str__(self):
        return " %-10s $%8.2f\n" % (self.name, self.value)

    def __gt__(self, other):
        if self.due_date != None and other.due_date != None:
            return self.due_date > other.due_date
        elif self.due_date != None:
            return False
        else:
            return True

    def __lt__(self, other):
        if self.due_date != None and other.due_date != None:
            return self.due_date < other.due_date
        elif self.due_date != None:
            return False
        else:
            return True

    def sort(self):
        self.transactions.sort()

    def write_qif(self, filename=None):
        if not filename:
            if not self.filename: raise Exception("No Asset filename defined")
            filename = self.filename
        self.filename = filename
        file = open(filename, 'w')
        file.write("%s" % self.qif_repr())
        file.close()
        return

    def write_txt(self, filename='pyasset.txt'):
        file = open(filename, 'w')
        file.write("%s" % self.text_repr())
        file.close()
        return

    def text_repr(self):
        lines = []
        for transaction in self.transactions: lines.append(str(transaction))
        return '\n'.join(lines)

    def qif_repr(self):
        lines = ['Type:Bank']
        for transaction in self.transactions: lines.append(transaction.qif_repr())
        lines.append('')
        return '\n'.join(lines)

    def get_name(self):
        return self.name

    def set_name(self,name):
        self.name = name

    def get_value(self):
        return self.value

    def set_value(self, value):
        try:
            self.value = round(float(value), 2)
        except:
            self.value = 0.0

    def get_last_pull_date(self):
        return self.last_pull_date

    def set_value_proj(self, value_proj):
        try:
            self.value_proj = round(float(value_proj), 2)
        except:
            self.value_proj = 0.0

    def get_value_proj(self):
        return self.value_proj

    def set_est_method(self, est_method):
        self.est_method = est_method

    def get_est_method(self):
        return self.est_method

    def set_last_pull_date(self, last_pull_date):
        if last_pull_date != 0:
            self.last_pull_date = str(last_pull_date).split(".")[0]

    def get_limit(self):
        return self.limit

    def set_limit(self, limit):
        try:
            self.limit = round(float(limit), 2)
        except:
            self.limit = 0.0

    def get_avail(self):
        return self.avail

    def set_avail(self, avail):
        try:
            self.avail = round(float(avail), 2)
        except:
            self.avail = 0.0

    def get_avail_proj(self):
        return self.avail_proj

    def set_avail_proj(self, avail_proj):
        try:
            self.avail_proj = round(float(avail_proj), 2)
        except:
            self.avail_proj = 0.0

    def get_rate(self):
        return self.rate

    def set_rate(self, rate):
        try:
            self.rate = round(float(rate), 3)
        except:
            self.rate = 0.0

    def get_payment(self):
        return self.payment

    def set_payment(self, payment):
        try:
            self.payment = round(float(payment), 2)
        except:
            self.payment = 0.0

    def get_due_date(self):
        return self.due_date

    def set_due_date(self, rest):
        if rest != None:
            if type(rest) is str:
                if len(rest) != 0:
                    [year, month, day] = Date.get_date_fields(self,rest)
                    self.due_date = wx.DateTime.FromDMY(day, month-1, year).Format(self.dateFormat)
                else:
                    self.due_date = None
            else:
                self.due_date = wx.DateTime.FromDMY(rest.day, rest.month-1, rest.year).Format(self.dateFormat)

    def get_sched_date(self):
        return self.sched_date

    def set_sched_date(self, rest):
        if rest != None:
            if type(rest) is str:
                if len(rest) != 0:
                    [year, month, day] = Date.get_date_fields(self, rest)
                    self.sched_date = wx.DateTime.FromDMY(day, month-1, year).Format(self.dateFormat)
                else:
                    self.sched_date = None
            else:
                self.sched_date = wx.DateTime.FromDMY(rest.day, rest.month-1, rest.year).Format(self.dateFormat)

    def get_min_pay(self):
        return self.min_pay

    def set_min_pay(self, min_pay):
        try:
            self.min_pay = round(float(min_pay), 2)
        except:
            self.min_pay = 0.0

    def get_type(self):
        st = self.type
        if st == CHECKING:
            return "checking"
        elif st == SAVINGS:
            return "savings"
        elif st == MONEY_MARKET:
            return "money market"
        elif st == OVERDRAFT:
            return "overdraft"
        elif st == CREDIT_CARD:
            return "credit card"
        elif st == STORE_CARD:
            return "store card"
        elif st == RETIREMENT:
            return "retirement"
        elif st == MORTGAGE:
            return "mortgage"
        elif st == LOAN:
            return "loan"
        elif st == OTHER:
            return "other"
        else:
            return "unknown type"

    def set_type(self, type):
        tu = type.upper()
        if "CHECKING" in tu:
            self.type = CHECKING
        elif "SAVINGS" in tu:
            self.type = SAVINGS
        elif "MONEY MARKET" in tu:
            self.type = MONEY_MARKET
        elif "OVERDRAFT" in tu:
            self.type = OVERDRAFT
        elif "STORE CARD" in tu:
            self.type = STORE_CARD
        elif "CREDIT CARD" in tu:
            self.type = CREDIT_CARD
        elif "RETIREMENT" in tu:
            self.type = RETIREMENT
        elif "MORTGAGE" in tu:
            self.type = MORTGAGE
        elif "LOAN" in tu:
            self.type = LOAN
        else:
            self.type = OTHER

    def get_stmt_bal(self):
        return self.stmt_bal

    def set_stmt_bal(self, stmt_bal):
        try:
            self.stmt_bal = round(float(stmt_bal), 2)
        except:
            self.stmt_bal = 0.0

    def get_amt_over(self):
        return self.amt_over

    def set_amt_over(self, amt_over):
        try:
            self.amt_over = round(float(amt_over), 2)
        except:
            self.amt_ovet = 0.0

    def get_cash_limit(self):
        return self.cash_limit

    def set_cash_limit(self, cash_limit):
        try:
            self.cash_limit = round(float(cash_limit), 2)
        except:
            self.cash_limit = 0.0

    def get_cash_used(self):
        return self.cash_used

    def set_cash_used(self, cash_used):
        try:
            self.cash_used = round(float(cash_used), 2)
        except:
            self.cash_used = 0.0

    def get_cash_avail(self):
        return self.cash_avail

    def set_cash_avail(self, cash_avail):
        try:
            self.cash_avail = round(float(cash_avail), 2)
        except:
            self.cash_avail = 0.0

def getNumAssetColumns():
    tempAsset = Asset(None)
    return tempAsset.__sizeof__()

