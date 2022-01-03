"""
INSTALLATION/REQUIREMENTS
PyAsset requires Python (>=3.7) and wxPython.

COPYRIGHT/LICENSING
Copyright (c) 2017-2022 Joseph J. Gorak. All rights reserved.
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

import wx
import re
from Date import Date

class myForm(wx.Panel):
    ''' The Form class is a wx.Panel that creates a bunch of controls
        and handlers for callbacks. Doing the layout of the controls is
        the responsibility of subclasses (by means of the doLayout() method).
    '''

    def __init__(self, parent, in_dateFormat="", in_payType="", in_refDate="", in_netpay="", in_payDepositAcct="none"):
        self.parent = parent
        super(myForm, self).__init__(parent)
        self.assetFrame = self.GetGrandParent()
        self.dateFormats = ['%m/%d/%Y', "%Y/%m/%d"]
        if in_dateFormat != "":
            try:
                self.dateFormatChoice = self.dateFormats.index(in_dateFormat)
            except:
                self.dateFormatChoice = -1
            if self.dateFormatChoice == -1:
                today = self.parent.Parent.curr_date
                if today.index("/") == 4:
                    self.dateFormatChoice = 1
                else:
                    self.dateFormatChoice = 0
                defaultDateFormat = self.dateFormats[self.dateFormatChoice].replace("%m", "mm").replace("%d", "dd").replace("%y", "yy").replace("%Y", "yyyy")
                self.MsgBox("Unknown date format %s ignored - default to %s" % (in_dateFormat, defaultDateFormat))
        else:
            self.dateFormatChoice = 0
        self.dateFormat = self.dateFormats[self.dateFormatChoice]
        self.inDateFormat = self.dateFormats[self.dateFormatChoice]
        self.payTypes = ['every week', 'every 2 weeks', 'monthly']
        if in_payType != "":
            try:
                self.payType = self.payTypes.index(in_payType)
            except:
                self.payType = -1
            if self.payType == -1:
                self.payType = 1
                self.MsgBox("Unknown pay frequency %s ignored - default to %s" % (in_payType, self.payTypes[self.payType]))
        else:
            self.payType = 1
        self.ref_date = in_refDate
        self.netpay = in_netpay
        self.payDepositAcct = in_payDepositAcct
        self.createControls()
        self.setControlInitValues()
        self.bindEvents()
        self.doLayout()

    def createControls(self):
        self.saveButton = wx.Button(self, label="Save")
        self.abortButton = wx.Button(self, label="Abort")
        display_dateFormats = []
        for next_format in self.dateFormats:
            next_format = next_format.replace("%m", "mm").replace("%d", "dd").replace("%y", "yy").replace("%Y", "yyyy")
            display_dateFormats.append(next_format)
        self.dateFormatRadioBox = wx.RadioBox(self,
                                         label="Format for dates?",
                                         choices=display_dateFormats,
                                         majorDimension=2,
                                         style=wx.RA_SPECIFY_COLS)
        self.netPay = wx.StaticText(self, label="Net pay (take home amount):")
        self.netPayTextCtrl = wx.TextCtrl(self,
                                          style = wx.TE_PROCESS_ENTER,
                                          value="$d,ddd.dd")
        self.refPayDate = wx.StaticText(self, label="Reference pay date:")
        self.payAcct = wx.StaticText(self, label="Direct deposit account:")
        self.payment_accounts = self.Parent.Parent.assets.getPaymentAccounts()
        self.payAcctCtrl = wx.Choice(self,
                                     choices=self.payment_accounts)
        self.refPayDateTextCtrl = wx.TextCtrl(self,
                                              style=wx.TE_PROCESS_ENTER,
                                              value=self.dateFormat)
        self.payTypeRadioBox = wx.RadioBox(self,
                                         label="How often are you paid?",
                                         choices=self.payTypes,
                                         majorDimension=3,
                                         style=wx.RA_SPECIFY_COLS)

    def setControlInitValues(self):
        self.dateFormatRadioBox.SetSelection(self.dateFormatChoice)
        self.dateFormatRadioBox.Refresh()
        self.netPayTextCtrl.LabelText = self.netpay
        self.netPayTextCtrl.Refresh()
        self.refPayDateTextCtrl.LabelText = self.ref_date
        self.refPayDateTextCtrl.Refresh()
        self.payAcct.Refresh()
        try:
            self.payDepositChoice = self.payment_accounts.index(self.payDepositAcct)
        except:
            self.payDepositChoice = -1
        if self.payDepositChoice == -1:
            self.payDepositChoice = 0
            self.MsgBox("Unknown payment account %s ignored - default to %s" % (self.payDepositAcct, self.payment_accounts[self.payDepositChoice]))
        self.payAcctCtrl.SetSelection(self.payDepositChoice)
        self.payAcctCtrl.Refresh()
        self.payTypeRadioBox.SetSelection(self.payType)
        self.payTypeRadioBox.Refresh()

    def bindEvents(self):
        for control, event, handler in \
                [(self.saveButton, wx.EVT_BUTTON, self.onSave),
                 (self.abortButton, wx.EVT_BUTTON, self.onAbort),
                 (self.netPayTextCtrl, wx.EVT_TEXT_ENTER, self.onNetPayEntered),
                 (self.refPayDateTextCtrl, wx.EVT_TEXT_ENTER, self.onRefPayDateEntered),
                 (self.dateFormatRadioBox, wx.EVT_RADIOBOX, self.onDateFormatchanged),
                 (self.payTypeRadioBox, wx.EVT_RADIOBOX, self.onPayTypechanged),
                 (self.payAcctCtrl, wx.EVT_CHOICE, self.onDepositAcctChanged)]:
            control.Bind(event, handler)

    # Callback methods:

    def onDateFormatchanged(self, event):
        self.inDateFormat = self.dateFormats[self.dateFormatChoice]
        self.dateFormatChoice = event.GetInt()
        self.dateFormat = self.dateFormats[self.dateFormatChoice]
        self.__log('Desired date format: %s' % self.dateFormat)
#        print("Ref date:")
        self.ref_date = Date.convertDateFormat(self, self.ref_date, self.inDateFormat, self.dateFormat)
        self.refPayDateTextCtrl.LabelText = self.ref_date
        self.refPayDateTextCtrl.Refresh()

    def onPayTypechanged(self, event):
        self.payType = event.GetInt()
        self.__log('User is paid: %s' % self.payTypes[self.payType])

    def onDepositAcctChanged(self, event):
        self.payDepositChoice = event.GetInt()
        self.payDepositAcct = self.payment_accounts[self.payDepositChoice]
        self.__log('Deposit into: %s' % self.payDepositAcct)

    def onNetPayEntered(self, event):
        money_regex = "^[\\-]*[\$]*[0-9]{1,3}((\,*)[0-9]{3})*[\\.][0-9]{2}$"
        in_netpay = event.GetString()
        match = re.search(money_regex, in_netpay)
        if match == None:
            self.MsgBox("Bad net pay entered: %s" % (in_netpay))
        else:
            self.netpay = in_netpay.replace("$", "").replace(",", "")
            self.__log('User entered net pay: %s' % self.netpay)

    def onRefPayDateEntered(self, event):
        in_date = event.GetString()
        return_date = Date.parse_datestring(self, in_date)
        if return_date != None:
            self.ref_date = in_date
            self.__log('User entered ref pay date: %s' % self.ref_date)
            self.year = return_date["year"]
            self.month = return_date["month"]
            self.day = return_date["day"]
            self.__log("Month: %02d, Day: %02d, Year: %04d" % (self.month, self.day, self.year))
        else:
            self.MsgBox("Bad input date: %s" % (in_date))

    # Button action methods

    def onSave(self, event):
        error = ""
        if self.payType == -1:
            error = "Bad pay type"
        else:
            self.payType = self.payType
        if self.ref_date == None:
            if len(error) > 0:
                error = "%s; " % (error)
            error = "%sBad reference date" % (error)
        else:
            self.ref_date = self.ref_date
        if self.netpay == None:
            if len(error) > 0:
                error = "%s; " % (error)
            error = "%sBad net pay" % (error)
        else:
            self.netpay = self.netpay
        if error != "":
            self.MsgBox(error)
        else:
            self.dateFormat = self.dateFormats[self.dateFormatChoice]
            payType = self.payTypes[self.payType]
            print("%s, %s, %s, %s, %s" % (self.dateFormat, payType, self.ref_date, self.netpay, self.payDepositAcct))
            if self.assetFrame != None:
                self.assetFrame.setDateFormat(self.dateFormat)
                self.assetFrame.setPayType(payType)
                self.assetFrame.setRefDate(self.ref_date)
                self.assetFrame.setNetPay(self.netpay)
                self.assetFrame.setPayDepositAcct(self.payDepositAcct)
                self.assetFrame.writeConfigFile()
                self.assetFrame.update_all_Date_Formats(self.inDateFormat, self.dateFormat)
            self.Parent.Destroy()

    def onAbort(self, event):
        self.Parent.Destroy()

    # Helper method(s):

    def MsgBox(self, message):
        d = wx.MessageDialog(self, message, "error", wx.OK | wx.ICON_INFORMATION)
        d.ShowModal()
        d.Destroy()

    def __log(self, message):
        ''' Private method to print a string to the console
            control. (Only used for debugging and turned off for now! JJG 5/27/2020)'''
        if (True):                         # Change this to True to print out debug messages
            print('%s' % message)

    def doLayout(self):
        ''' Layout the controls by means of sizers. '''

        # A GridSizer will contain the input controls:
        gridSizer = wx.FlexGridSizer(rows=20, cols=1, vgap=10, hgap=10)

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
                 (self.refPayDateTextCtrl, expandOption),
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
                (emptySpace),
                (buttonGridSizer, dict(border=5, flag=wx.ALL|wx.ALIGN_CENTER))
            ]:
            mainSizer.Add(control, **options)

        self.SetSizerAndFit(mainSizer)

class FrameWithForms(wx.Frame):
    def __init__(self, parent, in_dateFormat="", in_payType="", in_refDate="", in_netpay="", in_payDepositAcct=""):
        super(FrameWithForms, self).__init__(parent)
        self.SetTitle('Properties Form')
        myForm(self, in_dateFormat, in_payType, in_refDate, in_netpay, in_payDepositAcct)
        # We just set the frame to the right size manually. This is feasible
        # for the frame since the frame contains just one component. If the
        # frame had contained more than one component, we would use sizers
        # of course, as demonstrated in the myForm class above.
        self.SetClientSize(self.GetBestSize())

if __name__ == '__main__':
    app = wx.App(0)
    frame = FrameWithForms(None, 1, 1, "05/29/2020", "$5,000.00", "none")
    frame.Show()
    app.MainLoop()