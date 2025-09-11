#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2016-2025 Joseph J. Gorak. All rights reserved.
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

#  Version information
#  06/11/2016     Initial version v0.1
#  08/07/2021     Version v0.2
#  05/25/2024     Version v0.5      Added more support for .qif files

import os
import wx
from Date import Date
from Transaction import Transaction

# Asset Types
CASH = 0
CHECKING = 1
SAVINGS = 2
MONEY_MARKET = 3
OVERDRAFT = 4
CREDIT_CARD = 5
STORE_CARD = 6
RETIREMENT = 7
LOAN = 8
MORTGAGE = 9
CD = 10
HOUSE = 11
CAR = 12
OTHER = 13

from TransactionList import TransactionList
from Transaction import Transaction

class Asset(object):
    def __init__(self,name = "", type = "OTHER", last_pull_date = 0, value = 0.0, value_proj = 0.0, est_method = "", limit = 0.0, avail = 0.0, avail_proj = 0.0, rate = 0.0,
                payment = 0.0, due_date = None, sched_date = None, min_pay = 0.0, stmt_bal = 0.0, amt_over = 0.0, cash_limit = 0.0, cash_used = 0.0, cash_avail = 0.0):
        self.dateFormat = Date.get_global_date_format(Date)
        self.dateSep = Date.get_global_date_sep(Date)
        self.name = name
        self.filename = name
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
        self.transactions = TransactionList(self, limit=limit)

    def get_assetList(self):
        try:
            assetList = self.assetList
        except:
            assetList = None

    def set_assetList(self, assetList):
        self.assetList = assetList

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
            return self.due_date['dt'] > other.due_date['dt']
        elif self.due_date != None:
            return False
        else:
            return True

    def __lt__(self, other):
        if self.due_date != None and other.due_date != None:
            return self.due_date['dt'] < other.due_date['dt']
        elif self.due_date != None:
            return False
        else:
            return True

    def sort(self):
        self.transactions.sort()

    def write_qif(self, filename):
        if filename != None:
            self.filename = filename
            with open(filename, 'a') as file:
                arep = self.qif_repr()
                file.writelines("%s" % arep)

    def write_txt(self, filename=None):
        if filename != None:
            with open(filename, 'a') as file:
                trep = self.text_repr()
                file.writelines("%s" % trep)

    def text_repr(self):
        lines = []
        for transaction in self.transactions: lines.append(str(transaction))
        return '\n'.join(lines)

    def qif_repr(self):
        lines = []
        lines.append("N%s" % self.get_name())
        lines.append("T%s" % self.get_type())
        lines.append("$%s" % self.get_value())
        lines.append("L%s" % self.get_limit())
        memo_line = ""
        last_pull_date = self.get_last_pull_date()
        if last_pull_date != None:
            memo_line += "P%s" % (last_pull_date)
        avail = self.get_avail()
        if avail != 0.0:
            if memo_line != "":
                memo_line += ";"
            memo_line += "A%s" % (str(avail))
        rate = self.get_rate()
        if rate != 0.0:
            if memo_line != "":
                memo_line += ";"
            memo_line += "R%s" % (str(rate))
        payment = self.get_payment()
        if payment != 0.0:
            if memo_line != "":
                memo_line += ";"
            memo_line += "Y%s" % (str(payment))
        due_date = self.get_due_date()
        if due_date != None:
            if type(due_date) is not str:
                due_date = due_date["str"]
            if due_date != "":
                if memo_line != "":
                    memo_line += ";"
                memo_line += "D%s" % (due_date)
        sched_date = self.get_sched_date()
        if sched_date != None:
            if type(sched_date) is not str:
                sched_date = sched_date["str"]
            if sched_date != "":
                if memo_line != "":
                    memo_line += ";"
                memo_line += "S%s" % (sched_date)
        min_pay = self.get_min_pay()
        if min_pay != 0.0:
            if memo_line != "":
                memo_line += ";"
            memo_line += "M%s" % (str(min_pay))
        est_method = self.get_est_method()
        if est_method != None:
            if memo_line != "":
                memo_line += ";"
            memo_line += "E%s" % (est_method)
        amt_over = self.get_amt_over()
        if amt_over != 0.0:
            if memo_line != "":
                memo_line += ";"
            memo_line += "O%s" % (str(amt_over))
        stmt_bal = self.get_stmt_bal()
        if stmt_bal != 0.0:
            if memo_line != "":
                memo_line += ";"
            memo_line += "B%s" % (str(stmt_bal))
        cash_limit = self.get_cash_limit()
        if cash_limit != 0.0:
            if memo_line != "":
                memo_line += ";"
            memo_line += "C%s" % (str(cash_limit))
        cash_used = self.get_cash_used()
        if cash_used != 0.0:
            if memo_line != "":
                memo_line += ";"
            memo_line += "C%s" % (str(cash_used))
        if memo_line != "":
            lines.append("M%s" % memo_line)         # Use Memo field for parsable string of info for this asset
        lines.append("^\n")
        return '\n'.join(lines)

    def get_transactions(self):
        return self.transactions.transactions

    def transaction_exists(self,payee,date):
        return self.transactions.index(payee, date) != -1

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
        if last_pull_date != None:
            if type(last_pull_date) is str:
                dateTimeParts = last_pull_date.split(" ")
                date = dateTimeParts[0]
