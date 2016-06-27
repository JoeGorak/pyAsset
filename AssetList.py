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
        # type: () -> object
        self.assets = []

    def __len__(self):
        return len(self.assets)

    def __getitem__(self, i):
        return self.assets[i]

    def __setitem__(self, i, val):
        self.assets[i] = val

    def __str__(self):
        ret_str = ""
        for i in range(len(self.assets)):
            cur_asset = self.assets[i]
            cd = cur_asset.details
            ret_str += "%-10s $%8.2f %s %s" % (cur_asset.name, cd.get_total(), cd.get_last_pull_date(), cd.get_type())
            limit = cd.get_limit()
            if limit != 0:
                ret_str += " $%8.2f $%8.2f" % (limit, cd.get_avail())
            rate = cd.get_rate()
            if rate != 0:
                ret_str += " %8.3f%%" % (rate*100)
            payment = cd.get_payment()
            if payment != 0:
                ret_str += " $%8.2f" % (payment)
            due_date = cd.get_due_date()
            if due_date != 0:
                ret_str += " %s" % (due_date)
            sched = cd.get_sched()
            if sched != 0:
                ret_str += " %s" % (sched)
            min_pay = cd.get_min_pay()
            if min_pay != 0:
                ret_str += " $%8.2f" % (min_pay)
            ret_str += "\n"
        return ret_str

    def __delitem__(self, i):
        del self.assets[i]

    def append(self, name):
        nt = namedtuple('Asset','name,details')
        account = nt(name, Asset(name))
        self.assets.append(account)
        return account