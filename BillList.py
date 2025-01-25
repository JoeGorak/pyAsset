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

from Bill import Bill

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

    def __get_partition__(self, bills):
        payment_frequencies = Bill.get_payment_frequencies()
        partition = []
        for i in range(len(payment_frequencies)):
            partition.append(BillList())
        for i in range(len(bills)):
            partition[payment_frequencies.index(bills[i].get_pmt_frequency())].append(bills[i])
        return partition

    def sort_by_due_date(self):
        print("sort by due date called")
        bill_list_partition = self.__get_partition__(self.bills)
        for i in range(len(bill_list_partition)):
            if len(bill_list_partition[i]) != 0:
                print("Will sort partiton", i, "elements:", bill_list_partition[i] )
        return self                                 # JJG 8/16/24    For debugging!
     
    def insert(self, new_bill):
        if new_bill.empty():
            return

        #  Note that field to sort on is not specified here.
        #  It is controlled by the Bill itself and how operators are defined in Bill.py
        # To do a two level sort, call either the sort or the sort_by_due_date method after insert is finished.
        # Like this method, sort uses the operators in Bill.py
        # TODO: generalize the sort method to depracate the need for sort_by_due_date     JJG 8/16/24

        before  = -1
        after = 0
        while after < len(self.bills):
            if self.bills[after] > new_bill:
                break
            else:
                before = after
                after = after + 1
        if after == len(self.bills):
            self.bills.append(new_bill)
        else:
            self.bills[after+1:] = self.bills[after:len(self.bills)]
            self.bills[after] = new_bill

    def sort(self):
        return self.bills.sort()
