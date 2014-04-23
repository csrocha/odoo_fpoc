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

from openerp.addons.x_fiscal_printer.controllers.main import do_event

class wiz_update_printers(osv.TransientModel):
    """"""
    
    _name = 'fiscal_printer.wiz_update_printers'
    _inherit = [ 'fiscal_printer.wiz_update_printers' ]

    def update_printers(self, cr, uid, ids, context=None):
        """"""
        fp_obj = self.pool.get('fiscal_printer.fiscal_printer')
        R = do_event('info')
        print "R:", R
        for s in R:
            for p in R[s]:
                values = {
                    'name': p['name'],
                    'protocol': p['protocol'],
                    'model': p['model'],
                    'serialNumber': p['serialNumber'],
                }
                fp_obj.create(cr, uid, values)
        return True

wiz_update_printers()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
