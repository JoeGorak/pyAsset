#!/usr/bin/env /usr/local/bin/pythonw
"""
INSTALLATION/REQUIREMENTS
PyAsset requires Python (>=3.7) and wxPython.

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
import wx.adv
import re

from Date import Date
from wx.core import DateTime

class PropertyForm(wx.Panel):
    ''' The PropertyForm class is a wx.Panel that creates a bunch of controls
        and handlers for callbacks. Doing the layout of the controls is
        the responsibility of subclasses (by means of the doLayout() method).
    '''

    def __init__(self, parent, in_dateFormat, in_payType, in_refDate, in_netpay, in_payDepositAcct):
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
        self.date_format = self.dateFormats[self.dateFormatChoice]
        Date.set_global_date_format(self, self.date_format)
        self.date_format = Date.get_global_date_format(self)
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
#        self.refPayDatePicker = wx.adv.DatePickerCtrl(self,        
#                                                      pos=(0,0),
#                                                      size=(180,30),
#                                                      style=wx.adv.DP_DROPDOWN)
        self.refPayDateTextCtrl = wx.TextCtrl(self,
                                              pos=(0,0),
                                              size=(150,30),
                                              style=wx.TE_PROCESS_ENTER)
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
        if ref_date_type is str or ref_date_type is DateTime:
            if self.NewDateFormatChoice != self.dateFormatChoice:
                ref_date_parsed = Date.parse_date(self, self.ref_date, self.dateFormat)
                ref_date = Date.convertDateFormat(self, ref_date_parsed, self.dateFormat, self.NewDateFormat)
#            self.refPayDatePicker.SetValue(ref_date["dt"])
#            self.refPayDatePicker.Refresh()
            self.refPayDateTextCtrl.LabelText = self.NewRefDate
            self.refPayDateTextCtrl.SetValue(self.NewRefDate)
            self.refPayDateTextCtrl.Refresh()
        else:
            self.MsgBox("Unknown ref date type %s ignored - ref date info ignored" % (type(self.ref_date)))
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
                 (self.refPayDateTextCtrl, wx.EVT_TEXT_ENTER, self.onRefPayDateEntered),
                 (self.refPayDateTextCtrl, wx.EVT_KILL_FOCUS, self.onRefPayDateLostFocus),
#                 (self.refPayDatePicker, wx.adv.EVT_DATE_CHANGED, self.onRefPayDatePicked),      # JJG 12/23/2023   Causes lockups!
                 (self.dateFormatRadioBox, wx.EVT_RADIOBOX, self.onDateFormatChanged),
                 (self.payTypeRadioBox, wx.EVT_RADIOBOX, self.onPayTypeChanged),
                 (self.payAcctCtrl, wx.EVT_CHOICE, self.onDepositAcctChanged)]:
            control.Bind(event, handler)


    # Callback methods:

    def onDateFormatChanged(self, event):
        self.dateFormat = self.dateFormats[self.dateFormatChoice]
        self.dateFormatChoice = event.GetInt()
        self.NewDateFormat = self.dateFormats[self.NewDateFormatChoice]
        self.__log('Desired date format: %s' % self.NewDateFormat)
        self.NewRefDate = Date.convertDateFormat(self, self.NewRefDate, self.dateFormat, self.NewDateFormat)
        self.refPayDateTextCtrl.LabelText = self.NewRefDate["str"]
        self.refPayDateTextCtrl.Refresh()
#        self.refPayDatePicker.SetValue(self.ref_date["dt"])
#        self.refPayDatePicker.Refresh()

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

    def onNetPayLostFocus(self, event):
        in_netpay = self.netPayTextCtrl.GetValue()
        self.processNetPay(in_netpay)
        event.Skip()

    def updateRefPayDateControls(self, ref_date, how):
        self.NewRefDate = ref_date["str"]
        self.__log("User %s ref pay date: %s" % (how, self.NewRefDate))      
#        self.refPayDatePicker.SetValue(ref_date["dt"])
#        self.refPayDatePicker.Refresh
        self.refPayDateTextCtrl.LabelText = self.NewRefDate
        self.refPayDateTextCtrl.SetValue(self.NewRefDate)
        self.refPayDateTextCtrl.Refresh()

    def processRefDate(self, ref_date):
        dateFormat = self.date_format
        NewDateFormat = self.dateFormats[self.NewDateFormatChoice]
        ref_date_parsed = Date.parse_date(self, ref_date, NewDateFormat)
        if ref_date_parsed != None:
            ref_date = Date.convertDateFormat(self, ref_date_parsed, dateFormat, NewDateFormat)
            self.__log("Month: %02d, Day: %02d, Year: %04d" % (ref_date_parsed["month"], ref_date_parsed["day"], ref_date_parsed["year"]))
            self.updateRefPayDateControls(ref_date, "entered")
            print(ref_date)
            self.ref_date = ref_date
        else:
            dateFormat = dateFormat.replace("%y", "yy").replace("%m", "mm").replace("%d", "dd").replace("%Y", "yyyy")
            error = "Bad input reference date (%s) entered - format is %s - try again" % (ref_date, dateFormat)
            self.MsgBox(error)

    def onRefPayDateEntered(self, event):
        ref_date = event.String
        self.processRefDate(ref_date)

    def onRefPayDateLostFocus(self, event):
        ref_date = self.refPayDateTextCtrl.GetValue()
        self.processRefDate(ref_date)
        event.Skip()

    def onRefPayDatePicked(self, event):                        # JJG 12/26/2023 Not sure this is still correct
        year = event.Date.year
        month = event.Date.month
        day = event.Date.day
        self.__log("Month: %02d, Day: %02d, Year: %04d" % (month+1, day, year))
        ref_date = wx.DateTime.FromDMY(day, month, year)
        dateFormat = Date.get_date_format(self)
        ref_date_parsed = Date.parse_date(self, ref_date, dateFormat)
        if ref_date_parsed != None:
            ref_date = Date.convertDateFormat(self, ref_date_parsed, dateFormat, dateFormat)
            self.updateRefPayDateControls(ref_date, "picked") 
            print(ref_date)
            self.ref_date = ref_date
        else:
            dateFormat = dateFormat.replace("%y", "yy").replace("%m", "mm").replace("%d", "dd").replace("%Y", "yyyy")
            error = "Bad input reference date (%s) picked - format is %s - try again" % (ref_date, dateFormat)
            self.MsgBox(error)

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
            self.dateFormat = self.dateFormats[self.NewDateFormatChoice]
            Date.set_global_date_format(self, self.dateFormat)
            Date.set_global_date_sep(self, self.dateSep)
            payType = self.payType
            self.assetFrame.setPayType(payType)
            ref_date = self.NewRefDate
            self.assetFrame.setRefDate(ref_date)
            netpay = self.NewNetpay
            self.assetFrame.setNetPay(netpay)
            payDepositAcct = self.NewpayDepositAcct
            self.assetFrame.setPayDepositAcct(payDepositAcct)
            print("%s, %s, %s, %s, %s" % (self.dateFormat, payType, ref_date, netpay, payDepositAcct))
            self.Parent.Destroy()
            return True

    def onAbort(self, event):
        self.Parent.Destroy()
        return False

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
                 # For testing, Have separete Text control and Date Picker.... if it works want to change so TextCtrl overlays text portion of Date Picker JJG 08/08/2021
                 (self.refPayDate, expandOption),
                 (self.refPayDateTextCtrl, noOptions),
#                 (self.refPayDatePicker, noOptions),
                 emptySpace,
                 (self.payAcct, expandOption),
                 (self.payAcctCtrl, expandOption),
                 emptySpace
                ]:
            gridSizer.Add(control, **options)

        #for control, options in \
        #        [
        #         (self.refPayDate, expandOption),
        #         (self.refPayDateTextCtrl, noOptions),
        #         (self.refPayDatePicker, noOptions),
        #       ]:
        #    dateGridSizer.Add(control, **options)

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
