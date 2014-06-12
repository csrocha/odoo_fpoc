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

class fiscal_printer_configuration(osv.osv):
    """
    This configuration is independent of the printer, is related to point of sale.

    Must be used as entry for diferent calls:

    open_fiscal_ticket
    add_fiscal_item
    close_fiscal_ticket
    """

    _name = 'fiscal_printer.configuration'
    _description = 'Fiscal printer configuration'

    def _get_type(self, cr, uid, context=None):
        return []

    def _get_protocol(self, cr, uid, context=None):
        return []

    _columns = {
        'name': fields.char(string='Name'),
        'type': fields.selection(_get_type, 'Type'),
        'protocol': fields.char('Protocol'),
        'user_ids': fields.one2many('fiscal_printer.user', 'fiscal_printer_configuration_id', 'User entities'),
    }

    _sql_constraints = [
        ('unique_name', 'UNIQUE (name)', 'Name has to be unique!')
    ]

    def onchange_type(self, cr, uid, ids, type, context=None):
        return { 'value': { 'protocol': None } }

    def toDict(self, cr, uid, ids, context=None):
        return { id: {} for id in ids }

fiscal_printer_configuration()

class fiscal_printer_user(osv.AbstractModel):
    """
    Fiscal printer user is a Abstract class to be used by the owner of the fiscal printer.
    The entity responsable to print tickets must inheret this class.
    """
    def _get_fp_state(self, cr, uid, ids, fields_name, arg, context=None):
        context = context or {}
        r = {}
        for jou in self.browse(cr, uid, ids, context):
            r[jou.id] = 'offline'
            res = jou.fiscal_printer_id.get_state() if jou.fiscal_printer_id else False
            if res and res[jou.fiscal_printer_id.id]:
                res = res[jou.fiscal_printer_id.id]
                r[jou.id] = 'disabled'
                r[jou.id] = 'open_fiscal_journal' if res['inFiscalJournal'] else 'close_fiscal_printer'
                r[jou.id] = 'printing' if res['documentInProgress'] else r[jou.id]
                r[jou.id] = 'nopaper' if res['slipHasPaper'] else r[jou.id]
                r[jou.id] = 'nomemory' if res['memStatus'] else r[jou.id]
                r[jou.id] = 'offline' if res['isOffline'] else r[jou.id]
                r[jou.id] = 'onerror' if res['inError'] else r[jou.id]
                r[jou.id] = 'deviceopen' if res['isPrinterOpen'] else r[jou.id]
        return r

    _name = 'fiscal_printer.user'
    _description = 'Fiscal printer user'

    _columns = {
        'fiscal_printer_id': fields.many2one('fiscal_printer.fiscal_printer', 'Fiscal Printer'),
        'fiscal_printer_configuration_id': fields.many2one('fiscal_printer.configuration', 'Configuration'),
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
                                      ], help="Check printer status."),
    }


    def make_fiscal_ticket(self, cr, uid, ids, ticket, context=None):
        """
        Create Fiscal Ticket.
        """
        fp_obj = self.pool.get('fiscal_printer.fiscal_printer')
        context = context or {}
        r = {}
        for usr in self.browse(cr, uid, ids, context):
            options = usr.fiscal_printer_configuration_id.toDict()[usr.fiscal_printer_configuration_id.id]
            fp_id = usr.fiscal_printer_id.id
            r[usr.id] = fp_obj.make_fiscal_ticket(cr, uid, [fp_id],
                                                  options=options, ticket=ticket,
                                                  context=context)[fp_id]
        return r

    def cancel_fiscal_ticket(self, cr, uid, ids, context=None):
        """
        """
        fp_obj = self.pool.get('fiscal_printer.fiscal_printer')
        context = context or {}
        r = {}
        for usr in self.browse(cr, uid, ids, context):
            fp_id = usr.fiscal_printer_id.id
            r[usr.id] = fp_obj.cancel_fiscal_ticket(cr, uid, fp_id,
                                                   context=context)[fp_id]
        return r

