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

#  Version information
#  06/11/2016     Initial version v0.1
#  08/07/2021     Version v0.2

import wx
from Date import Date

# Transaction States
UNKNOWN = 0
OUTSTANDING = 1
CLEARED = 2
VOID = 3
RECONCILED = 4

def string_limit(mystr, limit):
    if mystr and len(mystr) > limit:
        mystr = mystr[:limit]
    return mystr

class Transaction:
    def __init__(self, parent):
        self.parent = parent
        self.dateFormat = Date.get_global_date_format(self)
        self.dateSep = Date.get_global_date_sep(self)
        self.pmt_method = None
        self.check_num = None
        self.payee = None
        self.amount = None
        self.action = None
        self.current_value = None
        self.sched_date = None
        self.due_date = None
        self.state = OUTSTANDING
        self.prev_state = UNKNOWN
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
            if self.current_value:
                lines.append("Curr Value: %4.2f " % self.current_value)
        if self.state == UNKNOWN:
            lines.append("State: Unknown ")
        elif self.state == OUTSTANDING:
            lines.append("State: Outstanding ")
        elif self.state == CLEARED:
            lines.append("State: Cleared ")
        elif self.state == VOID:
             lines.append("State: Void ")
        else:
            lines.append("State: ??  ")
        if self.comment:
            lines.append("Comment: %1s " % string_limit(self.comment, 10))
        if self.memo:
            lines.append("Memo: %1s " % string_limit(self.memo, 10))
        return " ".join(lines)

    def __gt__(self, other):
        if self.sched_date != None and other.sched_date != None:
            return self.sched_date > other.sched_date
        elif self.sched_date != None:
            return False
        else:
            return True

    def __lt__(self, other):
        if self.sched_date != None and other.sched_date != None:
            return self.sched_date < other.sched_date
        elif self.sched_date != None:
            return False
        else:
            return True

    def qif_repr(self):
        lines = []
        lines.append("S%s" % self.sched_date.formatUS())
        lines.append("D%s" % self.due_date.formatUS())
        lines.append("T%.2f" % self.amount)
        lines.append("A%s" % self.state)
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

    def set_current_value(self, rest):
        if rest == None:
            self.current_value = None
        else:
            try:
                self.current_value = round(float(rest), 2)
            except:
                self.current_value = 0.0

    def set_sched_date(self, rest):
        if rest != None:
            if type(rest) is str:
                if len(rest) != 0 and rest != "":
                    try:
                        [year, month, day] = Date.get_date_fields(self, rest)
                        self.sched_date = wx.DateTime.FromDMY(day, month-1, year).Format(self.dateFormat)
                    except:
                        error = "Invalid sched_date entered: %s - try again!" % (rest)
                        Date.MsgBox(self.parent, error)
            elif type(rest) is dict:
                self.sched_date = wx.DateTime.FromDMY(rest['day'], rest['month'], rest['year']).Format(self.dateFormat)
            else:
                self.sched_date = wx.DateTime.FromDMY(rest.day, rest.month-1, rest.year).Format(self.dateFormat)
        else:
            self.sched_date = None

    def set_due_date(self, rest):
        if rest != None:
            if type(rest) is str:
                if len(rest) != 0 and rest != "":
                    try:
                        [year, month, day] = Date.get_date_fields(self, rest)
                        self.due_date = wx.DateTime.FromDMY(day, month-1, year).Format(self.dateFormat)
                    except:
                        error = "Invalid due_date entered: %s - try again!" % (rest)
                        Date.MsgBox(self.parent.get_transaction_frame(), error)
                else:
                    self.due_date = None
            elif type(rest) is dict:
               self.due_date = wx.DateTime.FromDMY(rest['day'], rest['month'], rest['year']).Format(self.dateFormat)
            else:
                self.due_date = wx.DateTime.FromDMY(rest.day, rest.month-1, rest.year).Format(self.dateFormat)

    def set_payee(self, rest):
        self.payee = rest

    def set_comment(self, rest):
        if rest == None or rest == "None":
            self.comment = None
        else:
            self.comment = rest

    def set_memo(self, rest):
        if rest == None or rest == "None":
            self.memo = None
        else:
            self.memo = rest

    def set_check_num(self, rest):
        self.check_num = None
        if rest != None:
            self.check_num = rest
        return

    def set_state(self, rest):
        rest = str(rest).upper()
        if rest == "UNKNOWN":
            self.state = UNKNOWN
        elif rest == "OUTSTANDING":
            self.state = OUTSTANDING
        elif rest == "CLEARED":
            self.state = CLEARED
        elif rest == "VOID":
            self.state = VOID
        elif rest == "RECONCILED":
            self.state = RECONCILED
        return

    def set_prev_state(self, rest):
        rest = str(rest).upper()
        if rest == "UNKNOWN":
            self.prev_state = UNKNOWN
        elif rest == "OUTSTANDING":
            self.prev_state = OUTSTANDING
        elif rest == "CLEARED":
            self.prev_state = CLEARED
        elif rest == "VOID":
            self.prev_state = VOID
        elif rest == "RECONCILED":
            self.prev_state = RECONCILED
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

    def get_current_value(self):
        if self.current_value:
            return self.current_value
        else:
            return 0.0

    def get_comment(self):
        return self.comment

    def get_memo(self):
        return self.memo

    def get_check_num(self):
        return self.check_num

    def get_state(self):
        return_value = "??"
        if self.state == UNKNOWN:
            return_value = "unknown"
        elif self.state == OUTSTANDING:
            return_value = "outstanding"
        elif self.state == CLEARED:
            return_value = "cleared"
        elif self.state == VOID:
            return_value = "void"
        elif self.state == RECONCILED:
            return_value = "reconciled"
        return return_value

    def get_prev_state(self):
        return_value = "??"
        if self.prev_state == UNKNOWN:
            return_value = "unknown"
        elif self.prev_state == OUTSTANDING:
            return_value = "outstanding"
        elif self.prev_state == CLEARED:
            return_value = "cleared"
        elif self.prev_state == VOID:
            return_value = "void"
        elif self.prev_state == RECONCILED:
            return_value = "reconciled"
        return return_value

    def assetchange(self, which_column, new_value):
        print("Transaction: ", self.get_payee(), "Recieved notification that column", which_column, "changed", ", new_value", new_value)
