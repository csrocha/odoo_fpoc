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
from datetime import datetime

class fiscal_printer_attribute(osv.osv):
    """
    Fiscal printer attribute is a value to setup the printer.
    """
    
    _name = 'fiscal_printer.attribute'
    _description = 'Fiscal printer attribute'

    _columns = {
        'name': fields.char(string='Name'),
        'value': fields.char(string='Value'),
        'lastUpdate': fields.datetime(string='Last Update'),
        'lastCommit': fields.datetime(string='Last Commit'),
        'readOnly': fields.boolean(string='Read Only'),
        'fiscal_printer_id': fields.many2one('fiscal_printer.fiscal_printer', string='Fiscal Printer', required=True), 
    }

    _defaults = {
    }

    _constraints = [
        ('unique_name', 'UNIQUE (name, fiscal_printer_id)', 'Name has to be unique!')
    ]

fiscal_printer_attribute()

class fiscal_printer(osv.osv):
    """
    The fiscal printer entity.
    """

    def _get_status(self, cr, uid, ids, field_name, arg, context=None):
        s = self.get_state(cr, uid, ids, context) 
        r = {}
        for p_id in ids:
            if s[p_id]:
                dt = datetime.strptime(s[p_id]['clock'], "%Y-%m-%d %H:%M:%S")
                r[p_id] = {
                    'clock': dt.strftime("%Y-%m-%d %H:%M:%S"),
                    'printerStatus': s[p_id]['strPrinterStatus'],
                    'fiscalStatus': s[p_id]['strFiscalStatus'],
                }
            else:
                r[p_id]= {
                    'clock':False,
                    'printerStatus':'Offline',
                    'fiscalStatus': 'Offline',
                }
        return r
    
    _name = 'fiscal_printer.fiscal_printer'
    _description = 'fiscal_printer'

    _columns = {
        'name': fields.char(string='Name', required=True),
        'protocol': fields.char(string='Protocol'),
        'model': fields.char(string='Model'),
        'serialNumber': fields.char(string='Serial Number (S/N)'),
        'lastUpdate': fields.datetime(string='Last Update'),
        'printerStatus': fields.function(_get_status, type="char", method=True, readonly="True", multi="state", string='Printer status'),
        'fiscalStatus':  fields.function(_get_status, type="char", method=True, readonly="True", multi="state", string='Fiscal status'),
        'clock':         fields.function(_get_status, type="datetime", method=True, readonly="True", multi="state", string='Clock'),
        'session_id': fields.char(string='session_id'),
        'attribute_ids': fields.one2many('fiscal_printer.attribute', 'fiscal_printer_id', string='Attributes'), 
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

    def get_state(self, cr, uid, ids, context=None):
        r = {}
        for fp in self.browse(cr, uid, ids):
            event_result = do_event('get_status', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
            r[fp.id] = event_result.pop() if event_result else False
        return r

    def get_counters(self, cr, uid, ids, context=None):
        r = {}
        for fp in self.browse(cr, uid, ids):
            event_result = do_event('get_counters', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
            r[fp.id] = event_result.pop() if event_result else False
        return r

    def read_attributes(self, cr, uid, ids, context=None):
        attr_obj = self.pool.get('fiscal_printer.attribute')
        r = {}
        for fp in self.browse(cr, uid, ids):
            event_result = do_event('read_attributes', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
            r = event_result.pop() if event_result else False
            if r and 'attributes' in r:
                lastUpdate = fields.date.context_today
                attribs = []
                for k,v in r['attributes'].items():
                    attr_id = attr_obj.search(cr, uid, [('name','=',k), ('fiscal_printer_id','=',fp.id)])
                    if len(attr_id) == 0:
                        t_op = 0
                        t_id = 0
                    else:
                        t_op = 1
                        t_id = attr_id[0]
                    attribs.append((t_op,t_id,{
                        'name': k,
                        'value': v,
                        'lastUpdate': False,
                        'readOnly': k in r['readonly'],
                        'fiscal_printer_id': fp.id
                    }))
                self.write(cr, uid, fp.id, {'attribute_ids': attribs})
        return True

    def write_attributes(self, cr, uid, ids, context=None):
        r = {}
        return True

    def make_fiscal_ticket(self, cr, uid, ids, options={}, ticket={}, context=None):
        fparms = locals()
        r = {}
        for fp in self.browse(cr, uid, ids):
            fparms['name'] = fp.name
            fparms['options'] = options
            fparms['ticket'] = ticket
            event_result = do_event('make_fiscal_ticket', fparms,
                                    session_id=fp.session_id, printer_id=fp.name)
            r[fp.id] = event_result.pop() if event_result else False
        return r

    def cancel_fiscal_ticket(self, cr, uid, ids, context=None):
        fparms = locals()
        r = {}
        for fp in self.browse(cr, uid, ids):
            fparms['name'] = fp.name
            event_result = do_event('cancel_fiscal_ticket', fparms,
                                    session_id=fp.session_id, printer_id=fp.name)
            r[fp.id] = event_result.pop() if event_result else False
        return r

 
fiscal_printer()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
