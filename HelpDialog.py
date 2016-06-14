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

import wx


class HelpDialog(wx.Dialog):
    def __init__(self, parent, my_id, title="Help", text=None, **kwds):
        wx.Dialog.__init__(self, parent, my_id, title, **kwds)
        self.text = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.ok_button = wx.Button(self, wx.ID_OK, "OK")

        self.set_properties()
        self.do_layout()

        if text: self.text.SetValue(text)

    def set_properties(self):
        self.SetTitle("Help")
        self.text.SetSize((480, 400))
        self.ok_button.SetDefault()
        self.text.SetEditable(0)

    def do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text, 0, wx.EXPAND, 0)
        sizer.Add(self.ok_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 7)
        self.SetAutoLayout(1)
        self.SetSizer(sizer)
        sizer.Fit(self)
        sizer.SetSizeHints(self)
        self.Layout()
