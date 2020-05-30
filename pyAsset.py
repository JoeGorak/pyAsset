#!/usr/bin/env /usr/local/bin/pythonw
"""
                   PYTHON ASSET MANAGER
OVERVIEW
PyAsset.py  A personal finance manager in Python that can read
and write Quicken Interchange Format (qif) files.

Usage: PyAsset.py [filename]

Start the PyAsset program and optionally load the transactions
stored in filename, which is assumed to be in QIF format.

MENU FUNCTIONS
*Open* Open a new QIF file containing a Asset.

*Save* Save the current Asset under the default name;
asks for the name if it is not defined.

*Save As* Save the current Asset under a new name.

*Import* Add the transactions from another QIF archive to the current
Asset.

*Export Text* Export a text version of the current Asset

*Archive* Archive transactions older than a specified date to an archive
QIF file.

*Close* Close the current Asset.

*Quit* Quit PyAsset

*New Entry* Create a new transaction record in the register.

*Mark Cleared* Mark the current transaction record as cleared.

*Void Entry* Void the current transaction.

*Delete Entry* Delete the current transaction.

*Sort* Sort the current transaction register by date.

*Reconcile* Reconcile your Asset register.

*About* About PyAsset.

*Help* Print this help file.

INSTALLATION/REQUIREMENTS
PyAsset requires Python (>=3.7) and wxPython.

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

import sys
import wx
from AssetFrame import AssetFrame

version = 0.1

if __name__ == '__main__':
    cfgFile = None
    if len(sys.argv) > 1:
        cfgFile = sys.argv[1]
    assetFile = None
    if len(sys.argv) > 2:
        assetFile = sys.argv[2]
    app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
    app.frame = AssetFrame(None, 'PyAsset', cfgFile, assetFile)
    app.frame.Show()
    app.MainLoop()
