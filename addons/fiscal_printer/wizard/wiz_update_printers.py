# -*- coding: utf-8 -*-
##############################################################################
#
#    fiscal_printer
#    Copyright (C) 2014 No author.
#    No email
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import re
from openerp import netsvc
from openerp.osv import osv, fields

class wiz_update_printers(osv.TransientModel):
    """"""
    
    _name = 'fiscal_printer.wiz_update_printers'
    _description = 'wiz_update_printers'

    _states_ = [
        # State machine: untitle
        ('listing','Listing'),
        ('done','Done'),
    ]


    _columns = {
        'create_printers': fields.boolean(string='create_printers'),
        'state': fields.selection(_states_, "State"),
    }

    _defaults = {
        'state': 'listing',
    }


    _constraints = [
    ]


    def update_printers(self, cr, uid, ids, context=None):
        """"""
        raise NotImplementedError



wiz_update_printers()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
