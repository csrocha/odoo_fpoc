# -*- coding: utf-8 -*-
from openerp import netsvc
from openerp.osv import osv, fields
from openerp.tools.translate import _

class fiscal_printer_configuration(osv.osv):
    """
    This configuration is independent of the printer, is related to point of sale.

    Must be used as entry for diferent calls:

    open_fiscal_ticket
    add_fiscal_item
    close_fiscal_ticket
    """

    _name = 'fpoc.configuration'
    _description = 'Fiscal printer configuration'

    def _get_type(self, cr, uid, context=None):
        return []

    def _get_protocol(self, cr, uid, context=None):
        return []

    _columns = {
        'name': fields.char(string='Name'),
        'type': fields.selection(_get_type, 'Type'),
        'protocol': fields.char('Protocol'),
        'user_ids': fields.one2many('fpoc.user', 'fiscal_printer_configuration_id', 'User entities'),
    }

    _sql_constraints = [
        ('unique_name', 'UNIQUE (name)', 'Name has to be unique!')
    ]

    def onchange_type(self, cr, uid, ids, type, context=None):
        return { 'value': { 'protocol': None } }

    def toDict(self, cr, uid, ids, context=None):
        return { id: {} for id in ids }

    def solve_status(self, cr, uid, ids, status, context=None):
        """
        This function compute paper_state, fiscal_state and printer_state for this configuration type.
        """
        return status

fiscal_printer_configuration()

