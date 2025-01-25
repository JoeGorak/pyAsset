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

#  Version information
#  06/25/2016     Initial version v0.1
#  06/27/2021     Added limit to structure
#  07/03/2021     Added parent to structure
#  08/07/2021     Version v0.2

from Transaction import Transaction
from Date import Date

class TransactionList:
    def __init__(self, parent, limit = None):
        # type: () -> object
        self.transactions = []
        self.parent = parent
        self.limit = limit

    def __len__(self):
        return len(self.transactions)

    def __getitem__(self, i):
        return self.transactions[i]

    def __setitem__(self, i, val):
        self.transactions[i] = val

    def __str__(self):
        ret_str = ""
        if self.limit != None:
            ret_str = "limit: %s\n" % (self.limit)
        if self.transactions != None:
            for i in range(len(self.transactions)):
                cur_transaction = self.transactions[i]
                ret_str = "%s\n%s" % (ret_str, cur_transaction)
        return ret_str

    def __delitem__(self, i):
        del self.transactions[i]

    def index(self, payee):
        ret_index = -1
        for i in range(len(self.transactions)):
            if (self.transactions[i].get_name() == name):
                ret_index = i
                break
        return ret_index

    def append(self, transaction):
        self.transactions.append(transaction)
        value_proj = self.update_current_and_projected_values(len(self.transactions)-1)
        self.parent.set_value_proj(value_proj)        
        return transaction

    def sort(self):
        return self.transactions.sort()

    def insert(self, new_transaction):
        before  = -1
        after = 0
        while after < len(self.transactions):
            if self.transactions[after] > new_transaction:
                break
            else:
                before = after
                after = after + 1
        if after == len(self.transactions):
            self.transactions.append(new_transaction)
        else:
            self.transactions[after+1:] = self.transactions[after:len(self.transactions)]
            self.transactions[after] = new_transaction
        value_proj = self.update_current_and_projected_values()
        self.parent.set_value_proj(value_proj)

    def update_current_and_projected_values(self, start_trans_number = 0):
        trans_number = 0
        trans_sched_date = proj_date = Date.get_proj_date(Date)
        if proj_date == None: return
        proj_date_obj = ret_proj_value = None
        if 'mm' not in proj_date:
            proj_date_obj = Date.parse_date(self, proj_date, Date.get_global_date_format(Date))["dt"]
        if proj_date_obj != None:
            while trans_number < start_trans_number:
                trans_number = trans_number + 1
            if trans_number == 0:
                current_value = self.parent.get_value()
            else:
                current_value = self.transactions[trans_number].get_current_value()
            ret_proj_value= proj_value = current_value
            while trans_number < len(self.transactions):
                trans_pmt_method = self.transactions[trans_number].get_pmt_method()
                process_transaction = True
                new_current_value = current_value
                new_proj_value = proj_value
                if trans_pmt_method != "posted":
                    trans_state = self.transactions[trans_number].get_state()
                    trans_sched_date = self.transactions[trans_number].get_sched_date()
                else:
                    process_transaction = False
                    self.transactions[trans_number].set_current_value(str(new_current_value))
                    self.transactions[trans_number].set_projected_value(str(new_proj_value))
                if process_transaction:
                    trans_action = self.transactions[trans_number].get_action()
                    if trans_action:

#                       Check to make sure transaction hasn't been voided before updaing current value   JJG 07/17/2021

                        if trans_state != "void":
                            trans_amount = self.transactions[trans_number].get_amount()
                        else:
                            trans_amount = 0.00
                        if trans_action == '-':
                            new_current_value = current_value - trans_amount
                            new_proj_value = proj_value - trans_amount
                        elif trans_action == '+':
                            new_current_value = current_value + trans_amount
                            new_proj_value = proj_value + trans_amount
                        else:
                            print("Unknown action " + trans_action + " ignored")
                            new_current_value = current_value
                            new_proj_value = proj_value
                        self.transactions[trans_number].set_current_value(str(new_current_value))
                        self.transactions[trans_number].set_projected_value(str(new_proj_value))
                    current_value = new_current_value
                    proj_value = new_proj_value
                    DateFormat = Date.get_global_date_format(Date)
                    if trans_sched_date != None:
                        trans_sched_date_obj = Date.parse_date(self, trans_sched_date, DateFormat)["dt"]
                        proj_date_obj = Date.parse_date(self, proj_date, Date.get_global_date_format(Date))["dt"]
                        if trans_sched_date_obj <= proj_date_obj:
                            ret_proj_value = proj_value
                    else:
                        ret_proj_value = proj_value
                trans_number += 1
            trans_number = trans_number + 1
        return ret_proj_value

    def update_transaction_dates(self, oldDateFormat, newDateFormat):
        trans_number = 0

        while trans_number < len(self.transactions):
            due_date = self.transactions[trans_number].get_due_date()
            if due_date != None:
                new_due_date = Date.convertDateFormat(Date, due_date, oldDateFormat, newDateFormat)
                self.transactions[trans_number].set_due_date(new_due_date)

            sched_date = self.transactions[trans_number].get_sched_date()
            if sched_date != None:
                new_sched_date = Date.convertDateFormat(Date, sched_date, oldDateFormat, newDateFormat)
                self.transactions[trans_number].set_sched_date(new_sched_date)

            self.transactions[trans_number].dateFormat = newDateFormat

            trans_number += 1