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
        # type: () -> object
        self.bills = []

    def __len__(self):
        return len(self.bills)

    def __getitem__(self, i):
        return self.bills[i]

    def __setitem__(self, i, val):
        self.bills[i] = val

#TODO:  Modify str to use fields from Bill vice field from Asset
    def __str__(self):
        ret_str = ""
        for i in range(len(self.bills)):
            cur_bill = self.bills[i]
            cd = cur_bill.details
            ret_str += "%-10s $%8.2f %s %s" % (cur_bill.name, cd.get_value(), cd.get_last_pull_date(), cd.get_type())
            limit = cd.get_limit()
            if limit != 0:
                ret_str += " $%8.2f $%8.2f" % (limit, cd.get_avail())
            rate = cd.get_rate()
            if rate != 0:
                ret_str += " %8.3f%%" % (rate*100)
            payment = cd.get_payment()
            if payment != 0:
                ret_str += " $%8.2f" % (payment)
            due_date = cd.get_due_date()
            if due_date != None:
                ret_str += " %s" % (due_date)
            sched_date = cd.get_sched_date()
            if sched_date != None:
                ret_str += " %s" % (sched_date)
            min_pay = cd.get_min_pay()
            if min_pay != 0:
                ret_str += " $%8.2f" % (min_pay)
            ret_str += "\n"
        return ret_str

    def __delitem__(self, i):
        del self.bills[i]

    def append(self, name):
        bill = Bill(name)
        self.bills.append(bill)
        return bill
