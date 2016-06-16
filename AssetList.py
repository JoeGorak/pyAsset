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
#  6/15/2016     Initial version v0.1

from collections import namedtuple
from Asset import Asset


class AssetList:
    def __init__(self):
        self.assets = []

    def __len__(self):
        return len(self.assets)

    def __getitem__(self, i):
        return self.assets[i]

    def __setitem__(self, i, val):
        self.assets[i] = val

    def __str__(self):
        return " %-10s $%8.2f\n" % (self.name, self.total)

    def __delitem__(self, i):
        del self.assets[i]

    def append(self, myname):
        nt = namedtuple('Asset','name,asset')
        account = nt(myname, Asset(myname))
        self.assets.append(account)