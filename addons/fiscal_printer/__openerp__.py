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


{   'active': False,
    'author': 'No author.',
    'category': 'base.module_category_hidden',
    'demo_xml': [],
    'depends': [u'account'],
    'description': 'No documented',
    'init_xml': [],
    'installable': True,
    'license': 'AGPL-3',
    'name': 'fiscal_printer',
    'test': [],
    'update_xml': [   u'security/fiscal_printer_group.xml',
                      u'view/journal_view.xml',
                      u'view/fiscal_printer_view.xml',
                      u'view/invoice_view.xml',
                      u'view/fical_printer_attribute_view.xml',
                      u'data/journal_properties.xml',
                      u'data/fiscal_printer_properties.xml',
                      u'data/invoice_properties.xml',
                      u'data/fical_printer_attribute_properties.xml',
                      u'data/journal_track.xml',
                      u'data/fiscal_printer_track.xml',
                      u'data/invoice_track.xml',
                      u'data/fical_printer_attribute_track.xml',
                      'security/ir.model.access.csv',
                      u'wizard/wiz_update_printers_view.xml',
                      u'wizard/wiz_update_printers_workflow.xml',
                      u'view/fiscal_printer_menuitem.xml'],
    'version': 'No version',
    'website': ''}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
