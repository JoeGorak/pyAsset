#!/usr/bin/env /usr/local/bin/pythonw

"""

COPYRIGHT/LICENSING
Copyright (c) 2016,2017,2019,2020 Joseph J. Gorak. All rights reserved.
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

def string_limit(mystr, limit):
    if mystr and len(mystr) > limit:
        mystr = mystr[:limit]
    return mystr

class Transaction:
    def __init__(self):
        self.pmt_method = None
        self.check_num = None
        self.payee = None
        self.amount = None
        self.action = None
        self.balance = None
        self.sched_date = None
        self.due_date = None
        self.cleared = 0
        self.comment = None
        self.memo = None

    def __str__(self):
        lines = []
        lines.append("Sched date: %1s " % self.sched_date)
        if self.due_date:
            lines.append("Due date: %1s " % self.due_date)
        if self.pmt_method:
            lines.append("Pmt method: %1s " % self.pmt_method)
        if self.check_num:
            lines.append("Check_num: %1d " % self.check_num)
        lines.append("Payee: %1s " % string_limit(self.payee, 40))
        lines.append("Amount: %4.2f " % self.amount)
        if self.action:
            lines.append("Action: %s " % self.action)
            lines.append("Balance: %4.2f " % self.balance)
        lines.append("Cleared: ")
        if self.cleared:
            lines.append("x ")
        else:
            lines.append("  ")
        if self.comment:
            lines.append("Comment: %1s " % string_limit(self.comment, 10))
        if self.memo:
            lines.append("Memo: %1s " % string_limit(self.memo, 10))
        return ''.join(lines)

    def __gt__(self, other):
        return self.sched_date > other.sched_date

    def __lt__(self, other):
        return self.sched_date < other.sched_date

    def qif_repr(self):
        lines = []
        lines.append("D%s" % self.sched_date.formatUS())
        lines.append("D%s" % self.due_date.formatUS())
        lines.append("T%.2f" % self.amount)
        if self.cleared:
            lines.append("Cx")
        else:
            lines.append("C*")
        if self.check_num:
            lines.append("N%d" % self.check_num)
        lines.append("P%s" % self.payee)
        if self.comment:
            lines.append("L%s" % self.comment)
        if self.memo:
            lines.append("M%s" % self.memo)
        lines.append("^")
        return '\n'.join(lines)

    def set_pmt_method(self,rest):
        self.pmt_method = rest

    def set_amount(self, rest):
        try:
            self.amount = round(float(rest), 2)
        except:
            self.amount = 0.0

    def set_action(self, rest):
        self.action = rest

    def set_balance(self, rest):
        try:
            self.balance = round(float(rest), 2)
        except:
            self.balance = 0.0

    def set_sched_date(self, rest):
        if rest != 0:
            self.sched_date = str(rest).split(" ")[0]

    def set_due_date(self, rest):
        if rest != 0:
            self.due_date = str(rest).split(" ")[0]

    def set_payee(self, rest):
        self.payee = rest

    def set_comment(self, rest):
        self.comment = rest

    def set_memo(self, rest):
        self.memo = rest

    def set_check_num(self, rest):
        self.check_num = None
        if rest != None:
            self.check_num = rest
        return

    def set_cleared(self, rest):
        if rest[0] == "x":
            self.cleared = 1
        else:
            self.cleared = 0
        return

    def get_pmt_method(self):
        return self.pmt_method

    def get_sched_date(self):
        return self.sched_date

    def get_due_date(self):
        return self.due_date

    def get_payee(self):
        return self.payee

    def get_amount(self):
        return self.amount

    def get_action(self):
        return self.action

    def get_balance(self):
        return self.balance

    def get_comment(self):
        return self.comment

    def get_memo(self):
        return self.memo

    def get_check_num(self):
        return self.check_num
