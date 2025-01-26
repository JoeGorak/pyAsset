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

from logging import raiseExceptions
from msvcrt import kbhit
from Bill import Bill
from Date import Date

class BillList:
    def __init__(self):
        self.bills = []

    def __len__(self):
        return len(self.bills)

    def __getitem__(self, i):
        return self.bills[i]

    def __setitem__(self, i, val):
        self.bills[i] = val

    def __str__(self):
        ret_str = ""
        for i in range(len(self.bills)):
            cb = self.bills[i]
            ret_str += "Payee: %-30s Type: %-20s, Amount: $%8.2f" % (cb.get_payee(), cb.get_type(), cb.get_amount())
            min_due = cb.get_min_due()
            if min_due != None:
                ret_str += " Min Due: $%8.2f" % (min_due)
            due_date = cb.get_due_date()
            if due_date != None:
                ret_str += " Due Date: %10s" % (due_date)
            sched_date = cb.get_sched_date()
            if sched_date != None:
                ret_str += " Sched Date: %10s" % (sched_date)
            pmt_acct = cb.get_pmt_acct()
            if pmt_acct != None:
                ret_str += " Pmt Acct: %s Pmt Method: %s Pmt Freq: %s" % (pmt_acct, cb.get_pmt_method(), cb.get_pmt_frequency())
            ret_str += "\n"
        return ret_str

    def __delitem__(self, i):
        del self.bills[i]

    def index(self, payee):
        ret_index = -1
        for i in range(len(self.bills)):
            if (self.bills[i].get_payee() == payee):
                ret_index = i
                break
        return ret_index

    def append(self, bill):
        self.bills.append(bill)
        return bill

    def sort_by_fields(self, fields):                                   # A true in-place multi-field sort!    JJG 1/25/25
        valid_fields = ['due date', 'pmt frequency']
        for i in range(len(fields)):
            field = fields[i][0]
            if field not in valid_fields:
                print("field", field, "is not valid. Valid fields are", valid_fields, "ignoring sort for bills list" )
                return self.bills
        bills = self.bills
        payment_frequencies = Bill.get_payment_frequencies()
        j = len(bills) - 1
        while j >= 0:
            i = 0
            while i < len(fields):
                field = fields[i][0]
                order = fields[i][1]
                max_index = j
                current_max = None
                if field == "pmt frequency":
                    current_max = payment_frequencies.index(bills[j].get_pmt_frequency())
                elif field == "due date":
                    current_max = Date.parse_date(self, bills[j].get_due_date(), Date.get_global_date_format(self))
                    if current_max != None:
                        current_max = current_max['dt']
                    else:
                        current_max = Date.parse_date(self, "01/01/1970", "%m/%d/%Y")['dt']   # Force blank due_dates to top of bill list!
                test_max = current_max
                for k in range(j - 1, -1, -1):
                    if field == "pmt frequency":
                        test_max = payment_frequencies.index(bills[k].get_pmt_frequency())
                    elif field == "due date":
                        test_max = Date.parse_date(self, bills[k].get_due_date(), Date.get_global_date_format(self))
                        if test_max != None:
                            test_max = test_max['dt']
                        else:
                            test_max = Date.parse_date(self, "01/01/1970", "%m/%d/%Y")['dt']        # Force blanks to the top
                    if test_max > current_max and order == '>':
                        current_max = test_max
                        max_index = k
                if test_max == current_max:                     # Check the next field if this field is equal!
                    i += 1
                else:                                           # force while loop checking fields to terminate cause we found the spot!
                    i = len(fields)                             
            bills[j], bills[max_index] = bills[max_index], bills[j]
            j -= 1
        return self.bills
     
    def insert(self, new_bill):
        if new_bill.empty():
            return
        self.bills.append(new_bill)

    def sort(self):
        return self.bills.sort()
