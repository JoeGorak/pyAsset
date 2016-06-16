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
#  6/11/2016     Initial version v0.1

import os
from Transaction import Transaction


class Asset:
    def __init__(self, filename=None):
        self.name = ''
        self.filename = None
        self.transactions = []
        self.total = 0.
        if filename:
            self.read_qif(filename)
        return

    def __len__(self):
        return len(self.transactions)

    def __getitem__(self, i):
        return self.transactions[i]

    def __setitem__(self, i, val):
        self.transactions[i] = val

    def __str__(self):
        return " %-10s $%8.2f\n" % (self.name, self.total)

    def __delitem__(self, i):
        del self.transactions[i]

    def append(self, item):
        self.transactions.append(item)

    def read_qif(self, filename, readmode='normal'):
        if readmode == 'normal':  # things not to do on 'import':
            self.filename = filename
            name = filename.replace('.qif', '')
            self.name = os.path.split(name)[1]
        mffile = open(filename, 'r')
        lines = mffile.readlines()
        mffile.close()
        transaction = Transaction()
        type = lines.pop(0)
        for line in lines:
            type, rest = line[0], line[1:].strip()
            if type == "D":
                transaction.setdate(rest)
                blank_transaction = False
            elif type == "T":
                transaction.setamount(rest)
                blank_transaction = False
            elif type == "P":
                transaction.setpayee(rest)
                blank_transaction = False
            elif type == "C":
                transaction.setcleared(rest)
                blank_transaction = False
            elif type == "N":
                transaction.setnumber(rest)
                blank_transaction = False
            elif type == "L":
                transaction.setcomment(rest)
                blank_transaction = False
            elif type == "M":
                transaction.setmemo(rest)
                blank_transaction = False
            elif type == "A":
                total_payee = transaction.getpayee() + " " + rest
                transaction.setpayee(total_payee)
                blank_transaction = False
            elif type == "^":
                if not blank_transaction:
                    self.transactions.append(transaction)
                    self.total = self.total + transaction.getamount()
                    transaction = Transaction()
                blank_transaction = True
            else:
                print "Unparsable line: ", line[:-1]
        self.sort()
        return

    def sort(self):
        self.transactions.sort()

    def write_qif(self, filename=None):
        if not filename:
            if not self.filename: raise "No Asset filename defined"
            filename = self.filename
        self.filename = filename
        file = open(filename, 'w')
        file.write("%s" % self.qif_repr())
        file.close()
        return

    def write_txt(self, filename='pyasset.txt'):
        file = open(filename, 'w')
        file.write("%s" % self.text_repr())
        file.close()
        return

    def text_repr(self):
        lines = []
        for transaction in self.transactions: lines.append(str(transaction))
        return '\n'.join(lines)

    def qif_repr(self):
        lines = ['Type:Bank']
        for transaction in self.transactions: lines.append(transaction.qif_repr())
        lines.append('')
        return '\n'.join(lines)
