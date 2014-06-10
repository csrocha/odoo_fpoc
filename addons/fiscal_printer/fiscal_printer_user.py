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

class fiscal_printer_configuration_line(osv.osv):
    """
    The configuration line have information for each ticket from the same
    point of sale.
    """
    _name = 'fiscal_printer.configuration_line'
    _description = 'Configuration line'

    _columns = {
        'name': fields.char(string='Name'),
        'value': fields.char(string='Value'),
        'configuration_id': fields.many2one('fiscal_printer.configuration', 'Fiscal Printer Configuration'),
    }

    _constraints = [
        ('unique_name', 'UNIQUE (name, configuration_id)', 'Name has to be unique!')
    ]

fiscal_printer_attribute()

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

    _columns = {
        'name': fields.char(string='Name'),
        'configuration_line_ids': field.one2many('fiscal_printer.configuration_line', 'configuration_id', string='Configuration lines'),
        'user_ids': field.one2many('fiscal_printer.user', 'configuration_id', 'User entities'),
    }

    _constraints = [
        ('unique_name', 'UNIQUE (name)', 'Name has to be unique!')
    ]

fiscal_printer_configuration()

class fiscal_printer_user(osv.AbstractModel):
    """
    Fiscal printer user is a Abstract class to be used by the owner of the fiscal printer.
    The entity responsable to print tickets must inheret this class.
    """

    _name = 'fiscal_printer.user'
    _description = 'Fiscal printer user'

    _columns = {
        'fiscal_printer_id': field.many2one('fiscal_printer.fiscal_printer', 'Fiscal Printer'),
        'configuration_id': field.many2one('fiscal_printer.configuration', 'Configuration'),
    }

    def _load_configuration(cr, uid, ids, context=None):
        context = context or {}
        r = {}
        for usr in self.browse(cr, uid, ids, context):
            push_arg = {}
            r[usr.id] = {}
            for conf in usr.configuration_id:
                r[usr.id][conf.name] = conf.value
        return r
 
    def make_fiscal_ticket(cr, uid, ids, ticket, context=None):
        """
        Create Fiscal Ticket.
        """
        fp_obj = self.pool.get('fiscal_printer.fiscal_printer')
        context = args['context'] or {}
        r = {
            'turist_ticket': False,
        }
        options = self._load_configuration(cr, uid, ids, context=context)

        for usr in self.browse(cr, uid, ids, context):
            fp_id = usr.fiscal_printer_id.id
            r[usr.id] = fp_obj.open_fiscal_ticket(cr, uid, fp_id,
                                                  options=options, ticket=tiket,
                                                  context=context)
        return r

    def cancel_fiscal_ticket(cr, uid, ids, context=None):
        """
        """
        fp_obj = self.pool.get('fiscal_printer.fiscal_printer')
        context = args['context'] or {}
        r = {}
        for usr in self.browse(cr, uid, ids, context):
            fp_id = usr.fiscal_printer_id.id
            r[usr.id] = fp_obj.cancel_fiscal_ticket(cr, uid, fp_id,
                                                   context=context)
        return r

