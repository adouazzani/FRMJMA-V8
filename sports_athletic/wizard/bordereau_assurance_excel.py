# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from openerp.osv import fields, osv




class athletic_bordereau_assurance_excel(osv.osv_memory):
    _name = 'athletic.bordereau.assurance.excel'
    _columns = {
        'type': fields.selection([('par_date',u'''Par Date d'assurance'''),('toutes',u'''Toutes''')], 'Impression', readonly=False),
        'state': fields.selection([('none',u''' '''),('pdf',u'''PDF'''),('excel',u'''Excel''')], 'Sortie', readonly=False),
        'date_debut': fields.datetime('Date de Début'),
        'date_fin': fields.datetime('Date de Fin'),
        'saison_id':fields.many2one('sports.saison', 'Saison sportive')
          
    }

    _defaults = {
        'state': 'none',
        'type': 'toutes',
    }





    def imprimer_assurance(self, cr, uid, ids, context=None):
        '''Impression des assurances'''
        athlete_ids=[]
        datas = {'ids': context.get('active_ids', [])}
        date_debut=self.read(cr, uid, ids[0], ['date_debut'])['date_debut']
        date_fin=self.read(cr, uid, ids[0], ['date_fin'])['date_fin']
        state=self.read(cr, uid, ids[0], ['state'])['state']
        type_print=self.read(cr, uid, ids[0], ['type'])['type']
        datas['form'] = {}
        if type_print=='par_date':
            if date_debut and date_fin:
                datas['form']['date_debut']=date_debut
                datas['form']['date_fin']=date_fin
            else:
                raise osv.except_osv(('Avertissement !'),("Veuillez Remplir Les Dates"))
            if state=='excel':
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'bordereau.assurance.excel.reedition.filtre',
                    'datas': datas,
                }

            elif state=='pdf':
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'licence.assurance.print.filtre',
                    'datas': datas,
                }
    
        elif type_print=='toutes':
            if state=='excel':
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'bordereau.assurance.excel.reedition.all',
                    'datas': datas,
                }

            elif state=='pdf':
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'licence.assurance.print.all',
                    'datas': datas,
               }

athletic_bordereau_assurance_excel()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

