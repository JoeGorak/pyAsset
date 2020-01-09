#!/usr/bin/env /usr/local/bin/pythonw
"""

COPYRIGHT/LICENSING
Copyright (c) 2016, Joseph J. Gorak. All rights reserved.
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

#  Version information
#  6/25/2016     Initial version v0.1

from Transaction import Transaction


class TransactionList:
    def __init__(self):
        # type: () -> object
        self.transactions = []

    def __len__(self):
        return len(self.transactions)

    def __getitem__(self, i):
        return self.transactions[i]

    def __setitem__(self, i, val):
        self.transactions[i] = val

    def __str__(self):
        ret_str = ""
        for i in range(len(self.transactions)):
            ret_str = "%s\n%s" % (ret_str, self.transactions[i])
        return ret_str

    def __delitem__(self, i):
        del self.transactions[i]

    def append(self):
        transaction = Transaction()
        self.transactions.append(transaction)
        return transaction

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
#            self.transactions.append(Transaction())
            self.transactions[after+1:] = self.transactions[after:len(self.transactions)]
            self.transactions[after] = new_transaction
