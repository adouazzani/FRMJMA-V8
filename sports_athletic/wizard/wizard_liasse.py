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
from openerp.osv import osv, fields
from openerp.osv.orm import except_orm
import time
import openerp.netsvc
from openerp.tools.translate import _

import openerp.pooler
#import attachsvc
from datetime import datetime
from tempfile import TemporaryFile 
from xlrd import open_workbook, cellname 
from xlutils.copy import copy

from xlwt import *
from xlwt.ExcelFormulaParser import FormulaParseException
from getxlwtstylelist import get_xlwt_style_list  
#from percent import percent_fields
import os

from openerp.osv.orm import except_orm
#import wizard
from openerp.osv import osv
import openerp.pooler as pooler
from openerp.tools.translate import _
    
import os
import time  
import random
import string 
import openerp.netsvc as netsvc

def log(message):
    print "here"
    #netsvc.Logger().notifyChannel('IMPRESSION LIASSE FISCALE ', netsvc.LOG_INFO, ":: %s" % message)

template = "TemplateLF" 
_columns_account=['code','name','debit','credit','balance']



def xl_config(cr, uid, name):
    #pooler.get_pool(cr.dbname).get('edmaj_atr.property').getValue(cr, uid, name)
    return pooler.get_pool(cr.dbname).get('edmaj_atr.property')


def output_name(baseName):
    random.seed()
    d = [random.choice(string.ascii_letters) for x in xrange(20) ]
    name = "".join(d)
    return  time.strftime('%Y_%m_%d_%H_%M') + '_' + baseName + '_' + name + '.xls'

def output_path(cr, uid, name):
    path = "openerp/static/account_liasse/"
    output = "/home/gnaoui/Bureau/"
    if not os.path.isdir(output): 
        try:
            os.makedirs(output)
        except:
            raise except_orm(_('Permission Denied !'), _('You do not have permissions to write on the server side.'))
    return output + name;

def output_url(cr, uid, name):
    return "http://localhost:7015/web/" + "openerp/static/account_liasse/" + name;

def input_template(cr, uid, name):
    #return "sports_athletic/wizard/XLTemplates/" + name + ".xls"
    return "/home/gnaoui/Documents/Odoo_workspace/015_FRMA/frma_env/addons/sports_athletic/wizard/XLTemplates/TemplateLF.xls"
      




class wizard_liasse(osv.osv_memory):
    _name = "wizard.liasse"


