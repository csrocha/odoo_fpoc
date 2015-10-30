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
from openerp.tools.translate import _

from controllers.main import do_event
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)
_schema = logging.getLogger(__name__ + '.schema')

_header_lines = ['headerLine 1', 'headerLine 2', 'headerLine 3', 'headerLine 4', 'headerLine 5', 'headerLine 6', 'headerLine 7']
_footer_lines = ['footerLine 1', 'footerLine 2', 'footerLine 3', 'footerLine 4', 'footerLine 5', 'footerLine 6', 'footerLine 7']

class epson_ar_fiscal_printer(osv.osv):
    """
    The fiscal printer entity.
    """

    _inherit = 'fpoc.fiscal_printer'

    def _get_field(self, cr, uid, ids, field_name, args, context):
        r = {}
        for fp in self.browse(cr, uid, ids):
            r[fp.id] = { fn: False for fn in field_name }
            event_result = do_event('read_attributes', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
            event_result = event_result.pop() if event_result else {}
            if event_result and 'attributes' in event_result:
                attrs = event_result['attributes']
                r[fp.id]['header'] = '\n'.join([ attrs[k] for k in _header_lines
                                                if k in attrs and attrs[k] ])
                r[fp.id]['footer'] = '\n'.join([ attrs[k] for k in _footer_lines
                                                if k in attrs and attrs[k] ])
                for fn in field_name:
                    if fn in attrs:
                        if fn in ['tasaIVA', 'maxMonto']:
                            r[fp.id][fn] = float(attrs[fn])/100.
                        elif fn in ['fechaFiscalizacion']:
                            line = attrs[fn]
                            r[fp.id][fn] = "20{2}-{1}-{0}".format(*[line[i:i+2] for i in range(0, len(line), 2)])
                        else:
                            r[fp.id][fn] = attrs[fn]
        return r

    def _put_field(self, cr, uid, ids, field_name, field_value, arg, context):
        fp = self.browse(cr, uid, ids)
        data = { 'name': fp.name,
                 'attributes': {} }
        if (field_name == 'header'):
            lines = field_value.split('\n')[:len(_header_lines)] if field_value else []
            lines = lines + (len(_header_lines) - len(lines)) * ['']
            data['attributes'].update(dict(zip(_header_lines, lines)))
        if (field_name == 'footer'):
            lines = field_value.split('\n')[:len(_footer_lines)] if field_value else []
            lines = lines + (len(_footer_lines) - len(lines)) * ['']
            data['attributes'].update(dict(zip(_footer_lines, lines)))
        event_result = do_event('write_attributes', data,
                 session_id=fp.session_id, printer_id=fp.name)
        return True

    _columns = {
        'header': fields.function(_get_field, fnct_inv=_put_field, type="text", method=True, multi='epson_text', store=False, string='Header'),
        'footer': fields.function(_get_field, fnct_inv=_put_field, type="text", method=True, multi='epson_text', store=False, string='Footer'),

        'razonSocial': fields.function(_get_field, type="char", method=True, multi='epson_info', store=False, string='Razon Social'),
        'cuit': fields.function(_get_field, type="char", method=True, multi='epson_info', store=False, string='CUIT'),
        'caja': fields.function(_get_field, type="char", method=True, multi='epson_info', store=False, string='Caja/Punto de Venta'),
        'ivaResponsabilidad': fields.function(_get_field, type="char", method=True, multi='epson_info', store=False, string='Resp. IVA'),
        'calle': fields.function(_get_field, type="char", method=True, multi='epson_info', store=False, string='Calle'),
        'numero': fields.function(_get_field, type="char", method=True, multi='epson_info', store=False, string='Numero'),
        'piso': fields.function(_get_field, type="char", method=True, multi='epson_info', store=False, string='Piso'),
        'depto': fields.function(_get_field, type="char", method=True, multi='epson_info', store=False, string='Depto'),
        'localidad': fields.function(_get_field, type="char", method=True, multi='epson_info', store=False, string='Localidad'),
        'cpa': fields.function(_get_field, type="char", method=True, multi='epson_info', store=False, string='Cod.Pos.'),
        'provincia': fields.function(_get_field, type="char", method=True, multi='epson_info', store=False, string='Provincia'),
        'tasaIVA': fields.function(_get_field, type="float", method=True, multi='epson_info', store=False, string='Tasa IVA'),
        'maxMonto': fields.function(_get_field, type="float", method=True, multi='epson_info', store=False, string='Monto Maximo'),
        'fechaFiscalizacion': fields.function(_get_field, type="date", method=True, multi='epson_info', store=False, string='Fecha Fiscalizacion'),
    }

epson_ar_fiscal_printer()

class epson_ar_fiscal_tf_printer_configuration(osv.osv):
    """
    Configuracion necesaria para documentos fiscales Ticket-Facturas/Nota de Debito
    """

    _inherit = 'fpoc.configuration'
    _description = 'Configuracion de TF/TND para Epson Argentina'

    epson_type_paper_status = {
        'epson_ar_receipt': ( 'receiptState', {
            0: 'ok',
            1: 'low',
            2: 'none',
            3: 'unknown',
        }),
        'epson_ar_journal': ( 'journalState', {
            0: 'ok',
            1: 'low',
            2: 'none',
            3: 'unknown',
        }),
        'epson_ar_slip': ( 'slipHasPaper', {
            0: 'ok',
            1: 'low',
            2: 'none',
            3: 'unknown',
        }),
    }

    def solve_status(self, cr, uid, ids, status, context=None):
        r = super(epson_ar_fiscal_tf_printer_configuration, self).solve_status(cr, uid, ids, status, context=context)
        for conf in self.browse(cr, uid, ids):
            if conf.type not in ['epson_ar_receipt', 'epson_ar_journal', 'epson_ar_slip']:
                continue
            for stat in r.values():
                _logger.debug(stat)
                if not stat:
                    continue
                if 'paper_state' not in stat:
                    key, rule = self.epson_type_paper_status.get(conf.type, (False, False))
                    stat['paper_state'] = rule.get(stat.get(key, 'unknown'),'unknown')
                if 'fiscal_state' not in stat:
                    stat['fiscal_state'] = 'open' if stat['inFiscalJournal'] else 'close'
                if 'printer_state' not in stat:
                    stat['printer_state'] = [ v for v in ['deviceopen' if stat['isPrinterOpen']      else False,
                                                          'onerror'    if stat['inError']            else False,
                                                          'offline'    if stat['isOffline']          else False,
                                                          'nomemory'   if stat['memStatus']          else False,
                                                          'nopaper'    if stat['slipHasPaper']       else False,
                                                          'printing'   if stat['documentInProgress'] else False,
                                                          'ready'] if v ][0]
        return r

    def _get_type(self, cr, uid, context=None):
        r = super(epson_ar_fiscal_tf_printer_configuration, self)._get_type(cr, uid, context=context)
        return r + [
            ('epson_ar_receipt', _('Receipt Epson Arg.')),
            ('epson_ar_journal', _('Journal Epson Arg.')),
            ('epson_ar_slip',    _('Slip station Epson Arg.')),
        ]

    _columns = {
        'type': fields.selection(_get_type, 'Type'),
        'triplicated': fields.boolean('Imprimir en triplicado'),
        'store_description': fields.boolean('Almacenar descripciones de items'),
        'keep_description_attributes': fields.boolean('Conservar atributos de impresion de las descripciones'),
        'store_extra_description': fields.boolean('Almacenar solo primer descripcion extra'),
        'cut_paper': fields.boolean('Cortar papel'),
        'electronic_answer':fields.boolean('Devuelve respuesta electronica'),
        'print_return_attribute':fields.boolean('Imprime "Su Vuelto" con atributos'),
        'current_account_automatic_pay':fields.boolean('Utiliza pago automatico como cuenta corriente'),
        'print_quantities':fields.boolean('Imprimir Cantidad de unidades'),
        'tail': fields.text('Modificaciones en el pie del ticket'),
    }

    def onchange_type(self, cr, uid, ids, type, context=None):
        r = super(epson_ar_fiscal_tf_printer_configuration, self).onchange_type(cr, uid, ids, type, context=context)
        if (type == "epson_ar_tf"):
            r['value']['protocol'] = 'epson_ar'
        return r

    def toDict(self, cr, uid, ids, context=None):
        r = super(epson_ar_fiscal_tf_printer_configuration, self).toDict(cr, uid, ids, context=context)
        fields = self._columns.keys()
        fields.remove('user_ids')
        for conf in self.read(cr, uid, ids, fields, context=context):
            if (conf['type'] == "epson_ar_tf"):
                conf_id = conf['id']
                del conf['type']
                del conf['name']
                del conf['protocol']
                del conf['id']
                del conf['tail'] # Proceso especial.
                r[conf_id] = conf
        return r


epson_ar_fiscal_tf_printer_configuration()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
