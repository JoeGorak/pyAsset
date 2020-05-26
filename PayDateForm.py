import wx
import re
from Date import Date

class Form(wx.Panel):
    ''' The Form class is a wx.Panel that creates a bunch of controls
        and handlers for callbacks. Doing the layout of the controls is
        the responsibility of subclasses (by means of the doLayout()
        method). '''

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        self.payTypes = ['every week', 'every 2 weeks', 'monthly']
        self.payType = self.payTypes[0]
        self.ref_date = ""
        self.createControls()
        self.bindEvents()
        self.doLayout()

    def createControls(self):
        self.saveButton = wx.Button(self, label="Save")
        self.netPay = wx.StaticText(self, label="Net pay (take home amount):")
        self.netPayTextCtrl = wx.TextCtrl(self, style = wx.TE_PROCESS_ENTER, value="$d,ddd.dd")
        self.refPayDate = wx.StaticText(self, label="Reference pay date:")
        self.refPayDateTextCtrl = wx.TextCtrl(self, style = wx.TE_PROCESS_ENTER, value="mm/dd/yyyy")
        self.payTypeRadioBox = wx.RadioBox(self,
                                         label="How often are you paid?",
                                         choices=self.payTypes, majorDimension=3, style=wx.RA_SPECIFY_COLS)

    def bindEvents(self):
        for control, event, handler in \
                [(self.saveButton, wx.EVT_BUTTON, self.onSave),
                 (self.netPayTextCtrl, wx.EVT_TEXT_ENTER, self.onNetPayEntered),
                 (self.refPayDateTextCtrl, wx.EVT_TEXT_ENTER, self.onRefPayDateEntered),
                 (self.payTypeRadioBox, wx.EVT_RADIOBOX, self.onPayTypechanged)]:
            control.Bind(event, handler)

    def doLayout(self):
        ''' Layout the controls that were created by createControls().
            Form.doLayout() will raise a NotImplementedError because it
            is the responsibility of subclasses to layout the controls. '''
        raise NotImplementedError

        # Callback methods:

    def onPayTypechanged(self, event):
        newType = event.GetInt()
        self.payType = self.payTypes[newType]
        self.__log('User is paid: %s' % self.payType)

    def onSave(self, event):
        self.__log('User clicked on button with id %d' % event.GetId())

    def onNetPayEntered(self, event):
        money_regex = "^[\\-]*[\$]*[0-9]{1,3}((\,*)[0-9]{3})*[\\.][0-9]{2}$"
        in_netpay = event.GetString()
        match = re.search(money_regex, in_netpay)
        if match == None:
            print("Bad net pay entered: %s" % (in_netpay))
        else:
            self.netpay = in_netpay.replace("$", "").replace(",", "")
            self.__log('User entered net pay: %s' % self.netpay)

    def onRefPayDateEntered(self, event):
        in_date = event.GetString()
        in_date = Date.parse_datestring(self, in_date)
        if self.ref_date != None:
            self.ref_date = in_date
            self.__log('User entered ref pay date: %s' % self.ref_date)
            self.year = self.ref_date["year"]
            self.month = self.ref_date["month"]
            self.day = self.ref_date["day"]
            print("Month: %02d, Day: %02d, Year: %04d" % (self.month, self.day, self.year))
        else:
            print("Bad input date: %s" % (in_date))

    # Helper method(s):

    def __log(self, message):
        ''' Private method to print a string to the console
            control. '''
        print('%s' % message)

class FormWithSizer(Form):
    def doLayout(self):
        ''' Layout the controls by means of sizers. '''

        # A horizontal BoxSizer will contain the GridSizer (on the left)
        boxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        # A GridSizer will contain the other controls:
        gridSizer = wx.FlexGridSizer(rows=8, cols=1, vgap=10, hgap=10)
        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)

        # Add the controls to the sizers:
        for control, options in \
                [emptySpace,
                 (self.payTypeRadioBox, noOptions),
                 (self.netPay, noOptions),
                 (self.netPayTextCtrl, expandOption),
                 (self.refPayDate, noOptions),
                 (self.refPayDateTextCtrl, expandOption),
                 emptySpace,
                 (self.saveButton, dict(flag=wx.ALIGN_CENTER))]:
            gridSizer.Add(control, **options)

        for control, options in \
                [(gridSizer, dict(border=5, flag=wx.ALL))]:
            boxSizer.Add(control, **options)

        self.SetSizerAndFit(boxSizer)

class FrameWithForms(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(FrameWithForms, self).__init__(*args, **kwargs)
        FormWithSizer(self)
        # We just set the frame to the right size manually. This is feasible
        # for the frame since the frame contains just one component. If the
        # frame had contained more than one component, we would use sizers
        # of course, as demonstrated in the FormWithSizer class above.
        self.SetClientSize(self.GetBestSize())

if __name__ == '__main__':
    app = wx.App(0)
    frame = FrameWithForms(None, title='PayDate Form')
    frame.Show()
    app.MainLoop()