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

import wx
from Date import Date
from datetime import date, datetime

# Bill types
CHECKINGANDSAVINGS = 0
CREDITCARD = 1
LOAN = 2
OVERDRAFT = 3
EXPENSE = 4
UNKNOWN = 5

# Payment Methods
DIRECT_DEPOSIT = 1
SCHED_ONLINE = 2
CHECK = 3
AUTOPAY = 4
CASH = 5
TBD = 6
MANUAL = 7
OTHER = 8

# Payment_Frequency
BIWEEKLY = 0
MONTHLY = 1
QUARTERLY = 3
SEMI_YEARLY = 6
YEARLY = 12
MANUAL = -1

class Bill:
    bill_types = [ "Checking and Savings", "Credit Card", "Loan", "Expense", "Unknown" ]
    payment_methods = [ "Direct deposit", "sched online", "Check", "AutoPay", "Cash", "TBD", "Manual", "Other" ]
    payment_frequencies = [ "Bi-weekly", "monthly", "quarterly", "semi-yearly", "yearly", "manual" ]

    inc_values = ["2 weeks", "1 month", "3 months", "6 months", "1 year", ""]

    def get_bill_inc_value(payment_freq):
        which = Bill.payment_frequencies.index(payment_freq)
        if which == -1:
            return None
        else:
            return Bill.inc_values[which]

    def get_bill_types():
        return Bill.bill_types

    def get_payment_methods():
        return Bill.payment_methods

    def get_payment_frequencies():
        return Bill.payment_frequencies

    def __init__(self, payee=None, type="Unknown", action="-", amount=0.0, min_due=0.0, due_date=None, sched_date=None,
                 pmt_acct="Other", pmt_method="TBD", check_number=0, pmt_freq="Manual" ):
        self.set_payee(payee)
        self.set_type(type)
        self.set_action(action)
        self.set_amount(amount)
        self.set_min_due(min_due)
        self.set_due_date(due_date)
        self.set_sched_date(sched_date)
        self.set_pmt_acct(pmt_acct)
        self.set_pmt_method(pmt_method)
        self.set_pmt_frequency(pmt_freq)
        self.set_check_number(check_number)

    bill_fields = [ "Payee", "Type", "Amount", "Min Due", "Due Date", "Sched Date", "Pmt Acct", "Pmt Method", "Pmt Freq", "Check Number" ]

    def get_bill_fields():
        return Bill.bill_fields

    def __str__(self):
        return '\"%-10s","%-30s","$%8.2f","$%8.2f","%10s","%10s","%s","%s","%s"' %\
               (self.get_payee(), self.get_type(), self.get_amount(), self.get_min_due(), self.get_due_date(), self.get_sched_date(), self.get_pmt_acct(), self.get_pmt_method(), self.get_pmt_frequency())

    def write_qif(self, qif_file):
        with open(qif_file, 'a') as f:
            f.write(str(self))

    def empty(self):
        return self.get_payee() == None or self.get_pmt_frequency() == None

    def get_check_number(self):
        return self.check_number

    def set_check_number(self, check_number):
        self.check_number = check_number

    def set_action(self, action):
        self.action = action

    def get_action(self):
        return self.action

    def get_payee(self):
        return self.payee

    def get_type(self):
        st = self.type
        if st == CHECKINGANDSAVINGS:
            return "Checking and savings"
        elif st == CREDITCARD:
            return "Credit Card"
        elif st == LOAN:
            return "Loan"
        elif st == EXPENSE:
            return "Expense"
        elif st == UNKNOWN:
            return "Unknown"
        else:
            return ""

    def set_type(self,type):
        tu = type.upper().strip()
        if "CHECKING AND SAVINGS" in tu:
            self.type = CHECKINGANDSAVINGS
        elif "CREDIT CARD" in tu:
            self.type = CREDITCARD
        elif "LOAN" in tu:
            self.type = LOAN
        elif "EXPENSE" in tu:
            self.type = EXPENSE
        elif "UNKNOWN" in tu:
            self.type = UNKNOWN
        else:
            print("Unknown type", type, "ignored")

    def set_payee(self,payee):
        self.payee = payee

    def get_amount(self):
        return self.amount

    def set_amount(self, amount):
        if type(amount) is str:
            amount = float(amount.replace("$","").replace(" ",""))
        self.amount = round(amount,2)

    def get_min_due(self):
        return self.min_due

    def set_min_due(self, min_due):
        if type(min_due) is str:
            min_due = float(min_due.replace("$","").replace(" ",""))
        self.min_due = min_due

    def get_due_date(self):
       if self.due_date == None:
           return ""
       else:
           return self.due_date

    def get_date_representation(self, in_date):
        out_date_str = ''
        if type(in_date) == str:
            if in_date.strip() != '':
                temp_out_date = Date.parse_date(self, in_date, Date.get_global_date_format(Date))
                out_date_str = temp_out_date["str"]
        elif type(in_date) is dict:
            out_date_str = in_date["str"]
        elif type(in_date) is datetime:
            out_day = in_date.day
            out_month = in_date.month-1
            out_year = in_date.year
            out_date_str = wx.DateTime.FromDMY(out_day, out_month, out_year).Format(Date.get_global_date_format(Date))
        return out_date_str

    def set_due_date(self, due_date):
        if due_date == None or due_date == "":
            self.due_date = None
        else:
            self.due_date = self.get_date_representation(due_date)

    def get_sched_date(self):
        if self.sched_date == None:
            return ""
        else:
            return self.sched_date

    def set_sched_date(self, sched_date):
        if sched_date == None or sched_date == "":
            self.sched_date = None
        else:
            self.sched_date = self.get_date_representation(sched_date)

