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
#  06/11/2016     Initial version v0.1
#  08/07/2021     Version v0.2

import re
import wx
from Date import Date

# Transaction States
UNKNOWN = 0
OUTSTANDING = 1
SCHEDULED = 2
BUDGETED = 3
CLEARED = 4
VOID = 5
RECONCILED = 6

# Transaction Payment Methods
# While UNKNOWN is a valid method, it is already defined as 0 above
DIRECT_DEPOSIT = 1
AUTOPAY = 2
CHECK = 3
SCHED_ONLINE = 4
PENDING = 5
CASH = 6
TBD = 7
MANUAL = 8

def string_limit(mystr, limit):
    if mystr and len(mystr) > limit:
        mystr = mystr[:limit]
    return mystr

class Transaction:
    def __init__(self, parent, payee=None, action=None, sched_date=None, due_date=None, pmt_method='unknown', amount=None, state='unknown' ):
        self.parent = parent
        if self.parent != None:
            self.assetFrame = self.parent.parent
        else:
            self.assetFrame = None
        self.dateFormat = Date.get_global_date_format(self)
        self.dateSep = Date.get_global_date_sep(self)
        self.set_pmt_method(pmt_method)
        self.check_num = None
        self.set_payee(payee)
        self.set_amount(amount)
        self.set_action(action)
        self.current_value = None
        self.projected_value = None
        self.set_sched_date(sched_date)
        self.set_due_date(due_date)
        self.set_state(state)
        self.prev_state = 'unknown'
        self.comment = None
        self.memo = None

    transaction_fields = [ "Payee", "Action", "Amount", "Due Date", "Sched Date", "Pmt Method" ]

    def get_asset_frame(self):
        return self.assetFrame

    def set_asset_frame(self, assetFrame):
        self.assetFrame = assetFrame

    def get_transaction_fields():
        return Transaction.transaction_fields

    def __str__(self):
        line = []
        line.append("Sched date: %1s " % self.get_sched_date())
        line.append("Due date: %1s " % self.get_due_date())
        line.append("Pmt method: %1s " % self.get_pmt_method())
        line.append("Check_num: %1s " % self.get_check_num())
        line.append("Payee: %1s " % string_limit(self.get_payee(), 40))
        line.append("Amount: %4.2f " % self.get_amount())
        line.append("Action: %s " % self.get_action())
        line.append("Curr Value: %4.2f " % self.get_current_value())
        line.append("Proj Value: %4.2f " % self.get_projected_value())
        line.append("State: %1s " % self.get_state())
        line.append("Comment: %1s " % string_limit(self.get_comment(), 10))
        line.append("Memo: %1s " % string_limit(self.get_memo(), 10))
        return " ".join(line)

    def __gt__(self, other):
        if self.due_date != None and other.due_date != None:
            date_self = Date.parse_date(self,self.due_date,self.dateFormat)
            date_other = Date.parse_date(self,other.due_date,other.dateFormat)
            return date_self["dt"] > date_other["dt"]
        elif self.due_date != None:
            return False
        else:
            return True

    def __ge__(self, other):
        if self.due_date != None and other.due_date != None:
            date_self = Date.parse_date(self,self.due_date,Date.get_global_date_format)
            date_other = Date.parse_date(self,other.due_date,Date.get_global_date_format)
            return date_self["dt"] >= date_other["dt"]
        elif self.due_date != None:
            return False
        else:
            return True

    def __lt__(self, other):
        if self.due_date != None and other.due_date != None:
            date_self = Date.parse_date(self,self.due_date,Date.get_global_date_format)
            date_other = Date.parse_date(self,other.due_date,Date.get_global_date_format)
            return date_self["dt"] < date_other["dt"]
        elif self.due_date != None:
            return False
        else:
            return True

    def __le__(self, other):
        if self.due_date != None and other.due_date != None:
            date_self = Date.parse_date(self,self.due_date,Date.get_global_date_format)
            date_other = Date.parse_date(self,other.due_date,Date.get_global_date_format)
            return date_self["dt"] <= date_other["dt"]
        elif self.due_date != None:
            return False
        else:
            return True

    def getDateFormat(self):
        return self.dateFormat

    def setDateFormat(self, newDateFormat):
        self.dateFormat = Date.set_global_date_format(Date, newDateFormat)

    def qif_repr(self):
        lines = []
        lines.append("S%s" % self.get_sched_date())
        lines.append("D%s" % self.get_due_date())
        lines.append("T%4.2f" % self.get_amount())
        lines.append("A%s" % self.get_state())
        lines.append("N%1s" % self.get_check_num())
        lines.append("P%s" % self.get_payee())
        lines.append("L%s" % self.get_comment())
        memo_line = "";
        pmt_method = self.get_pmt_method()
        if pmt_method != "":
            if memo_line != "":
                memo_line += ";"
            memo_line += "P%s" % (pmt_method)
        action = self.get_action()
        if action != "":
            if memo_line != "":
                memo_line += ";"
            memo_line += "A%s" % (action)
        current_value = self.get_current_value()
        if current_value != 0.0:
            if memo_line != "":
                memo_line += ";"
            memo_line += "V%s" % (str(current_value))
        projected_value = self.get_projected_value()
        if projected_value != 0.0:
            if memo_line != "":
                memo_line += ";"
            memo_line += "J%s" % (str(projected_value))
        state = self.get_state()
        if state != "":
            if memo_line != "":
                memo_line += ";"
            memo_line += "S%s" % (state)
        prev_state = self.get_prev_state()
        if prev_state != "":
            if memo_line != "":
                memo_line += ";"
            memo_line += "T%s" % (prev_state)
        memo = self.get_memo()
        if memo != "":
            if memo_line != "":
                memo_line += ";"
            memo_line += "M%s" % (memo)
        if memo_line != "":
            lines.append("M%s" % memo_line)         # Use Memo field for parsable string of info for this transaction
        lines.append("^")
        return '\n'.join(lines)

    def set_pmt_method(self,rest):
        if type(rest) is str:
            rest = rest.upper()
            if "UNKNOWN" in rest:
                self.pmt_method = UNKNOWN
            elif "DIRECT DEPOSIT" in rest:
                self.pmt_method = DIRECT_DEPOSIT
            elif "AUTOPAY" in rest:
                self.pmt_method = AUTOPAY
            elif "CHECK" in rest:
                self.pmt_method = CHECK
            elif "SCHED ONLINE" in rest:
                self.pmt_method = SCHED_ONLINE
            elif "PENDING" in rest:
                self.pmt_method = PENDING
            elif "CASH" in rest:
                self.pmt_method = CASH
            elif "TBD" in rest:
                self.pmt_method = TBD
            elif "MANUAL" in rest:
                self.pmt_method = MANUAL
        elif type(rest) is int:
            self.state = rest
        else:
            print("State: " + rest + " not known - setting to UNKNOWN")
            self.state = UNKNOWN
        return self.pmt_method

    def set_amount(self, rest):
        if rest == None:
            rest = 0.0
        temp = rest
        if type(rest) == str:
            temp = float(temp.replace('$','').replace(',',''))
        try:
            self.amount = round(temp,2)
        except:
            print("Error setting amount to ", rest)
            print("transaction: ", self)
            self.MsgBox("Error setting amount to ", rest, " See error log for more details!")
            self.amount = 0.0
        return self.amount

    def set_action(self, rest):
        self.action = rest
        return self.action

    def set_current_value(self, rest):
        if rest == None:
            self.current_value = None
        else:
            try:
                self.current_value = round(float(rest), 2)
            except:
                print("Error setting current value to ", rest)
                print("transaction: ", self)
                self.MsgBox("Error setting current value to ", rest, " See error log for more details!")
                self.current_value = 0.0
        return self.current_value

    def set_projected_value(self, rest):
        if rest == None:
            self.projected_value = None
        else:
            try:
                self.projected_value = round(float(rest), 2)
            except:
                self.projected_value = 0.0
        return self.projected_value

    def set_sched_date(self, rest):
        if rest != None:
            global_date_format = Date.get_global_date_format(Date)
            if type(rest) is str:
                in_date_format = Date.guessDateFormat(Date, rest)
                if in_date_format != global_date_format:
                    rest = Date.convertDateFormat(Date, rest, in_date_format, global_date_format)
            self.sched_date = Date.parse_date(self, rest, global_date_format)
        else:
            self.sched_date = None
        return self.sched_date

    def set_due_date(self, rest):
        if rest != None:
            global_date_format = Date.get_global_date_format(Date)
            if type(rest) is str:
                in_date_format = Date.guessDateFormat(Date,rest)
                if in_date_format != global_date_format:
                    rest = Date.convertDateFormat(Date, rest, in_date_format, global_date_format)
            self.due_date = Date.parse_date(self, rest, Date.get_global_date_format(Date))
        else:
            self.due_date = None
        return self.due_date

    def set_payee(self, rest):
        if rest == None or rest == "None":
            self.payee = None
        else:
            self.payee = rest
        return self.payee

    def set_comment(self, rest):
        if rest == None or rest == "None":
            self.comment = None
        else:
            self.comment = rest
        return self.comment

    def set_memo(self, rest):
        if rest == None or rest == "None":
            self.memo = None
        else:
            self.memo = rest
        return self.memo

    def set_check_num(self, rest):
        self.check_num = None
        if rest != None:
            self.check_num = rest
        return self.check_num
    
    def set_state(self, rest):
        if type(rest) is str:
            rest = rest.upper()
            if "UNKNOWN" in rest:
                self.state = UNKNOWN
            elif "OUTSTANDING" in rest:
                self.state = OUTSTANDING
            elif "SCHEDULED" in rest:
                self.state = SCHEDULED
            elif "BUDGETED" in rest:
                self.state = BUDGETED
            elif "CLEARED" in rest:
                self.state = CLEARED
            elif "VOID" in rest:
                self.state = VOID
            elif "RECONCILED" in rest:
                self.state = RECONCILED
        elif type(rest) is int:
            self.state = rest
        else:
            print("State: " + rest + " not known - setting to UNKNOWN")
            self.state = UNKNOWN
        return self.state

    def set_prev_state(self, rest):
        rest = str(rest).upper()
        if rest == "UNKNOWN":
            self.prev_state = UNKNOWN
        elif rest == "OUTSTANDING":
            self.prev_state = OUTSTANDING
        elif rest == "SCHEDULED":
            self.prev_state = SCHEDULED
        elif rest == "BUDGETED":
            self.prev_state = BUDGETED
        elif rest == "CLEARED":
            self.prev_state = CLEARED
        elif rest == "VOID":
            self.prev_state = VOID
        elif rest == "RECONCILED":
            self.prev_state = RECONCILED
        return self.prev_state

    def get_pmt_method(self):
        return_value = ""
        val = -1
        try:
            val = self.pmt_method
        except:
            pass
        if val == UNKNOWN:
            return_value = "unknown"
        elif val == DIRECT_DEPOSIT:
            return_value = "Direct Deposit"
        elif val == AUTOPAY:
            return_value = "AutoPay"
        elif val == CHECK:
            return_value = "Check"
        elif val == SCHED_ONLINE:
            return_value = "sched online"
        elif val == PENDING:
            return_value = "pending"
        elif val == CASH:
            return_value = "Cash"
        elif val == TBD:
            return_value = "TBD"
        elif val == MANUAL:
            return_value = "manual"
        return return_value

    def get_sched_date(self):
        return_value = ""
        try:
            return_value = self.sched_date["str"]
        except:
            pass
        return return_value

    def get_due_date(self):
        return_value = ""
        try:
            return_value = self.due_date["str"]
        except:
            pass
        return return_value

    def get_payee(self):
        ret_val = ""
        try:
            ret_val = self.payee
        except :
            pass
        return ret_val

    def get_amount(self):
        ret_val = 0.0
        try:
            ret_val = self.amount
        except :
            pass
        return ret_val

    def get_action(self):
        return self.action

    def get_current_value(self):
        if self.current_value:
            return self.current_value
        else:
            return 0.0

    def get_projected_value(self):
        if self.projected_value:
            return self.projected_value
        else:
            return 0.0

    def get_comment(self):
        ret_val = ""
        try:
            ret_val = self.comment
        except:
            pass
        return ret_val

    def get_memo(self):
        ret_val = ""
        try:
            ret_val = self.memo
        except:
            pass
        return ret_val

    def get_check_num(self):
        ret_val = ""
        try:
            ret_val = str(self.check_num)
        except :
            pass
        return ret_val

    def get_state(self):
        return_value = ""
        if self.state == UNKNOWN:
            return_value = "unknown"
        elif self.state == OUTSTANDING:
            return_value = "outstanding"
        elif self.state == SCHEDULED:
            return_value = "scheduled"
        elif self.state == BUDGETED:
            return_value = "budgeted"
        elif self.state == CLEARED:
            return_value = "cleared"
        elif self.state == VOID:
            return_value = "void"
        elif self.state == RECONCILED:
            return_value = "reconciled"
        return return_value

    def get_prev_state(self):
        return_value = ""
        if self.prev_state == UNKNOWN:
            return_value = "unknown"
        elif self.prev_state == OUTSTANDING:
            return_value = "outstanding"
        elif self.prev_state == SCHEDULED:
            return_value = "scheduled"
        elif self.prev_state == BUDGETED:
            return_value = "budgeted"
        elif self.prev_state == CLEARED:
            return_value = "cleared"
        elif self.prev_state == VOID:
            return_value = "void"
        elif self.prev_state == RECONCILED:
            return_value = "reconciled"
        return return_value

    def assetchange(self, which_column, new_value):
        print("Transaction: ", self.get_payee(), "Recieved notification that column", which_column, "changed", ", new_value", new_value)
        
    def MsgBox(self, message):
        d = wx.MessageDialog(self.parent, message, "error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()
