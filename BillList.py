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
from Bill import Bill
from Date import Date

class BillList():
    def __init__(self):
        self.bills = None

    def getBills(self):
        return self.bills

    def getSortOrder(self):
        sortFields = [('Due Date', '>'), ('Pmt Freq', '<')]                             # Default sort order for bills list
        valid_fields = Bill.get_bill_fields()
        for i in range(len(sortFields)):
            field = sortFields[i][0]
            if field not in valid_fields:
                print("field", field, "is not valid. Valid fields are", valid_fields, "ignoring sort for bills list" )
                return []
        return sortFields

    def __len__(self):
        if self.bills != None:
            return len(self.getBills())
        else:
            return 0

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
        if bill != None:
            if self.bills == None:
                self.bills = [bill]
            else:
                self.bills.append(bill)
        return bill

    def get_field_value(self, field, order, j, bills):
        field_value = None
        if field == "Pmt Freq":
#            payment_frequencies = Bill.get_payment_frequencies()
            field_value = bills[j].get_pmt_frequency()
        elif field == "Due Date" or field == "Sched Date":
            current = None
            if field == "Due Date":
                current = Date.parse_date(self, bills[j].get_due_date(), Date.get_global_date_format(self))
            else:
                current = Date.parse_date(self, bills[j].get_sched_date(), Date.get_global_date_format(self))
            if current != None:
                field_value = current['dt']
            else:
                if order == '>':
                    field_value = Date.parse_date(self, "01/01/1970", "%m/%d/%Y")['dt']   # Force blank due_dates to top of bill list!
                else:
                    field_value = Date.parse_date(self, "12/31/9999", "%m/%d/%Y")['dt']   # Force blanks to the bottom
        elif field == "Type":
            field_value = bills[j].get_type()
        return field_value


    def sort_by_fields(self, fields = None):                                   # A true multi-field sort!    JJG 1/25/25
        if self.bills == None:
            return
        if fields == None:
            fields = self.getSortOrder()
        valid_fields = Bill.get_bill_fields()
        for i in range(len(fields)):
            field = fields[i][0]
            if field not in valid_fields:
                print("field", field, "is not valid. Valid fields are", valid_fields, "ignoring sort for bills list" )
                return []
        bills = self.bills
        field = fields[0][0]
        order = fields[0][1]
        if order == '>':
            j = len(bills) - 1
        else:
            j = 0
        while (j > 0 and order == '>') or (j < len(bills) and order == '<'):
            maxmin_index = j
            maxmin = self.get_field_value(field, order, j, bills)
            if order == '>':
                krange = range(j-1, -1, -1)
            else:
                krange = range(j+1, len(bills))
            for k in krange:
                test_maxmin = self.get_field_value(field, order, k, bills)
                if (order == '>' and test_maxmin > maxmin) or (order == '<' and test_maxmin < maxmin):
                    maxmin = test_maxmin
                    maxmin_index = k
                elif test_maxmin == maxmin:                           # Check the remaining fields if this field is equal!
                    for i in range(1, len(fields)):
                        curr = self.get_field_value(fields[i][0], fields[i][1], j, bills)
                        poss = self.get_field_value(fields[i][0], fields[i][1], k, bills)
                        if (fields[i][1] == '>' and curr > poss) or (fields[i][1] == '<' and curr < poss):
                            maxmin = test_maxmin
                            maxmin_index = k
                            break
            bills[j], bills[maxmin_index] = bills[maxmin_index], bills[j]
            if order == '>':
                j -= 1
            else:
                j += 1
        self.bills = bills
        pass
     
    def insert(self, new_bill):
        if new_bill != None:
            self.append(new_bill)

    def sort(self):
        return self.sort_by_fields(self.getSortOrder(self))
