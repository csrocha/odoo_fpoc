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

from controllers.main import do_event

class fiscal_printer(osv.osv):
    """"""
    
    _name = 'fiscal_printer.fiscal_printer'
    _description = 'fiscal_printer'

    _columns = {
        'name': fields.char(string='Name', required=True),
        'protocol': fields.char(string='Protocol'),
        'model': fields.char(string='Model'),
        'serialNumber': fields.char(string='Serial Number (S/N)'),
        'printerStatus': fields.char(string='Printer Status'),
        'lastUpdate': fields.datetime(string='Last Update'),
        'clock': fields.datetime(string='Clock'),
        'session_id': fields.char(string='session_id'),
        'journal_id': fields.one2many('account.journal', 'fiscal_printer_id', string='Journals'), 
        'attribute_ids': fields.one2many('fiscal_printer.fical_printer_attribute', 'fiscal_printer_id', string='Attributes'), 
        'invoice_ids': fields.one2many('account.invoice', 'fiscal_printer_id', string='Invoices'), 
    }

    _defaults = {
    }

    _constraints = [
    ]

    _sql_constraints = [ ('model_serialNumber_unique', 'unique("model", "serialNumber")', 'this printer with this model and serial number yet exists') ]

    def update_printers(self, cr, uid, ids, context=None):
        r = do_event('info', {})
        return True

    def short_test(self, cr, uid, ids, context=None):
        for fp in self.browse(cr, uid, ids):
            do_event('short_test', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
        return True

    def large_test(self, cr, uid, ids, context=None):
        for fp in self.browse(cr, uid, ids):
            do_event('large_test', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
        return True


    def advance_paper(self, cr, uid, ids, inv_id, context=None):
        for fp in self.browse(cr, uid, ids):
            do_event('advance_paper', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
        return True
        
    def cut_paper(self, cr, uid, ids, inv_id, context=None):
        for fp in self.browse(cr, uid, ids):
            do_event('cut_paper', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
        return True
        
    def open_fiscal_journal(self, cr, uid, ids, inv_id, context=None):
        for fp in self.browse(cr, uid, ids):
            do_event('open_fiscal_journal', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
        return True

    def close_fiscal_journal(self, cr, uid, ids, inv_id, context=None):
        for fp in self.browse(cr, uid, ids):
            do_event('close_fiscal_journal', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
        return True

    def shift_change(self, cr, uid, ids, inv_id, context=None):
        for fp in self.browse(cr, uid, ids):
            do_event('shift_change', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
        return True

    # TODO: {'name': fp.name} must be replaced with printer_id
    def get_state(self, cr, uid, ids, context=None):
        r = {}
        for fp in self.browse(cr, uid, ids):
            event_result = do_event('get_status', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
            r[fp.id] = event_result.pop() if event_result else False
        return r



fiscal_printer()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
