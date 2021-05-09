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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import pooler
import time
from report import report_sxw
from jasper_reports import jasper_report


def reporting_achat( cr, uid, ids, data, context ):
    params = {}
    params['date_du']=data['form']['date_du']
    params['date_au']=data['form']['date_au']
    print "paramssssssssssssssss",params
    return {"parameters": params}
jasper_report.report_jasper('report.athletic.purchase.reporting.achat','purchase.requisition',parser = reporting_achat)