#=====================================================================================================================================================
    def _toXl(self, cr, uid, ids, input_path, output_path, context, context2):
        """ 
            Exporter la Balance vers un fichier Excel 
        """
        log("Ouverture du template Excel...")
        try:
            print input_path
            rb = open_workbook(input_path, formatting_info=True, encoding_override="cp1252") 
        except Exception,e:
            log("Impossible d\'ouvrir le template.")
            raise osv.except_osv(_("*** Fichier modèle ***"),
                                 _("Impossible de lire le fichier Excel modèle! Vérifier que le fichier existe dans le chemin spécifié."))
        
        comptes_list=self.pool.get('account.account').search(cr, uid, [])
        log("Lecture des valeurs des comptes...")
        readData2=self.pool.get('account.account').read(cr, uid, comptes_list, _columns_account, context2)
        readData=self.pool.get('account.account').read(cr, uid, comptes_list, _columns_account, context)
        
        date_start = self.pool.get('account.period').read(cr, uid, min(context['periods']), ['date_start'])['date_start']
        date_stop = self.pool.get('account.period').read(cr, uid, max(context['periods']), ['date_stop'])['date_stop']
        period = "Du : " + str(time.strftime('%d/%m/%Y', time.strptime(date_start, '%Y-%m-%d'))) + " Au : " + str(time.strftime('%d/%m/%Y', time.strptime(date_stop, '%Y-%m-%d')))
        
        company = self.pool.get('res.users').read(cr, uid, uid, ['company_id'])['company_id'][1]
        
        date = datetime.now().strftime("%d/%m/%Y")

        style_list = get_xlwt_style_list(rb) 
        wb = copy(rb)
            
        log("Alimentation de la Balance...")                
        for sheet_index in  range(rb.nsheets):
            rs=rb.sheet_by_index(sheet_index)
            ws=wb.get_sheet(sheet_index)
            if sheet_index == 0:
                taille=len(readData)
                rowp=1
                colp=0
                for i in range(taille):
                    code = readData[i]['code']
                    if code[0] == '0':
                        continue
                    if len(code) > 4 and code[-4:] == '0000': # Les 4 derniers chiffres sont des zeros
                        code = code[:-4] 
                    if len(code) > 4 or code[0] == '0':
                        continue
                    
                    ws.write(rowp, colp, code, style_list[rs.cell(rowp, colp).xf_index])
                    ws.write(rowp,colp+1,readData[i]['name'],style_list[rs.cell(rowp, colp+1).xf_index])
                    ws.write(rowp,colp+2,readData[i]['debit'],style_list[rs.cell(rowp, colp+2).xf_index])
                    ws.write(rowp,colp+3,readData[i]['credit'],style_list[rs.cell(rowp, colp+3).xf_index])
                    ws.write(rowp,colp+4,readData[i]['balance'],style_list[rs.cell(rowp, colp+4).xf_index])
                    if 'fiscalyear' in context2:
                        ws.write(rowp,colp+5,readData2[i]['debit'],style_list[rs.cell(rowp, colp+5).xf_index])
                        ws.write(rowp,colp+6,readData2[i]['credit'],style_list[rs.cell(rowp, colp+6).xf_index])
                        ws.write(rowp,colp+7,readData2[i]['balance'],style_list[rs.cell(rowp, colp+7).xf_index])
                    else:
                        ws.write(rowp,colp+5,0,style_list[rs.cell(rowp, colp+5).xf_index])
                        ws.write(rowp,colp+6,0,style_list[rs.cell(rowp, colp+6).xf_index])
                        ws.write(rowp,colp+7,0,style_list[rs.cell(rowp, colp+7).xf_index])
                    rowp +=1
                continue
            
            if sheet_index == 2:
                ws.write(0, 1, company, style_list[rs.cell(0, 1).xf_index])
                """ws.write(1, 1, address, style_list[rs.cell(1, 1).xf_index])
                ws.write(2, 1, city, style_list[rs.cell(2, 1).xf_index])"""
                ws.write(5, 1, date, style_list[rs.cell(5, 1).xf_index])
                ws.write(6, 1, period, style_list[rs.cell(6, 1).xf_index])
                continue
                 
        wb.save(output_path)
        return output_path

    
    
    
    def _toXlFormulas(self, cr, uid, ids, input_path, output_path,context,context2):
        """ 
            Prendre le fichier précédent puis effectuer les traitements 
        """
        try:
            rb = open_workbook(input_path, formatting_info=True, encoding_override="cp1252")
        except Exception,e:
            log("Impossible d\'ouvrir le template.")
            raise osv.except_osv(_("*** Ficher modèle ***"),
                                 _("Impossible de lire le fichier Excel modèle! Vérifier que le fichier existe dans le chemin spécifié."))    
        
        style_list = get_xlwt_style_list(rb) 
        wb = copy(rb)
            
        log("Preparation de la Balance triee...")                
        for sheet_index in  range(rb.nsheets):
            rs=rb.sheet_by_index(sheet_index)
            ws=wb.get_sheet(sheet_index)
            
            rs0 = rb.sheet_by_index(0)
            ws0 = wb.get_sheet(0)
            rs1 = rb.sheet_by_index(1)
            ws1 = wb.get_sheet(1)
            log("Conversion des formules Excel...")
            for row in range(min(rs.nrows,10000))  : 
                if row != 0: # Entete 1ere feuille BAL
                    value0_code = rs0.cell(row,0).value
                    value0_name = rs0.cell(row,1).value
                    value0_cdebit = rs0.cell(row,2).value
                    value0_ccredit = rs0.cell(row,3).value
                    value0_csolde = rs0.cell(row,4).value
                    value0_pdebit = rs0.cell(row,5).value
                    value0_pcredit = rs0.cell(row,6).value
                    value0_psolde = rs0.cell(row,7).value
                    
                    if type(value0_code).__name__!='unicode' :
                        continue
                    value0_code = value0_code.encode('utf-8')
                    if value0_code == 'pcg' or value0_code[0] == '0':
                        continue
                        
                    ws1.write(int(value0_code)-1, 0, value0_code, style_list[rs1.cell(int(value0_code)-1,0).xf_index])
                    ws1.write(int(value0_code)-1, 1, value0_name, style_list[rs1.cell(int(value0_code)-1,0).xf_index])
                    ws1.write(int(value0_code)-1, 2, value0_cdebit, style_list[rs1.cell(int(value0_code)-1,0).xf_index])
                    ws1.write(int(value0_code)-1, 3, value0_ccredit, style_list[rs1.cell(int(value0_code)-1,0).xf_index])
                    ws1.write(int(value0_code)-1, 4, value0_csolde, style_list[rs1.cell(int(value0_code)-1,0).xf_index])
                    ws1.write(int(value0_code)-1, 5, value0_pdebit, style_list[rs1.cell(int(value0_code)-1,0).xf_index])
                    ws1.write(int(value0_code)-1, 6, value0_pcredit, style_list[rs1.cell(int(value0_code)-1,0).xf_index])
                    ws1.write(int(value0_code)-1, 7, value0_psolde, style_list[rs1.cell(int(value0_code)-1,0).xf_index])
                            
                            
                for col in range(min(rs.ncols, 100)):
                    value = rs.cell(row,col).value	
                    if type(value).__name__!='unicode':
						continue
                    elif value.find('$$=') >= 0:
                        formuleatxt = str(value)[3:]
                        formuleatxt = formuleatxt.replace('$$=', '=')
                        if formuleatxt.find("+") == 0:
                            formuleatxt = formuleatxt[1:]
                        try:
                            formula = Formula(formuleatxt)
                            ws.write(row, col, formula, style_list[rs.cell(row, col).xf_index])
                        except Exception,e:
                            log( "Could not parse %r: %s in %s/%r/%r" % (formuleatxt,e.args[0], sheet_index, row, col )) 
                        
        log("Enregistrement de la Liasse...")
        wb.save(output_path)
        return output_path
    
    
