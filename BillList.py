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

    def append(self, payee):
        bill = Bill(payee)
        self.bills.append(bill)
        return bill
