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

from openerp.addons.fiscal_printer.controllers.main import do_event

import logging
_logger = logging.getLogger(__name__)

class wiz_fiscal_printer(osv.TransientModel):
    """
    Temporal published printers to be selected.
    """
    _name = 'fiscal_printer.wiz_fiscal_printer'
    _description = 'Published printers to be selected in wizard.'

    _columns = {
        'name': fields.char(string='Name'),
        'protocol': fields.char(string='Protocol'),
        'model': fields.char(string='Model'),
        'serialNumber': fields.char(string='Serial Number'),
    }

wiz_fiscal_printer()

def _get_fiscal_printers(self, cr, uid, context=None):
    t_fp_obj = self.pool.get('fiscal_printer.wiz_fiscal_printer')

    R = do_event('list_printers', control=True)

    w_fp_ids = []
    for r in R:
        for p in r['printers']:
            values = {
                'name': p['name'],
                'protocol': p['protocol'],
                'model': p['model'],
                'serialNumber': p['serialNumber'],
            }
            pid = t_fp_obj.create(cr, uid, values)
            w_fp_ids.append(pid)

    return w_fp_ids

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
        'state': fields.selection(_states_, "State"),
        'wiz_fiscal_printer_ids': fields.many2many('fiscal_printer.wiz_fiscal_printer', 'wiz_update_printers_rel', 'wiz_id', 'pri_id', 'Fiscal Printers'),
    }

    _defaults = {
        'state': 'listing',
        'wiz_fiscal_printer_ids': _get_fiscal_printers,
    }

    _constraints = [
    ]


    def update_printers(self, cr, uid, ids, context=None):
        """"""
        fp_obj = self.pool.get('fiscal_printer.fiscal_printer')
        for wiz in self.browse(cr, uid, ids):
            for pri in wiz.wiz_fiscal_printer_ids:
                values = {
                    'name': pri.name,
                    'protocol': pri.protocol,
                    'model': pri.model,
                    'serialNumber': pri.serialNumber,
                }
                fp_obj.create(cr, uid, values)
        return True

wiz_update_printers()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
