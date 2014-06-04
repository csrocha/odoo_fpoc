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

class fiscal_printer_attribute(osv.osv):
    """"""
    
    _name = 'fiscal_printer.fiscal_printer_attribute'
    _description = 'fiscal_printer_attribute'



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
    ]

fiscal_printer_attribute()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
