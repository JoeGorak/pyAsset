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

# Payment Methods
MYCHECKFREE = 1
SCHED_ONLINE = 2
SCHED_HICKAM = 3
CHECK = 4
AUTOPAY = 5
CASH = 6
OTHER = 7

# Payment_Frequency
MONTHLY = 1
QUARTERLY = 4
SEMI_YEARLY = 6
YEARLY = 12
MANUAL = -1

class Bill:
    def __init__(self, name = None, amount = 0.0, min_due = 0.0, due_date = None, sched_date = None,
                 pmt_acct = "Other", pmt_method = "Other", check_number = 0, pmt_freq = "Manual" ):
        self.name = name
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
        return " %-10s $%8.2f $%8.2f %10s %10s %s %s %s\n" %\
               (self.name, self.amount, self.min_due, self.due_date, self.sched_date, self.pmt_acct, self.pmt_method, self.pmt_frequency)

    def get_check_number(self):
        return self.check_number

    def set_check_number(self, check_number):
        self.check_number = check_number

    def get_name(self):
        return self.name

    def set_name(self,name):
        self.name = name

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

    def set_due_date(self, due_date):
        self.due_date = due_date

    def get_sched_date(self):
        return self.sched_date

    def set_sched_date(self, sched_date):
        self.sched_date = sched_date

#TODO: Modify get_pmt_acct and set_pmt_acct to use AssetList and Asset!  For now just put in and return whatever is typed!
    def get_pmt_acct(self):
        return self.pmt_acct

    def set_pmt_acct(self, pmt_acct):
        self.pmt_acct = pmt_acct

    def get_pmt_method(self):
        spm = self.payment_method
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
        elif pmu == "OTHER":
            self.pmt_method = OTHER
        else:
            print("Unknown payment method - " + pmt_method + "! Defaulting to SCHED_ONLINE")
            self.pmt_method = SCHED_ONLINE

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
