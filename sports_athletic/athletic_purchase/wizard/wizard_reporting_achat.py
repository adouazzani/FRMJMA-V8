# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
import time
from osv import osv, fields
import datetime
from time import localtime
import pooler
import time
import netsvc
from osv import fields, osv
from osv.orm import except_orm
import pooler
from tools import config
from tools.translate import _
import base64
import re

class wizard_athletic_purchase_reporting_achat(osv.osv_memory):
    _name = 'wizard_athletic_purchase.reporting_achat'
    _description = 'Reporting achat'




    _columns = {

        'date_du':fields.date('Du',required=True),
        'date_au':fields.date('Au',required=True),
    }
    _defaults = {  
                }
    def print_report(self, cr, uid, ids, context=None):
        value = {}
        if context is None:
            context = {}
        datas = {}
        res1 = self.read(cr, uid, ids, ['date_du','date_au'], context=context)
        res2 = res1 and res1[0] or {}
        datas['form'] = res2
        datas['ids'] = ids
        cr.execute(""" select id from purchase_requisition where date_start between '%s' and '%s'"""%(datas['form']['date_du'],datas['form']['date_au']))
        res=cr.fetchall()
        print "resssssssssssssssssssssss",res
        if len(res)==0:
                raise osv.except_osv(_('Alerte!'), _('Pas de reporting pour cette periode'))
        value = {
                'type': 'ir.actions.report.xml',
                'report_name': 'athletic.purchase.reporting.achat',
                'datas': datas,
                }
        print "okkkkkkkkkkkkkkkkkkkwiz"
        return value
wizard_athletic_purchase_reporting_achat()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