#TODO: Modify get_pmt_acct and set_pmt_acct to use AssetList and Asset!  For now just put in and return whatever is typed!
    def get_pmt_acct(self):
        return self.pmt_acct

    def set_pmt_acct(self, pmt_acct):
        self.pmt_acct = pmt_acct

    def get_pmt_method(self):
        spm = self.pmt_method
        if spm == DIRECT_DEPOSIT:
            return "Direct deposit"
        elif spm == SCHED_ONLINE:
            return "sched online"
        elif spm == CHECK:
            return "Check"
        elif spm == AUTOPAY:
            return "AutoPay"
        elif spm == CASH:
            return "Cash"
        elif spm == TBD:
            return "TBD"
        elif spm == MANUAL:
            return "Manual"
        elif spm == OTHER:
            return "Other"
        else:
            return "Unknown pmt method"

    def set_pmt_method(self, pmt_method):
        pmu = pmt_method.upper()
        if pmu == "DIRECT DEPOSIT":
            self.pmt_method = DIRECT_DEPOSIT
        elif pmu == "SCHED ONLINE":
            self.pmt_method = SCHED_ONLINE
        elif pmu == "CHECK":
            self.pmt_method = CHECK
        elif pmu == "AUTOPAY":
            self.pmt_method = AUTOPAY
        elif pmu == "CASH":
            self.pmt_method = CASH
        elif pmu == "TBD":
            self.pmt_method = TBD
        elif pmu == "MANUAL" or pmu == "":
            self.pmt_method = MANUAL
        elif pmu == "OTHER":
            self.pmt_method = OTHER
        else:
            print("Unknown payment method - " + pmt_method + "! Defaulting to TBD")
            self.pmt_method = TBD

    def get_pmt_frequency(self):
        spf = self.payment_frequency
        if spf == BIWEEKLY:
            return "Bi-weekly"
        elif spf == MONTHLY:
            return "monthly"
        elif spf == QUARTERLY:
            return "quarterly"
        elif spf == SEMI_YEARLY:
            return "semi-yearly"
        elif spf == YEARLY:
            return "yearly"
        elif spf == MANUAL:
            return "manual"
        else:
            return "unknown payment freq"

    def set_pmt_frequency(self, payment_freq):
        pfu = payment_freq.upper()
        if pfu == "BI-WEEKLY":
            self.payment_frequency = BIWEEKLY
        elif pfu == "MONTHLY":
            self.payment_frequency = MONTHLY
        elif pfu == "QUARTERLY":
            self.payment_frequency = QUARTERLY
        elif pfu == "SEMI-YEARLY":
            self.payment_frequency = SEMI_YEARLY
        elif pfu == "YEARLY":
            self.payment_frequency = YEARLY
        elif pfu == "MANUAL":
            self.payment_frequency = MANUAL
        else:
            print("Unknown payment frequency " + payment_freq + "! Defaulting to MANUAL")
            self.payment_frequency = MANUAL
