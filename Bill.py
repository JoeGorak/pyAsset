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

import re
import wx
from Date import Date
from wx.core import DateTime
from datetime import date, datetime

class Bill:

    # Define static class variables - There are no enums in python
    # We use get_bill_types() etc to access these lists

    bill_types = [ "checking and savings", "credit card", "loan", "emergency fund", "expense", "unknown" ]
    payment_methods = [ "direct deposit", "sched online", "check", "autopay", "cash", "TBD", "Zelle", "manual", "other", "unknown" ]
    payment_frequencies = [ "bi-weekly", "2 weeks", "4 weeks", "monthly", "quarterly", "semi-yearly", "yearly", "manual", "unknown" ]

    inc_values = ["2 weeks", "2 weeks", "4 weeks", "1 month", "3 months", "6 months", "1 year", "manual"]

    bill_fields = [ "Payee", "Type", "Amount", "Min Due", "Due Date", "Sched Date", "Pmt Acct", "Pmt Method", "Pmt Freq", "Check Number" ]

    # Instance variables

    def __init__(self, parent, payee=" "*50, type="unknown", action="-", amount=0.00, min_due=0.00, due_date=None, sched_date=None,
                 pmt_acct="unknown", pmt_method="TBD", check_number=0, pmt_frequency="manual" ):
        self.parent = parent
        self.set_payee(payee)
        self.set_type(type)
        self.set_action(action)
        self.set_amount(amount)
        self.set_min_due(min_due)
        self.set_due_date(due_date)
        self.set_sched_date(sched_date)
        self.set_pmt_acct(pmt_acct)
        self.set_pmt_method(pmt_method)
        self.set_pmt_frequency(pmt_frequency)
        self.set_check_number(check_number)

    def get_bill_inc_value(payment_freq):
        ret_value = None
        which = Bill.payment_frequencies.index(payment_freq)
        if which != -1:
            inc_value = Bill.inc_values[which]
            if inc_value == "2 weeks" or inc_value == "bi-weekly":
                ret_value = wx.DateSpan(weeks=2)
            elif inc_value == "4 weeks":
                ret_vaue = wx.DateSpan(weeks=4)
            elif inc_value == "1 month":
                ret_value = wx.DateSpan(months=1)
            elif inc_value == "3 months":
                ret_value = wx.DateSpan(months=3)
            elif inc_value == "6 months":
                ret_value = wx.DateSpan(months=6)
            elif inc_value == "1 year":
                ret_value = wx.DateSpan(years=1)
        return ret_value

    def get_bill_types():
        return Bill.bill_types

    def get_payment_methods():
        return Bill.payment_methods

    def get_payment_frequencies():
        return Bill.payment_frequencies

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
        if type(check_number) is int:
            try:
                check_number = str(check_number)
            except:
                check_number = "0"
        self.check_number = check_number
        return self.check_number

    def set_action(self, action):
        self.action = action
        return self.action

    def get_action(self):
        return self.action

    def get_payee(self):
        return self.payee

    def get_type(self):
        ret_type = Bill.bill_types[self.type]
        if ret_type == "unknown":
            ret_type = ""
        return ret_type
 
    def set_type(self, in_type):
        if type(in_type) is str:
            type_lower = in_type.lower().strip()
            try:
             self.type = Bill.bill_types.index(type_lower)
            except:
                self.type = -1
        elif type(in_type) is int:
            self.type = in_type
        else:
            self.type = -1
        if self.type == -1:
            print("Unknown type", in_type, "ignored - default to unknown")
            self.type = Bill.bill_types.index("unknown")
        return self.type

    def set_payee(self,payee):
        self.payee = payee
        return self.payee

    def get_amount(self):
        return self.amount

    def set_amount(self, amount):
        if type(amount) is str:
            amount = float(amount.replace("$","").replace(" ",""))
        self.amount = round(amount,2)
        return self.amount

    def get_min_due(self):
        return self.min_due

    def set_min_due(self, min_due):
        if type(min_due) is str:
            min_due = float(min_due.replace("$","").replace(" ",""))
        self.min_due = min_due
        return self.min_due

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
        elif type(in_date) is DateTime or type(in_date) is datetime:
            out_day = in_date.day
            if type(in_date) is DateTime:
                out_month = in_date.month
            else:
                out_month = in_date.month-1
            out_year = in_date.year
            out_date_str = wx.DateTime.FromDMY(out_day, out_month, out_year).Format(Date.get_global_date_format(Date))
        return out_date_str

    def set_due_date(self, due_date):
        if due_date == None or due_date == "":
            self.due_date = None
        else:
            self.due_date = self.get_date_representation(due_date)
        return self.due_date

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
        return self.sched_date

    def get_pmt_acct(self):
        try:
            pmt_acct = self.pmt_acct
        except:
            pmt_acct = ""
        return pmt_acct

    def set_pmt_acct(self, pmt_acct):
        if pmt_acct == "unknown":
            self.pmt_acct = "unknown"
        else:
            try:
                assets = self.parent.assets
            except:
                self.pmt_acct = "unknown"
                assets = None
            if assets != None:
                if assets.index(pmt_acct) == -1 and pmt_acct != "other" and pmt_acct != "unknown" and pmt_acct != "":
                    self.MsgBox("Payment account " + pmt_acct + " not found in asset list! Ignoring update")
                    self.pmt_acct = "unknown"
                else:
                    self.pmt_acct = pmt_acct
        return self.pmt_acct

    def get_pmt_method(self):
        return Bill.payment_methods[self.pmt_method]
 
    def set_pmt_method(self, pmt_method):
        pml = pmt_method.lower().strip()
        if pml == "tbd": pml = "TBD"                        # Handle TBD special case
        self.pmt_method = Bill.payment_methods.index(pml)
        if self.pmt_method == -1:
            print("Unknown payment method - " + pmt_method + "! Defaulting to unknown")
            self.pmt_method = Bill.payment_methods.index("unknown")
        return self.pmt_method

    def get_pmt_frequency(self):
        return Bill.payment_frequencies[self.payment_frequency]

    def set_pmt_frequency(self, payment_freq):
       pfl = payment_freq.lower().strip().replace("every ","")
       self.payment_frequency = Bill.payment_frequencies.index(pfl)
       if self.payment_frequency == -1:
           print("Unknown payment frequency " + payment_freq + "! Defaulting to unknown")
           self.payment_frequency = Bill.payment_frequencies.index("unknown")
       return self.payment_frequency

    def MsgBox(self, message):
        d = wx.MessageDialog(self.parent, message, "error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()

