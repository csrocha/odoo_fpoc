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



fiscal_printer()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
