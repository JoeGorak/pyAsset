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

import wx
from Date import Date
from datetime import date, datetime

# Bill types
CHECKINGANDSAVINGS = 0
CREDITCARD = 1
LOAN = 2
EXPENSE = 3
UNKNOWN = 4

# Payment Methods
MYCHECKFREE = 1
SCHED_ONLINE = 2
SCHED_HICKAM = 3
CHECK = 4
AUTOPAY = 5
CASH = 6
TBD = 7
MANUAL = 8
OTHER = 9

# Payment_Frequency
MONTHLY = 1
QUARTERLY = 4
SEMI_YEARLY = 6
YEARLY = 12
MANUAL = -1

class Bill:
    def __init__(self, payee = None, type = "Unknown", amount = 0.0, min_due = 0.0, due_date = None, sched_date = None,
                 pmt_acct = "Other", pmt_method = "TBD", check_number = 0, pmt_freq = "Manual" ):
        self.payee = payee
        self.type = self.set_type(type)
        self.amount = amount
        self.min_due = min_due
        self.due_date = due_date
        self.sched_date = sched_date
        self.pmt_acct = self.set_pmt_acct(pmt_acct)
        self.pmt_method = self.set_pmt_method(pmt_method)
        self.pmt_frequency = self.set_pmt_frequency(pmt_freq)
        self.check_number = check_number
        return

    def __str__(self):
        return " %-10s %-20s $%8.2f $%8.2f %10s %10s %s %s %s\n" %\
               (self.payee, self.type, self.amount, self.min_due, self.due_date, self.sched_date, self.pmt_acct, self.pmt_method, self.pmt_frequency)

    def get_check_number(self):
        return self.check_number

    def set_check_number(self, check_number):
        self.check_number = check_number

    def get_payee(self):
        return self.payee

    def get_type(selt):
        st = selt.type
        if st == CHECKINGANDSAVINGS:
            return "Checking and saving"
        elif st == CREDITCARD:
            return "Credit Card"
        elif st == LOAN:
            return "Loan"
        elif st == EXPENSE:
            return "Expense"
        elif st == UNKNOWN:
            return "Unknown"
        else:
            return "Unknown bill type"

    def set_type(self,type):
        tu = type.upper()
        if tu == "CHECKING AND SAVINGS ACCOUNTS":
            self.type = CHECKINGANDSAVINGS
        elif tu == "CREDIT CARDS":
            self.type = CREDITCARD
        elif tu == "LOANS":
            self.type = LOAN
        elif tu == "EXPENSES":
            self.type = EXPENSE
        elif tu == "UNKNOWN":
            self.type = UNKNOWN
        else:
            print("Unknown type", type, "ignored")

    def set_payee(self,payee):
        self.payee = payee

    def get_amount(self):
        return self.amount

    def set_amount(self, amount):
        self.amount = amount

    def get_min_due(self):
        return self.min_due

    def set_min_due(self, min_due):
        self.min_due = min_due

    def get_due_date(self):
       return self.due_date

    def get_date_representation(self, in_date):
        out_date_str = ''
        if type(in_date) == str:
            if in_date != '':
                temp_out_date = Date.guessDateFormat(self, in_date)
                temp_out_date = date(temp_out_date['year'], temp_out_date['month'], temp_out_date['day'])
                temp_out_date = Date.parse_date(Date, temp_out_date, Date.get_global_date_format(Date))
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
        self.due_date = self.get_date_representation(due_date)

    def get_sched_date(self):
        return self.sched_date

    def set_sched_date(self, sched_date):
        self.sched_date = self.get_date_representation(sched_date)

#TODO: Modify get_pmt_acct and set_pmt_acct to use AssetList and Asset!  For now just put in and return whatever is typed!
    def get_pmt_acct(self):
        return self.pmt_acct

    def set_pmt_acct(self, pmt_acct):
        self.pmt_acct = pmt_acct

    def get_pmt_method(self):
        spm = self.pmt_method
        if spm == MYCHECKFREE:
            return "Mycheckfree"
        elif spm == SCHED_ONLINE:
            return "sched online"
        elif spm == SCHED_HICKAM:
            return "sched Hickam"
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
        if pmu == "MYCHECKFREE":
            self.pmt_method = MYCHECKFREE
        elif pmu == "SCHED ONLINE":
            self.pmt_method = SCHED_ONLINE
        elif pmu == "SCHED HICKAM":
            self.pmt_method = SCHED_HICKAM
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
        if spf == MONTHLY:
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
        if pfu == "MONTHLY":
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
            print("Unknown payment frequency -" + payment_freq + "! Defaulting to MANUAL")
            self.payment_frequency = MANUAL