#                dateFormat = Date.guessDateFormat(Date, date)
                dateFields = Date.get_date_fields(self, date)
                year = dateFields[0]
                month = dateFields[1]
                day = dateFields[2]
                [hour, min, sec] = dateTimeParts[1].split(":")
            else:
                try:
                    month = last_pull_date["dt"].month+1
                    day = last_pull_date["dt"].day
                    year = last_pull_date["dt"].year
                    hour = last_pull_date["dt"].hour
                    min = last_pull_date["dt"].minute
                    sec = last_pull_date["dt"].second
                except:
                    month = last_pull_date.month
                    day = last_pull_date.day
                    year = last_pull_date.year
                    hour = last_pull_date.hour
                    min = last_pull_date.minute
                    sec = last_pull_date.second
            time = "%02d:%02d:%02d" % (int(hour), int(min), int(sec))
            last_pull_date = wx.DateTime.FromDMY(day, month-1, year).Format(Date.get_global_date_format(Date))
            last_pull_date = last_pull_date + " " + time
        self.last_pull_date = last_pull_date

    def get_last_pull_date(self):
        return self.last_pull_date

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
            self.due_date = Date.parse_date(self, rest, self.dateFormat)
        else:
            self.due_date = None

    def get_sched_date(self):
        return self.sched_date

    def set_sched_date(self, rest):
        if rest != None:
            self.sched_date = Date.parse_date(self, rest, self.dateFormat)
        else:
            self.sched_date = None

    def get_min_pay(self):
        return self.min_pay

    def set_min_pay(self, min_pay):
        try:
            self.min_pay = round(float(min_pay), 2)
        except:
            self.min_pay = 0.0

    def get_type(self):                 # JJG 2/11/24 Modified to retun qif codes for assets
        st = self.type
        if st == CASH: return "Cash"
        elif st == CHECKING or st == SAVINGS or st == MONEY_MARKET: return "Bank"
        elif st == CREDIT_CARD or st == STORE_CARD: return "CCard"
        elif st == CD or st == RETIREMENT: return "Invst"
        elif st == HOUSE or st == CAR: return "Oth A"
        elif st == OVERDRAFT or st == LOAN or st == MORTGAGE: return "Oth L"
        elif st == OTHER: return "OTH U"                # JJG 2/11/24 Addition to qif codes
        else: return "UNK"                              # JJG 2/11/24 Also addition to qif codes (should not occur if code is working properly!!)

    def set_type(self, type):
        tu = type.upper()
        if "CASH" in tu: self.type = CASH
        elif "CHECKING" in tu: self.type = CHECKING
        elif "SAVINGS" in tu: self.type = SAVINGS
        elif "MONEY MARKET" in tu: self.type = MONEY_MARKET
        elif "OVERDRAFT" in tu: self.type = OVERDRAFT
        elif "STORE CARD" in tu: self.type = STORE_CARD
        elif "CREDIT CARD" in tu: self.type = CREDIT_CARD
        elif "RETIREMENT" in tu: self.type = RETIREMENT
        elif "MORTGAGE" in tu: self.type = MORTGAGE
        elif "LOAN" in tu: self.type = LOAN
        elif "CD" in tu: self.type = CD
        elif "HOUSE" in tu: self.type = HOUSE
        elif "CAR" in tu: self.type = CAR
        else: self.type = OTHER

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

