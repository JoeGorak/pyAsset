#!/usr/bin/env /usr/local/bin/pythonw

"""

COPYRIGHT/LICENSING
Copyright (c) 2016,2017 Joseph J. Gorak. All rights reserved.
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

from Date import Date

def string_limit(mystr, limit):
    if mystr and mystr > limit:
        mystr = mystr[:limit]
    return mystr


class Transaction:
    def __init__(self):
        self.date = Date()
        self.number = None
        self.payee = None
        self.cleared = 0
        self.comment = None
        self.memo = None
        self.amount = None

    def __str__(self):
        lines = []
        lines.append("%10s " % self.date.formatUS())
        if self.number:
            lines.append("%5d " % self.number)
        else:
            lines.append("      ")
        lines.append("%-20s " % string_limit(self.payee, 20))
        if self.cleared:
            lines.append("x ")
        else:
            lines.append("  ")
        if self.comment:
            lines.append("%-10s " % string_limit(self.comment, 10))
        else:
            lines.append("           ")
        if self.memo:
            lines.append("%-10s " % string_limit(self.memo, 10))
        else:
            lines.append("           ")
        lines.append("%8.2f " % self.amount)
        return ''.join(lines)

    def __cmp__(self, other):
        return cmp(self.date, other.date)

    def qif_repr(self):
        lines = []
        lines.append("D%s" % self.date.formatUS())
        lines.append("T%.2f" % self.amount)
        if self.cleared:
            lines.append("Cx")
        else:
            lines.append("C*")
        if self.number: lines.append("N%d" % self.number)
        lines.append("P%s" % self.payee)
        if self.comment:
            lines.append("L%s" % self.comment)
        if self.memo:
            lines.append("M%s" % self.memo)
        lines.append("^")
        return '\n'.join(lines)

    def setamount(self, rest):
        self.amount = float(rest.strip().replace(',', ''))

    def setdate(self, rest):
        self.date = Date(rest)

    def setpayee(self, rest):
        self.payee = rest

    def setcomment(self, rest):
        self.comment = rest

    def setmemo(self, rest):
        self.memo = rest

    def setnumber(self, rest):
        val = rest.strip()
        if val:
            self.number = int(val)
        else:
            self.number = None
        return

    def setcleared(self, rest):
        if rest[0] == "x":
            self.cleared = 1
        else:
            self.cleared = 0
        return

    def getpayee(self):
        return self.payee

    def getamount(self):
        return self.amount
