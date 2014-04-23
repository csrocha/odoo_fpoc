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

class invoice(osv.osv):
    """"""
    
    _name = 'account.invoice'
    _inherits = {  }
    _inherit = [ 'account.invoice' ]

    def onchange_journal_id(self, cr, uid, ids, journal_id, context=None):
        """
        Set the fiscal printer for selected journal.
        """
        journal_obj = self.pool.get('account.journal')
        result = super(invoice,self).onchange_journal_id(cr, uid, ids, journal_id, context=None)
        data = journal_obj.read(cr, uid, journal_id, ['fiscal_printer_id'])
        result['value']['fiscal_printer_id'] = data['fiscal_printer_id'] and data['fiscal_printer_id'][0]
        return result

    def print_in_fiscal_printer(self, cr, uid, ids, context=None):
        return {
            'type' : 'ir.actions.client',
            'name' : 'Print in fiscal printer',
            'tag'  : 'fp_print',
            'params' : {},
        }

    def validate_fiscal_printer(self, cr, uid, ids, context=None):
        raise RuntimeError("Ouch")
        return False;


invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
