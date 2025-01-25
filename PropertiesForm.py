#!/usr/bin/env /usr/local/bin/pythonw
"""
INSTALLATION/REQUIREMENTS
PyAsset requires Python (>=3.7) and wxPython.

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
#  07/15/2024     Version v0.3               Replaced date picker text with minidatepicker widget from Stack Overflow (see minidatepicker.py)

import wx
import wx.adv
import re
import minidatepicker

from Date import Date
from wx.core import DateTime

class PropertyForm(wx.Panel):
    ''' The PropertyForm class is a wx.Panel that creates a bunch of controls
        and handlers for callbacks. Doing the layout of the controls is
        the responsibility of subclasses (by means of the doLayout() method).
    '''

    def __init__(self, parent, in_dateFormat, in_payType, in_refDate, in_netpay, in_payDepositAcct):
        self.oldDateFormat = in_dateFormat
        self.oldPayType = in_payType
        self.oldRefDate = in_refDate
        self.oldNetPay = in_netpay
        self.oldPayDepositAcct = in_payDepositAcct
        self.parent = parent
        super(PropertyForm, self).__init__(parent)
        self.assetFrame = self.GetGrandParent()
        self.dateFormats = Date.getDateFormats(self)
        self.dateSep = Date.get_global_date_sep(self)
        if in_dateFormat != "":
            try:
                self.dateFormatChoice = self.dateFormats.index(in_dateFormat)
            except:
                self.dateFormatChoice = -1
            if self.dateFormatChoice == -1:
                self.dateFormatChoice = 0
                self.MsgBox("Unknown date format %s ignored - default to %s" % (in_dateFormat, self.dateFormats[self.dateFormatChoice]))
        else:
            self.dateFormatChoice = 0
        self.dateFormat = self.dateFormats[self.dateFormatChoice]
        Date.set_global_date_format(Date, self.dateFormat)
        self.dateFormat = Date.get_global_date_format(Date)
        self.payTypes = self.assetFrame.get_pay_types()
        self.payType = in_payType
        if in_payType == "":
           self.payType = self.assetFrane.get_default_pay_type()
        else:
           if type(in_payType) is not int:
                try:
                    self.payType = self.payTypes.index(in_payType)
                except:
                    self.payType = self.assetFrame.get_default_pay_type()
        if type(self.payType) is str:
            self.payType = self.payTypes.index(self.payType)
        if in_refDate != "":
            self.ref_date = in_refDate
        else:
            self.ref_date = "12/20/2023"                # JJG  12/23/2023   added default if none given
        if in_netpay != "":
            self.netpay = in_netpay
        else:
            self.netpay = "0.00"
        if in_payDepositAcct != None:
            self.payDepositAcct = in_payDepositAcct
        else:
            self.payDepositAcct = "none"
        self.initNewValues()
        self.createControls()
        self.setControlInitValues()
        self.bindEvents()
        self.doLayout()
        self.Show()
 
    def initNewValues(self):
        self.NewDateFormatChoice = self.dateFormatChoice
        self.NewDateFormat = Date.getDateFormats(self)[self.NewDateFormatChoice]
        self.NewNetpay = self.netpay
        self.NewPayType = self.payType
        self.NewRefDate = self.ref_date
        self.NewpayDepositAcct = self.payDepositAcct

    def createControls(self):
        self.saveButton = wx.Button(self, label="Save")
        self.abortButton = wx.Button(self, label="Abort")
        display_dateFormats = []
        for next_format in Date.getDateFormats(self):
            next_format = next_format.replace("%m", "mm").replace("%d", "dd").replace("%y", "yy").replace("%Y", "yyyy")
            display_dateFormats.append(next_format)
        self.dateFormatRadioBox = wx.RadioBox(self,
                                         label="Format for dates?",
                                         choices=display_dateFormats,
                                         majorDimension=2,
                                         style=wx.RA_SPECIFY_COLS)
        self.netPay = wx.StaticText(self, label="Net pay (take home amount):")
        self.netPayTextCtrl = wx.TextCtrl(self,
                                          style=wx.TE_PROCESS_ENTER,
                                          value="$d,ddd.dd")
        self.refPayDate = wx.StaticText(self, label="Reference pay date:")
        self.payAcct = wx.StaticText(self, label="Direct deposit account:")
        self.payment_accounts = self.Parent.Parent.assets.getPaymentAccounts()
        self.payAcctCtrl = wx.Choice(self,
                                     choices=self.payment_accounts)
        ref_date = Date.parse_date(self, self.oldRefDate, self.oldDateFormat)
        format = (lambda dt: (f'{dt.Format(self.oldDateFormat)}'))
        self.refPayDatePicker = minidatepicker.MiniDatePicker(self, date=ref_date["dt"], formatter=format)
        self.payTypeRadioBox = wx.RadioBox(self,
                                         label="How often are you paid?",
                                         choices=self.payTypes,
                                         majorDimension=3,
                                         style=wx.RA_SPECIFY_COLS)

    def setControlInitValues(self):
        self.dateFormatRadioBox.SetSelection(self.NewDateFormatChoice)
        self.dateFormatRadioBox.Refresh()
        self.netPayTextCtrl.LabelText = self.NewNetpay
        self.netPayTextCtrl.SetValue(self.NewNetpay)
        self.netPayTextCtrl.Refresh()
        ref_date_type = type(self.ref_date)
        format = lambda dt: (dt.Format(self.NewDateFormat))
        self.refPayDatePicker.SetFormatter(format)
        self.refPayDatePicker.SetValue(self.ref_date["str"])
        self.refPayDatePicker.Refresh()
        try:
            self.NewPayDepositChoice = self.payment_accounts.index(self.NewpayDepositAcct)
        except:
            self.NewPayDepositChoice = -1
        if self.NewPayDepositChoice == -1:
            defaultAcct = "none"
            self.NewPayDepositChoice = self.payment_accounts.index(defaultAcct)
            if self.payDepositAcct != "":
                self.MsgBox("Unknown payment account %s ignored - default to %s" % (self.payDepositAcct, defaultAcct))
        self.payAcctCtrl.SetSelection(self.NewPayDepositChoice)
        self.payAcctCtrl.Refresh()
        self.payTypeRadioBox.SetSelection(self.payType)
        self.payTypeRadioBox.Refresh()

    def bindEvents(self):
        for control, event, handler in \
                [(self.saveButton, wx.EVT_BUTTON, self.onSave),
                 (self.abortButton, wx.EVT_BUTTON, self.onAbort),
                 (self.netPayTextCtrl, wx.EVT_TEXT_ENTER, self.onNetPayEntered),
                 (self.netPayTextCtrl, wx.EVT_KILL_FOCUS, self.onNetPayLostFocus),
                 (self.refPayDatePicker, minidatepicker.EVT_DATE_CHANGED, self.onRefPayDatePicked),
                 (self.dateFormatRadioBox, wx.EVT_RADIOBOX, self.onDateFormatChanged),
                 (self.payTypeRadioBox, wx.EVT_RADIOBOX, self.onPayTypeChanged),
                 (self.payAcctCtrl, wx.EVT_CHOICE, self.onDepositAcctChanged)]:
            control.Bind(event, handler)

    # Callback methods:

    def onDateFormatChanged(self, event):
        olddateFormat = self.dateFormat
        dateFormatChoice = event.GetInt()
        self.NewDateFormat = self.dateFormats[dateFormatChoice]
        self.__log('Desired date format: %s' % self.NewDateFormat)
        self.NewRefDate = Date.convertDateFormat(Date, self.NewRefDate, olddateFormat, self.NewDateFormat)
        format = lambda dt: (dt.Format(self.NewDateFormat))
        self.refPayDatePicker.SetValue(self.NewRefDate["dt"])
        self.refPayDatePicker.SetFormatter(format)

    def onPayTypeChanged(self, event):
        self.NewPayType = event.GetInt()
        self.__log('User is paid: %s' % self.payTypes[self.NewPayType])

    def onDepositAcctChanged(self, event):
        payDepositChoice = event.GetInt()
        self.NewpayDepositAcct = self.payment_accounts[payDepositChoice]
        self.__log('Deposit into: %s' % self.NewpayDepositAcct)

    def processNetPay(self, in_netpay):
        money_regex = "^[\\-]*[\$]*[0-9]{1,3}((\,*)[0-9]{3})*[\\.][0-9]{2}$"
        match = re.search(money_regex, in_netpay)
        if match == None:
            self.MsgBox("Bad net pay entered: %s" % (in_netpay))
        else:
            self.NewNetpay = in_netpay.replace("$", "").replace(",", "")
            self.__log('User entered net pay: %s' % self.NewNetpay)
            self.netPayTextCtrl.SetValue(self.NewNetpay)

    def onNetPayEntered(self, event):
        in_netpay = event.GetString()
        self.processNetPay(in_netpay)
        event.Skip()

    def onNetPayLostFocus(self, event):
        in_netpay = self.netPayTextCtrl.GetValue()
        self.processNetPay(in_netpay)
        event.Skip()

    def onRefPayDatePicked(self, event):
        ref_date = event.GetDate()
        dateFormat = Date.get_date_format(self)
        self.ref_date = Date.parse_date(self, ref_date, dateFormat)
        self.NewRefDate = self.ref_date
        self.__log("User picked ref pay date: %s" % (self.NewRefDate["str"]))
        self.refPayDatePicker.SetValue(self.ref_date["dt"])

    # Button action methods

    def onSave(self, event):
        error = ""
        if self.payType == -1:
            error = "Bad pay type"
        else:
            self.payType = self.NewPayType
        if self.ref_date == None:
            if len(error) > 0:
                error = "%s; " % (error)
            error = "%sBad reference date" % (error)
        if self.netpay == None:
            if len(error) > 0:
                error = "%s; " % (error)
            error = "%sBad net pay" % (error)
        if error != "":
            self.MsgBox(error)
        else:
            old_format = self.oldDateFormat
            new_format = self.NewDateFormat
            new_format, new_date_sep = Date.parseDateFormat(Date, new_format)
            if old_format != new_format:
                Date.set_global_date_format(Date, new_format)
                Date.set_global_date_sep(Date, new_date_sep)
                global_proj_date = Date.get_global_proj_date(Date)
                new_global_proj_date = Date.convertDateFormat(Date,global_proj_date,old_format,new_format)
                Date.set_global_proj_date(Date, new_global_proj_date)
                curr_date = self.assetFrame.curr_date
                self.assetFrame.curr_date = Date.convertDateFormat(Date,curr_date,old_format,new_format)             # JJG 1/7/2024 Change current date to new format
                self.assetFrame.proj_date = new_global_proj_date                                                     # JJG 5/26/2024 Change proj_date to new format
            self.NewRefDate = Date.convertDateFormat(Date,self.NewRefDate,old_format,new_format)
            self.assetFrame.setRefDate(self.NewRefDate)
            if self.oldPayType != self.payType:
                self.assetFrame.setPayType(self.payType)
            if self.oldNetPay != self.NewNetpay:
                self.assetFrame.setNetPay(self.NewNetpay)
            if self.oldPayDepositAcct != self.NewpayDepositAcct:
                self.assetFrame.setPayDepositAcct(self.NewpayDepositAcct)
            self.Parent.newDateFormat = new_format
            print("%s, %s, %s, %s, %s" % (self.Parent.newDateFormat, self.payType, self.NewRefDate["str"], self.NewNetpay, self.NewpayDepositAcct))
            self.Parent.Destroy()
            self.assetFrame.update = True

    def onAbort(self, event):
        self.Parent.Destroy()
        self.assetFrame.update = False

    def doLayout(self):
        ''' Layout the controls by means of sizers. '''

        # A GridSizer will contain the input controls (except for the refernce pay date controls)
        gridSizer = wx.FlexGridSizer(rows=20, cols=1, vgap=10, hgap=10)

        # Anothe GridSizer for the reference pay date controls (done to allow string portion of datePicker control to be overlayed)
        dateGridSizer = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)

        # Aother GridSizer has the Save and Abort buttons
        buttonGridSizer = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)

        # Add the controls to the sizers:
        for control, options in \
                [emptySpace,
                (self.netPay, expandOption),
                 (self.netPayTextCtrl, expandOption),
                 (self.payTypeRadioBox, expandOption),
                 (self.dateFormatRadioBox, expandOption),
                 (self.refPayDate, expandOption),
                 (self.refPayDatePicker, noOptions),
                 emptySpace,
                 (self.payAcct, expandOption),
                 (self.payAcctCtrl, expandOption),
                 emptySpace
                ]:
            gridSizer.Add(control, **options)

        for control, options in \
                [(self.saveButton, noOptions),
                 (self.abortButton, noOptions)
                 ]:
            buttonGridSizer.Add(control, **options)

        mainSizer = wx.BoxSizer(orient=wx.VERTICAL)
        for control, options in \
            [
                (gridSizer, dict(border=5, flag=wx.ALL)),
                (buttonGridSizer, dict(border=5, flag=wx.ALL|wx.ALIGN_CENTER))
            ]:
            mainSizer.Add(control, **options)

        self.SetSizerAndFit(mainSizer)

    # Helper method(s):

    def MsgBox(self, message):
        d = wx.MessageDialog(self, message, "error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()

    def __log(self, message):
        ''' Private method to print a string to the console
            control. (Only used for debugging and turned off for now! JJG 7/25/2021)'''
        if True:                         # Change this to True to print out debug messages
            print('%s' % message)

class PropertyFrameWithForm(wx.Dialog):
    def __init__(self, parent, in_dateFormat="", in_payType="", in_refDate="", in_netpay="", in_payDepositAcct=""):
        super(PropertyFrameWithForm, self).__init__(parent)
        self.SetTitle('Properties Form')
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        PropertyForm(self, in_dateFormat, in_payType, in_refDate, in_netpay, in_payDepositAcct)
        # We just set the frame to the right size manually. This is feasible
        # for the frame since the frame contains just one component. If the
        # frame had contained more than one component, we would use sizers
        # of course, as demonstrated in the PropertyForm class above (see doLayout).
        self.SetClientSize(self.GetBestSize())