#======================================================================================================================================================
    _columns = {
        'fiscalyear': fields.many2one('account.fiscalyear', \
                                    'Année', required=True),
        'period_from': fields.many2one('account.period', 'Début de période'),
        'period_to': fields.many2one('account.period', 'Fin de période'),
    }
    
    
    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear_id=False, context=None):
        res = {}
        res['value'] = {}
        if fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               ORDER BY p.date_start ASC
                               LIMIT 1) AS period_start
                UNION
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
            periods =  [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 1:
                start_period = periods[0]
                end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to': end_period}
        return res

    def print_report(self, cr, uid, ids, context):
        data = self.read(cr, uid, ids, [], context=context)[0]
        context2={}
        for k,v in context.iteritems():
            context2[k]=v
#-------------------------------------------------------------------------------------------------------------------------------------------------
        print data['period_from']
        cr.execute("""SELECT date_start-1  FROM account_period WHERE id=%d"""%(data['period_from'][0]))
        res1=cr.fetchall()
        date_start=res1[0][0]
        cr.execute("""SELECT fiscalyear_id  FROM account_period WHERE date_stop='%s' """%(date_start))
        res=cr.fetchall()
        if len(res)!=0:
            prec_fiscalyear_id = res[0][0]
            cr.execute("""SELECT id  FROM account_period WHERE fiscalyear_id=%d"""%(prec_fiscalyear_id))
            resu=cr.fetchall()
            l=[]
            t=len(resu)
            if t!=0:
                for i in range(t):
                    l.append(resu[i][0])
                context2['fiscalyear']= prec_fiscalyear_id
                context2['periods']= l
#-------------------------------------------------------------------------------------------------------------------------------------------------
        period_obj = self.pool.get('account.period')
        fy_obj = self.pool.get('account.fiscalyear')

        result={}
        result2={}
        result['periods'] = []
        if data['period_from'] and data['period_to']:
            result['periods'] = period_obj.build_ctx_periods(cr, uid, data['period_from'][0], data['period_to'][0])
        context['fiscalyear']= data['fiscalyear']
        context['periods']= result['periods']
        
        pool = pooler.get_pool(cr.dbname)
        xl_name = output_name(template)
        input = input_template(cr, uid, template)
        output = output_path(cr, uid, xl_name)
        url = output_url(cr, uid, xl_name)
        
        out = self._toXl(cr, uid,ids, input, output,context,context2)
        aw = {
            'url': "%s" % (url)  ,

            'type': 'ir.actions.act_url' ,
            'target': 'current'
        }
        #log(str(aw))
        aw['url']
        self._toXlFormulas(cr, uid, ids, out, output, context, context2)
        log(str(aw))
        return aw


wizard_liasse()

 

