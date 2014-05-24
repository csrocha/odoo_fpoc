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

from openerp import netsvc
from openerp.osv import osv, fields
import logging

from controllers.main import do_event

_logger = logging.getLogger(__name__)
_schema = logging.getLogger(__name__ + '.schema')

class account_journal(osv.osv):
    def _get_fp_state(self, cr, uid, ids, fields_name, arg, context=None):
        context = context or {}
        r = {}
        for jou in self.browse(cr, uid, ids, context):
            if jou.fiscal_printer_id:
                res = jou.fiscal_printer_id.get_state()[jou.fiscal_printer_id.id]
                r[jou.id] = 'disabled'
                r[jou.id] = 'open_fiscal_journal' if res['inFiscalJournal'] else 'close_fiscal_printer'
                r[jou.id] = 'printing' if res['documentInProgress'] else r[jou.id]
                r[jou.id] = 'nopaper' if res['slipHasPaper'] else r[jou.id]
                r[jou.id] = 'nomemory' if res['memStatus'] else r[jou.id]
                r[jou.id] = 'offline' if res['isOffline'] else r[jou.id]
                r[jou.id] = 'onerror' if res['inError'] else r[jou.id]
                r[jou.id] = 'deviceopen' if res['isPrinterOpen'] else r[jou.id]
            else:
                r[jou.id] = False
        return r

    def _get_fp_items_generated(self, cr, uid, ids, fields_name, arg, context=None):
        context = context or {}
        r = {}
        for jou in self.browse(cr, uid, ids, context):
            if jou.fiscal_printer_id:
                r[jou.id] = False
            else:
                r[jou.id] = False
        return r

    _inherit = "account.journal"
    _columns = {
        'use_fiscal_printer': fields.boolean('Associated to a fiscal printer'),
        'fiscal_printer_id': fields.many2one('fiscal_printer.fiscal_printer', 'Fiscal printer',
                            help="Which fiscal printer is using this journal."),
        'fiscal_printer_state': fields.function(_get_fp_state, type='selection', string='Fiscal printer state',
                                      method=True, readonly=True,
                                      selection=[
                                          ('deviceopen','Printer Open'),
                                          ('onerror','On Error'),
                                          ('offline','Offline'),
                                          ('nomemory','No memory'),
                                          ('printing','Printing'),
                                          ('nopaper','No paper'),
                                          ('open_fiscal_journal','Open Fiscal Journal'),
                                          ('closed_fiscal_journal','Closed Fiscal Journal'),
                                          ('disabled','Disabled'),
                                      ],
                            help="Check printer status."),
        'fiscal_printer_items_generated': fields.function(_get_fp_items_generated, type='integer', string='Number of Invoices Generated',method=True, 
                            help="Check how many invoices was generated in the printer.", readonly=True),
    }
 
account_journal()

