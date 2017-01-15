#!/usr/bin/env /usr/local/bin/pythonw
"""

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
#  6/11/2016     Initial version v0.1

import os
from Transaction import Transaction

# Asset Types
CHECKING = 0
SAVINGS = 1
MONEY_MARKET = 2
OVERDRAFT = 3
CREDIT_CARD = 4
STORE_CARD = 5
RETIREMENT = 6
MORTGAGE = 7
OTHER = 8

class Asset:
    def __init__(self, name, filename=None, type = "OTHER", last_pull_date = 0, total = 0.0, value_proj = 0.0, limit = 0.0, avail = 0.0, avail_proj = 0.0, rate = 0.0,
                 payment = 0.0, due_date = 0, sched = 0, min_pay = 0.0, stmt_bal = 0.0, cash_limit = 0.0, cash_used = 0.0, cash_avail = 0.0):
        self.name = name
        self.filename = filename
        self.type = self.set_type(type)
        self.transactions = []
        self.last_pull_date = last_pull_date
        self.limit = limit
        self.avail = avail
        self.avail_proj = avail_proj
        self.rate = rate
        self.payment = payment
        self.due_date = due_date
        self.sched = sched
        self.min_pay = min_pay
        self.total = total
        self.value_proj = value_proj
        self.amt_over = 0.0
        self.stmt_bal = stmt_bal
        self.cash_limit = cash_limit
        self.cash_used = cash_used
        self.cash_avail = cash_avail

        if (filename is not None):
            self.read_qif(filename)
        return

    def __len__(self):
        return len(self.transactions)

    def __getitem__(self, i):
        return self.transactions[i]

    def __setitem__(self, i, val):
        self.transactions[i] = val

    def __str__(self):
        return " %-10s $%8.2f\n" % (self.name, self.total)

    def __delitem__(self, i):
        del self.transactions[i]

    def append(self, item):
        self.transactions.append(item)

    def read_qif(self, filename, readmode='normal'):
        if readmode == 'normal':  # things not to do on 'import':
            self.filename = filename
            name = filename.replace('.qif', '')
            self.name = os.path.split(name)[1]
        mffile = open(filename, 'r')
        lines = mffile.readlines()
        mffile.close()
        transaction = Transaction()
        input_type = lines.pop(0)
        for line in lines:
            input_type, rest = line[0], line[1:].strip()
            if input_type == "D":
                transaction.setdate(rest)
                blank_transaction = False
            elif input_type == "T":
                transaction.setamount(rest)
                blank_transaction = False
            elif input_type == "P":
                transaction.setpayee(rest)
                blank_transaction = False
            elif input_type == "C":
                transaction.setcleared(rest)
                blank_transaction = False
            elif input_type == "N":
                transaction.setnumber(rest)
                blank_transaction = False
            elif input_type == "L":
                transaction.setcomment(rest)
                blank_transaction = False
            elif input_type == "M":
                transaction.setmemo(rest)
                blank_transaction = False
            elif input_type == "A":
                total_payee = transaction.getpayee() + " " + rest
                transaction.setpayee(total_payee)
                blank_transaction = False
            elif input_type == "^":
                if not blank_transaction:
                    self.transactions.append(transaction)
                    self.total = self.total + transaction.getamount()
                    transaction = Transaction()
                blank_transaction = True
            else:
                print "Unparsable line: ", line[:-1]
        self.sort()
        return

    def sort(self):
        self.transactions.sort()

    def write_qif(self, filename=None):
        if not filename:
            if not self.filename: raise "No Asset filename defined"
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

    def get_total(self):
        return self.total

    def set_total(self, total):
        self.total = total

    def get_last_pull_date(self):
        return self.last_pull_date

    def set_value_proj(self, value_proj):
        self.value_proj = value_proj

    def get_value_proj(self):
        return self.value_proj

    def set_last_pull_date(self, last_pull_date):
        if last_pull_date != 0:
            self.last_pull_date = str(last_pull_date).split(".")[0]

    def get_limit(self):
        return self.limit

    def set_limit(self, limit):
        self.limit = limit

    def get_avail(self):
        return self.avail

    def set_avail_proj(self, avail_proj):
        self.avail_proj = avail_proj

    def get_avail_proj(self):
        return self.avail_proj

    def set_avail(self, avail):
        self.avail = avail

    def get_rate(self):
        return self.rate

    def set_rate(self, rate):
        self.rate = rate

    def get_payment(self):
        return self.payment

    def set_payment(self, payment):
        self.payment = payment

    def get_due_date(self):
        return self.due_date

    def set_due_date(self, due_date):
        if due_date != 0:
            self.due_date = str(due_date).split(" ")[0]

    def get_sched(self):
        return self.sched

    def set_sched(self, sched):
        if sched != 0:
            self.sched = str(sched).split(" ")[0]

    def get_min_pay(self):
        return self.min_pay

    def set_min_pay(self, min_pay):
        self.min_pay = min_pay

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
        elif st == OTHER:
            return "other"
        else:
            return "unknown type"

    def set_type(self, type):
        tu = type.upper()
        if tu == "CHECKING":
            self.type = CHECKING
        elif tu == "SAVINGS":
            self.type = SAVINGS
        elif tu == "MONEY MARKET":
            self.type = MONEY_MARKET
        elif tu == "OVERDRAFT":
            self.type = OVERDRAFT
        elif tu == "CREDIT CARD":
            self.type = CREDIT_CARD
        elif tu == "STORE CARD":
            self.type = STORE_CARD
        elif tu == "RETIREMENT":
            self.type = RETIREMENT
        elif tu == "OTHER":
            self.type = OTHER
        else:
            self.type = OTHER

    def get_stmt_bal(self):
        return self.stmt_bal

    def set_stmt_bal(self, stmt_bal):
        self.stmt_bal = stmt_bal

    def get_amt_over(self):
        return self.amt_over

    def set_amt_over(self, amt_over):
        self.amt_over = amt_over

    def get_cash_limit(self):
        return self.cash_limit

    def set_cash_limit(self, cash_limit):
        self.cash_limit = cash_limit

    def get_cash_used(self):
        return self.cash_used

    def set_cash_used(self, cash_used):
        self.cash_used = cash_used

    def get_cash_avail(self):
        return self.cash_avail

    def set_cash_avail(self, cash_avail):
        self.cash_avail = cash_avail
