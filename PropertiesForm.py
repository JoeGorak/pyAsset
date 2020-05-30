import wx
import re
from Date import Date

class myForm(wx.Panel):
    ''' The Form class is a wx.Panel that creates a bunch of controls
        and handlers for callbacks. Doing the layout of the controls is
        the responsibility of subclasses (by means of the doLayout() method).
    '''

    def __init__(self, parent, in_payType=-1, in_refDate="", in_netpay=""):
        self.parent = parent
        super(myForm, self).__init__(parent)
        self.payTypes = ['every week', 'every 2 weeks', 'monthly']
        if in_payType != -1:
            self.payType = in_payType
        else:
            self.payType = 1
#            self.MsgBox("Pay type default to %d (%s)" % (self.payType, self.payTypes[self.payType]))
        self.ref_date = in_refDate
        self.netpay = in_netpay
        self.createControls()
        self.setControlInitValues()
        self.bindEvents()
        self.doLayout()

    def createControls(self):
        self.saveButton = wx.Button(self, label="Save")
        self.abortButton = wx.Button(self, label="Abort")
        self.netPay = wx.StaticText(self, label="Net pay (take home amount):")
        self.netPayTextCtrl = wx.TextCtrl(self, style = wx.TE_PROCESS_ENTER, value="$d,ddd.dd")
        self.refPayDate = wx.StaticText(self, label="Reference pay date:")
        self.refPayDateTextCtrl = wx.TextCtrl(self, style = wx.TE_PROCESS_ENTER, value="mm/dd/yyyy")
        self.payTypeRadioBox = wx.RadioBox(self,
                                         label="How often are you paid?",
                                         choices=self.payTypes, majorDimension=3, style=wx.RA_SPECIFY_COLS)

    def setControlInitValues(self):
        self.netPayTextCtrl.LabelText = self.netpay
        self.netPayTextCtrl.Refresh()
        self.refPayDateTextCtrl.LabelText = self.ref_date
        self.refPayDateTextCtrl.Refresh()
        self.payTypeRadioBox.SetSelection(self.payType)
        self.payTypeRadioBox.Refresh()

    def bindEvents(self):
        for control, event, handler in \
                [(self.saveButton, wx.EVT_BUTTON, self.onSave),
                 (self.abortButton, wx.EVT_BUTTON, self.onAbort),
                 (self.netPayTextCtrl, wx.EVT_TEXT_ENTER, self.onNetPayEntered),
                 (self.refPayDateTextCtrl, wx.EVT_TEXT_ENTER, self.onRefPayDateEntered),
                 (self.payTypeRadioBox, wx.EVT_RADIOBOX, self.onPayTypechanged)]:
            control.Bind(event, handler)

    # Callback methods:

    def onPayTypechanged(self, event):
        self.payType = event.GetInt()
        self.__log('User is paid: %s' % self.payTypes[self.payType])

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
            print("%s, %s, %s" % (self.payTypes[self.payType], self.ref_date, self.netpay))
            assetFrame = self.GetGrandParent()
            if assetFrame != None:
                assetFrame.setPayType(self.payType)
                assetFrame.setRefDate(self.ref_date)
                assetFrame.setNetPay(self.netpay)
                assetFrame.writeConfigFile()
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
        if (False):                         # Change this to True to print out debug messages
            print('%s' % message)

    def doLayout(self):
        ''' Layout the controls by means of sizers. '''

        # A GridSizer will contain the input controls:
        gridSizer = wx.FlexGridSizer(rows=8, cols=1, vgap=10, hgap=10)

        # Aother GridSizer has the Save and Abort buttons
        buttonGridSizer = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)

        # Add the controls to the sizers:
        for control, options in \
                [emptySpace,
                 (self.payTypeRadioBox, expandOption),
                 (self.netPay, expandOption),
                 (self.netPayTextCtrl, expandOption),
                 (self.refPayDate, expandOption),
                 (self.refPayDateTextCtrl, expandOption),
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
    def __init__(self, parent, in_payType=-1, in_refDate="", in_netpay=""):
        super(FrameWithForms, self).__init__(parent)
        self.SetTitle('Properties Form')
        myForm(self, in_payType, in_refDate, in_netpay)
        # We just set the frame to the right size manually. This is feasible
        # for the frame since the frame contains just one component. If the
        # frame had contained more than one component, we would use sizers
        # of course, as demonstrated in the myForm class above.
        self.SetClientSize(self.GetBestSize())

if __name__ == '__main__':
    app = wx.App(0)
    frame = FrameWithForms(None, 1, "05/29/2020", "$5,000.00")
    frame.Show()
    app.MainLoop()