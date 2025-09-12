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

from operator import ge
from re import S
from Transaction import Transaction
from Date import Date

class TransactionList:
    def __init__(self, parent, transactions=None, limit=None):
        # type: () -> object
        self.transactions = transactions
        self.parent = parent
        self.limit = limit

    def __len__(self):
        if self.transactions == None:
            return 0
        else:
            return len(self.transactions)

    def getSortOrder(self):
        sortFields = [('Sched Date', '>'), ('Action', '<')]                               # Default sort order for transaction list
        valid_fields = Transaction.get_transaction_fields()
        for i in range(len(sortFields)):
            field = sortFields[i][0]
            if field not in valid_fields:
                print("field", field, "is not valid. Valid fields are", valid_fields, "ignoring sort for transaction list" )
                return []
        return sortFields

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

    def getTransactions(self):
        return self.transactions

    def index(self, payee, date):
        # Assume the desired transaction is not there
        ret_index = -1
        # if there are transactions
        if self.transactions != None:
            date = Date.parse_date(Date, date, Date.get_global_date_format(Date))
            # Loop over all the transactions
            for i in range(len(self.transactions)):
                # if the payee of the current transction matches
                if self.transactions[i].get_payee() == payee:
                    due_date = self.transactions[i].get_due_date()
                    # Check to make sure the due date also matched
                    if due_date != None and self.transactions[i].get_due_date()['str'] == date['str']:
                        # We found it! Set the index and get out of the loop!
                        ret_index = i
                        break
        return ret_index

    def append(self, transaction):
        if self.transactions == None:
            self.transactions = TransactionList(self.parent, [])
        self.transactions.append(transaction)
        value_proj = self.update_current_and_projected_values(len(self.transactions)-1)
        self.parent.set_value_proj(value_proj)        
        return transaction

    def sort(self):
        return self.sort_by_fields()

    def insert(self, new_transaction):
        before  = -1
        after = 0
        if self.transactions == None:
            self.transactions = [new_transaction]
        else:
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

    def get_field_value(self, field, order, j, transactions):
        field_value = None
        if field == "Due Date" or field == "Sched Date":
            current = None
            if field == "Due Date":
                current = Date.parse_date(self, transactions[j].get_due_date(), Date.get_global_date_format(self))
            else:
                current = Date.parse_date(self, transactions[j].get_sched_date(), Date.get_global_date_format(self))
            if current != None:
                field_value = current['dt']
        elif field == "Action":
            field_value = transactions[j].get_action()
        return field_value

    def sort_by_fields(self, fields = None):                                   # A true multi-field sort! Modeled after similar function for BillList    JJG 8/31/2025
        if self.transactions == None:
            return
        if fields == None:
            fields = self.getSortOrder()
        valid_fields = Transaction.get_transaction_fields()
        for i in range(len(fields)):
            field = fields[i][0]
            if field not in valid_fields:
                print("field", field, "is not valid. Valid fields are", valid_fields, "ignoring sort for transaction list" )
                return []
        transactions = self.transactions
        field = fields[0][0]
        order = fields[0][1]
        if order == '>':
            j = len(transactions)-1
        else:
            j = 0
        while (j > 0 and order == '>') or (j < len(transactions) and order == '<'):
            maxmin_index = j
            maxmin = self.get_field_value(field, order, j, transactions)
            if maxmin == None:
                if order == '>':
                    j -= 1
                else:
                    j += 1
                continue
            if order == '>':
                krange = range(j-1, -1, -1)
            else:
                krange = range(j+1, len(transactions))
            for k in krange:
                test_maxmin = self.get_field_value(field, order, k, transactions)
                if test_maxmin == None:
                    continue
                if (test_maxmin > maxmin and order == '>') or (test_maxmin < maxmin and order == '<'):
                    maxmin = test_maxmin
                    maxmin_index = k
                elif test_maxmin == maxmin:
                    for i in range(1, len(fields)):                                    # Check the remaining fielda if this field is equal
                       curr = self.get_field_value(fields[i][0], fields[i][1], j, transactions)
                       poss = self.get_field_value(fields[i][0], fields[i][1], k, transactions)
                                                                                       # Update maxmin if the next field is different
                       if (curr > poss and fields[i][1] == '>') or (curr < poss and fields[i][1] == '<'):
                           maxmin_index = k
                           maxmin = test_maxmin
                           break
            transactions[j], transactions[maxmin_index] = transactions[maxmin_index], transactions[j]
            if order == '>':
                j -= 1
            else:
                j += 1
        self.transactions = transactions
        self.update_current_and_projected_values()

    def update_current_and_projected_values(self, start_trans_number = 0):
        ret_proj_value = self.parent.get_value()
        transactions = self.transactions
        if transactions == None:
            return ret_proj_value
        trans_number = 0
        trans_sched_date = proj_date = Date.get_proj_date(Date)
        if proj_date == None: return
        proj_date_obj = None
        if 'mm' not in proj_date:
            proj_date_obj = Date.parse_date(self, proj_date, Date.get_global_date_format(Date))["dt"]
        if proj_date_obj != None:
            while trans_number < start_trans_number:
                trans_number = trans_number + 1
            if trans_number == 0:
                current_value = self.parent.get_value()
            else:
                current_value = self.transactions[trans_number-1].get_current_value()
            ret_proj_value= proj_value = current_value
            while trans_number < len(self.transactions):
                due_date_obj = Date.parse_date(self, self.transactions[trans_number].get_due_date(), Date.get_global_date_format(Date))
                if due_date_obj != None:
                    trans_pmt_method = self.transactions[trans_number].get_pmt_method()
                    trans_sched_date = self.transactions[trans_number].get_sched_date()
                    new_current_value = current_value
                    new_proj_value = proj_value
                    trans_state = self.transactions[trans_number].get_state()
                    self.transactions[trans_number].set_current_value(str(new_current_value))
                    self.transactions[trans_number].set_projected_value(str(new_proj_value))
                    trans_action = self.transactions[trans_number].get_action()
                    if trans_action:
#                       Check to make sure transaction hasn't been voided before updating current value     JJG 07/17/2021
#                       Also check for outstanding transactions which should not affect current value
                        if trans_state != "void" and trans_state != "outstanding":
                            trans_amount = self.transactions[trans_number].get_amount()
                            if trans_amount == None:
                                trans_amount = 0.00
                        else:
                            trans_amount = 0.00
                        if trans_action == '-':
                            new_current_value = current_value - trans_amount
                            new_proj_value = proj_value - trans_amount
                        elif trans_action == '+':
                            new_current_value = current_value + trans_amount
                            new_proj_value = proj_value + trans_amount
                        else:
                            print("Unknown action ", trans_action, " ignored")
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
        return ret_proj_value

    def update_transaction_dates(self, oldDateFormat, newDateFormat):
        trans_number = 0
        if self.transactions != None:
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