class fiscal_printer_user(osv.AbstractModel):
    """
    Fiscal printer user is a Abstract class to be used by the owner of the fiscal printer.
    The entity responsable to print tickets must inheret this class.
    """
    def _get_fp_state(self, cr, uid, ids, fields_name, arg, context=None):
        context = context or {}
        r = {}
        for fpu in self.browse(cr, uid, ids, context):
            r[fpu.id] = dict(zip(fields_name, ['unknown']*len(fields_name)))

            if not fpu.fiscal_printer_id:
                continue

            res = fpu.fiscal_printer_id.get_state()
            res = fpu.fiscal_printer_configuration_id.solve_status(res)[fpu.fiscal_printer_id.id]

            if res:
                r[fpu.id]['fiscal_printer_paper_state'] = res['paper_state'] if 'paper_state' in res else 'unknown'
                r[fpu.id]['fiscal_printer_fiscal_state'] = res['fiscal_state'] if 'fiscal_state' in res else 'unknown'
                r[fpu.id]['fiscal_printer_state'] = res['printer_state'] if 'printer_state' in res else 'unknown'

        return r

    _name = 'fpoc.user'
    _description = 'Fiscal printer user'

    _columns = {
        'fiscal_printer_id': fields.many2one('fpoc.fiscal_printer', 'Fiscal Printer'),
        'fiscal_printer_configuration_id': fields.many2one('fpoc.configuration', 'Configuration'),
        'fiscal_printer_anon_partner_id': fields.many2one('res.partner', 'Anonymous partner'),
        'fiscal_printer_fiscal_state': fields.function(_get_fp_state,
                                                       type='selection', string='Printer Fiscal State',
                                                       method=True, readonly=True, multi="state",
                                                       selection=[
                                                           ('open','Open'),
                                                           ('close','Close'),
                                                           ('unknown','Unknown'),
                                                       ], help="Fiscal state of the printer"),
        'fiscal_printer_paper_state': fields.function(_get_fp_state,
                                                      type='selection', string='Printer Paper State',
                                                      method=True, readonly=True, multi="state",
                                                      selection=[
                                                          ('ok','Ok'),
                                                          ('low','Low Paper'),
                                                          ('none','No Paper'),
                                                          ('unknown','Unknown'),
                                                      ], help="Page state of the printer"),
        'fiscal_printer_state': fields.function(_get_fp_state, type='selection', string='Printer State',
                                                method=True, readonly=True, multi="state",
                                                selection=[
                                                    ('ready','Ready'),
                                                    ('deviceopen','Printer Open'),
                                                    ('onerror','On Error'),
                                                    ('offline','Offline'),
                                                    ('nomemory','No memory'),
                                                    ('printing','Printing'),
                                                    ('disabled','Disabled'),
                                                    ('unknown','Unknown'),
                                                ], help="Check printer status."),
    }


    def make_fiscal_ticket(self, cr, uid, ids, ticket, context=None):
        """
        Create Fiscal Ticket.
        """
        fp_obj = self.pool.get('fpoc.fiscal_printer')
        context = context or {}
        r = {}
        for usr in self.browse(cr, uid, ids, context):
            if not usr.fiscal_printer_id:
                raise osv.except_osv(_('Error!'),
                                     _('Selected journal has not printer associated.'))
            if not usr.fiscal_printer_configuration_id:
                raise osv.except_osv(_('Error!'),
                                     _('Selected journal has not configuration associated.'))
            if not usr.fiscal_printer_fiscal_state == 'open':
                raise osv.except_osv(_('Error!'),
                                     _('Need open fiscal status to print a '
                                       'ticket. Actual status is %s') % usr.fiscal_printer_fiscal_state)
            options = usr.fiscal_printer_configuration_id.toDict()[usr.fiscal_printer_configuration_id.id]
            fp_id = usr.fiscal_printer_id.id
            r[usr.id] = fp_obj.make_fiscal_ticket(cr, uid, [fp_id],
                                                  options=options, ticket=ticket,
                                                  context=context)[fp_id]
            if isinstance(r[usr.id], RuntimeError) and r[usr.id].message == "Timeout":
                raise osv.except_osv(_('Error!'),
                                     _('Timeout happen!!'))
        return r

    def cancel_fiscal_ticket(self, cr, uid, ids, context=None):
        """
        """
        fp_obj = self.pool.get('fpoc.fiscal_printer')
        context = context or {}
        r = {}
        for usr in self.browse(cr, uid, ids, context):
            fp_id = usr.fiscal_printer_id.id
            r[usr.id] = fp_obj.cancel_fiscal_ticket(cr, uid, fp_id,
                                                   context=context)[fp_id]
        return r

    def open_fiscal_journal(self, cr, uid, ids, context=None):
        context = context or {}
        r = {}
        for usr in self.browse(cr, uid, ids, context):
            if not usr.fiscal_printer_state in ['ready']:
                raise osv.except_osv(_('Error!'), _('Printer is not ready to open.'))
            if not usr.fiscal_printer_fiscal_state in ['close']:
                raise osv.except_osv(_('Error!'), _('You can\'t open a opened printer.'))
            r[usr.id] = usr.fiscal_printer_id.open_fiscal_journal()
        return r

    def close_fiscal_journal(self, cr, uid, ids, context=None):
        context = context or {}
        r = {}
        for usr in self.browse(cr, uid, ids, context):
            if not usr.fiscal_printer_state in ['ready']:
                raise osv.except_osv(_('Error!'), _('Printer is not ready to close.'))
            if not usr.fiscal_printer_fiscal_state in ['open']:
                raise osv.except_osv(_('Error!'), _('You can\'t close a closed printer.'))
            if not usr.fiscal_printer_paper_state in ['ok']:
                raise osv.except_osv(_('Error!'), _('You can\'t close a printer with low quantity of paper.'))
            r[usr.id] = usr.fiscal_printer_id.close_fiscal_journal()
        return r

    def shift_change(self, cr, uid, ids, context=None):
        context = context or {}
        r = {}
        for usr in self.browse(cr, uid, ids, context):
            if not usr.fiscal_printer_state in ['ready']:
                raise osv.except_osv(_('Error!'), _('Printer is not ready to close.'))
            if not usr.fiscal_printer_fiscal_state in ['open']:
                raise osv.except_osv(_('Error!'), _('You can\'t close a closed printer.'))
            if not usr.fiscal_printer_paper_state in ['ok']:
                raise osv.except_osv(_('Error!'), _('You can\'t close a printer with low quantity of paper.'))
            r[usr.id] = usr.fiscal_printer_id.shift_change()
        return r

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
