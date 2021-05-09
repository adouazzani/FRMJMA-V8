# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Generdal Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
        "name" : "ATHLETIC PURCHASE",
        "version" : "1.0",
        "author" : "RIBATIS",
        "website" : "http://www.ribatis.com",
        "category" : "Edmaj - Addons",
        "description": """  Add-On pour le module PURCHASE  """,
   'depends': ['base','purchase','hr'],
    'init_xml': [],
    'update_xml': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'costum_view.xml','costum_sequence.xml',
        'notification_view.xml',
        'purchase_report.xml',
        'workflow/demande_achat.xml',
        'wizard/wizard_demande_achat.xml',
        'wizard/wizard_reporting_achat.xml',


    ],
    
    'installable': True,
    'active': False,
    'certificate':False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
