# -*- encoding: utf-8 -*-
######################################################################################################################
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
######################################################################################################################
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
import dispatcher
import utils




#===============================================================================================================================
#                           Demande achat
#===============================================================================================================================
class athletic_purchase_demande_achat(osv.osv):
    _name = "athletic_purchase.demande_achat"

    def fields_get(self, cr, uid, fields=None, context=None):
        res = super(athletic_purchase_demande_achat,self).fields_get(cr, uid, fields, context)
        if context != None:
            if 'department_id' in context:
                if 'service_dem' in res :
                    res['service_dem']['domain']=[('id','=',context['department_id'])]
        return res
#-------------------------------------------------------------------------------------------------------------------------------
    def onchange_manager_dem(self, cr, uid, id, department):
        cr.execute("""SELECT r.user_id FROM hr_department d,hr_employee e,resource_resource r where d.manager_id=e.id and e.resource_id=r.id and d.id=%d"""%(department))
        res=cr.fetchall()
        if len(res)==0:
            return {}
        return {'value': {'responsable_dem':res[0][0]}}

    def onchange_departement(self, cr, uid, id, demandeur):
        cr.execute("""SELECT context_department_id FROM res_users where id=%d"""%(demandeur))
        res=cr.fetchall()
        if len(res)==0:
            return {}
        return {'value': {'service_dem':res[0][0]}}

    def onchange_manager_dest(self, cr, uid, id, department):
        cr.execute("""SELECT manager_id FROM hr_department where id=%d"""%(department))
        res=cr.fetchall()
        print "res",res
        if len(res)==0:
            return {}
        return {'value': {'responsable_dest':res[0][0]}}

#-------------------------------------------------------------------------------------------------------------------------------
    _columns = {
        'objet_dem': fields.char('Objet', size=256,required=True),
        'code': fields.char('N° Demande', size=256,readonly=True),
        'date_dem':fields.date('Demande du',required=True),
        'service_dem': fields.many2one('hr.department','Service demandeur',required=True),
        'service_dest': fields.many2one('hr.department','Service destinataire'),
        'responsable_dem': fields.many2one('res.users','Responsable',readonly=True),
        'responsable_dest': fields.many2one('hr.employee','Responsable'),
        'objet': fields.char('Objet', size=256),
        'objet_mode': fields.char('Mode de lancement de l\'offre', size=256),
        'description': fields.text('commentaire'),
        'societes': fields.many2many('res.partner','athletic_purchase_demande_achat_partner_rel','demande_id','partner_id'),
        'articles_ids': fields.one2many('athletic_purchase.demande_achat_articles','demande_id'),
        'criteres_ids': fields.one2many('athletic_purchase.demande_achat_critere_evaluation_offre','demande_id'),

        'state': fields.selection([('non','  '),('draft','Brouillon'),('resp_dem','Validée par le responsable des achats'),('resp_fin','Validée par le responsable financier'),('dir_frma','Validée par le directeur FRMA'),('cancel','Rejetée')], 'Statut', readonly=True),
        'user_creation': fields.many2one('res.users', 'Par', readonly=True),
        'date_creation': fields.datetime('Création de la demande le', readonly=True),
        'user_draft': fields.many2one('res.users', 'Par', readonly=True),
        'date_draft': fields.datetime('Validé par le responsable des achats le', readonly=True),
        'user_resp_dem': fields.many2one('res.users', 'Par', readonly=True),
        'date_resp_dem': fields.datetime('Validé par le responsable financier le', readonly=True),
        'user_resp_fin': fields.many2one('res.users', 'Par', readonly=True),
        'date_resp_fin': fields.datetime('Validé par le directeur FRMA le', readonly=True),
        'user_cancel': fields.many2one('res.users', 'Par', readonly=True),
        'date_cancel': fields.datetime('Refusé le', readonly=True),

}
#******************
    _rec_name ='code'
    _order ='code desc'
    _defaults = {  
        'responsable_dem' : lambda self,cr,uid,ctx : uid,
        'state':'non',
        'date_dem': lambda *a: time.strftime("%Y-%m-%d"),
        }
#-------------------------------------------------------------------------------------------------------------------------------
    def action_draft(self, cr, uid, ids):
        print "action_draft"
        self.write(cr, uid, ids, { 'state' : 'draft' })
        self.write(cr, uid, ids, {'date_creation': time.strftime('%Y-%m-%d %H:%M:%S'), 'user_creation': uid  })
#-----------------------------------------------Notifications------------------------------------------
        users_ids,liste_var=[],[]
        liste_var=utils.get_variables_demande(self,cr,uid,ids)
 #--> emailto
        group_obj = self.pool.get('res.groups')
        groups_ids = group_obj.search(cr, uid, [('name','=','RESPONSABLE DES ACHATS')])
        sql_query = 'select distinct uid from res_groups_users_rel where gid in (' + ','.join(map(str, groups_ids)) + ')'
        cr.execute(sql_query)
        users_ids = map(lambda x: x[0], cr.fetchall())   # list(set(maliste)) or select distinct
        if users_ids:
            dispatcher.notify_set(self, cr, uid, "purchase.extended.notification","demande_achats","purchase.extended.notification.demande","dem_creee", liste_var, users_ids, context={})
        return True
    def action_resp_dem(self, cr, uid, ids):
        print "action_resp_dem"
        for inv in self.browse(cr, uid, ids):
            if not inv.articles_ids:
                raise osv.except_osv(_('Articles !'), _('La liste des articles est vide'))
        self.write(cr, uid, ids, { 'state' : 'resp_dem' })
        self.write(cr, uid, ids, {'date_draft': time.strftime('%Y-%m-%d %H:%M:%S'), 'user_draft': uid  })
#-----------------------------------------------Notifications------------------------------------------
        users_ids,liste_var=[],[]
        liste_var=utils.get_variables_demande(self,cr,uid,ids)
 #--> emailto
        group_obj = self.pool.get('res.groups')
        groups_ids = group_obj.search(cr, uid, [('name','=','Accounting / Manager')])
        sql_query = 'select distinct uid from res_groups_users_rel where gid in (' + ','.join(map(str, groups_ids)) + ')'
        cr.execute(sql_query)
        users_ids = map(lambda x: x[0], cr.fetchall())   # list(set(maliste)) or select distinct
        if users_ids:
            dispatcher.notify_set(self, cr, uid, "purchase.extended.notification","demande_achats","purchase.extended.notification.demande","dem_val_rsachats", liste_var, users_ids, context={})
        return True
    def action_resp_fin(self, cr, uid, ids):
        for inv in self.browse(cr, uid, ids):
            if not inv.articles_ids:
                raise osv.except_osv(_('Articles !'), _('La liste des articles est vide'))
        self.write(cr, uid, ids, { 'state' : 'resp_fin' })
        self.write(cr, uid, ids, {'date_resp_dem': time.strftime('%Y-%m-%d %H:%M:%S'), 'user_resp_dem': uid  })
#-----------------------------------------------Notifications------------------------------------------
        users_ids,liste_var=[],[]
        liste_var=utils.get_variables_demande(self,cr,uid,ids)
 #--> emailto
        group_obj = self.pool.get('res.groups')
        groups_ids = group_obj.search(cr, uid, [('name','=','DIRECTION FRMA')])
        sql_query = 'select distinct uid from res_groups_users_rel where gid in (' + ','.join(map(str, groups_ids)) + ')'
        cr.execute(sql_query)
        users_ids = map(lambda x: x[0], cr.fetchall())   # list(set(maliste)) or select distinct
        if users_ids:
            dispatcher.notify_set(self, cr, uid, "purchase.extended.notification","demande_achats","purchase.extended.notification.demande","dem_val_rsfinancier", liste_var, users_ids, context={})
        return True
    def action_dir_frma(self, cr, uid, ids):
        for inv in self.browse(cr, uid, ids):
            if not inv.articles_ids:
                raise osv.except_osv(_('Articles !'), _('La liste des articles est vide'))
        self.write(cr, uid, ids, { 'state' : 'dir_frma' })
        self.write(cr, uid, ids, {'date_resp_fin': time.strftime('%Y-%m-%d %H:%M:%S'), 'user_resp_fin': uid  })
#-----------------------------------------------Notifications------------------------------------------
        users_ids,liste_var=[],[]
        liste_var=utils.get_variables_demande(self,cr,uid,ids)
 #--> emailto
        group_obj = self.pool.get('res.groups')
        groups_ids = group_obj.search(cr, uid, [('name','in',('RESPONSABLE DES ACHATS','RESPONSABLE FINANCIER','Purchase / Manager'))])
        sql_query = 'select distinct uid from res_groups_users_rel where gid in (' + ','.join(map(str, groups_ids)) + ')'
        cr.execute(sql_query)
        users_ids = map(lambda x: x[0], cr.fetchall())   # list(set(maliste)) or select distinct
        if users_ids:
            dispatcher.notify_set(self, cr, uid, "purchase.extended.notification","demande_achats","purchase.extended.notification.demande","dem_val_dir", liste_var, users_ids, context={})
        return True
    def action_cancel(self, cr, uid, ids):
        self.write(cr, uid, ids, { 'state' : 'cancel' })
        self.write(cr, uid, ids, {'date_cancel': time.strftime('%Y-%m-%d %H:%M:%S'), 'user_cancel': uid  })
#-----------------------------------------------Notifications------------------------------------------
        users_ids,liste_var=[],[]
        liste_var=utils.get_variables_demande(self,cr,uid,ids)
 #--> emailto
        user_id=self.read(cr, uid,ids[0], ['responsable_dem'])['responsable_dem']
        if user_id:
            users_ids = [user_id[0]]
            dispatcher.notify_set(self, cr, uid, "purchase.extended.notification","demande_achats","purchase.extended.notification.demande","dem_rejetee", liste_var, users_ids, context={})
        return True
#-------------------------------------------------------------------------------------------------------------------------------
    def create(self, cr, user, vals, context=None):
        vals['code'] = self.pool.get('ir.sequence').get(cr, user,'demande.achat')
        res=super(athletic_purchase_demande_achat, self).create(cr, user, vals, context)
        return res
athletic_purchase_demande_achat()
#===============================================================================================================================
#                           Articles
#===============================================================================================================================
class athletic_purchase_demande_achat_articles(osv.osv):
    _name = "athletic_purchase.demande_achat_articles"
#-------------------------------------------------------------------------
    def unite_produit(self, cr, uid,id,product_id):
        valeur={}
        cr.execute("""select  uom.name from product_product produit,product_template tmpl,product_category categ,product_uom uom where  produit.product_tmpl_id=tmpl.id and tmpl.categ_id=categ.id and tmpl.uom_id=uom.id and produit.id=%d"""%(product_id))
        res=cr.fetchall()
        if len(res)==0:
            return {'value':valeur}
        else:
            valeur['unit']=res[0][0]
        cr.execute("""SELECT pu.name, pt.uos_coeff FROM product_template pt JOIN product_product pp ON pp.product_tmpl_id=pt.id JOIN product_uom pu ON pt.uos_id=pu.id WHERE pp.id=%d"""%(product_id))
        res=cr.fetchall()
        if len(res)==0:
            return {'value':valeur}
        else:
            valeur['unit_sec']=res[0][0]
        return {'value':valeur}
    
    
    def onchange_quantity(self, cr, uid, id, product_id, quantity):
        cr.execute("""SELECT pu.name, pt.uos_coeff FROM product_template pt JOIN product_product pp ON pp.product_tmpl_id=pt.id JOIN product_uom pu ON pt.uos_id=pu.id WHERE pp.id=%d"""%(product_id))
        res=cr.fetchall()
        if len(res)==0:
            return {}
        return {'value': {'unit_sec':res[0][0], 'quantity_sec':quantity*res[0][1]}}

    def onchange_quantity_sec(self, cr, uid, id, product_id, quantity):
        cr.execute("""SELECT pu.name, pt.uos_coeff FROM product_template pt JOIN product_product pp ON pp.product_tmpl_id=pt.id JOIN product_uom pu ON pt.uos_id=pu.id WHERE pp.id=%d"""%(product_id))
        res=cr.fetchall()
        if len(res)==0:
            return {}
        if res[0][1]==0:
            return {}
        return {'value': {'unit_sec':res[0][0], 'quantity':quantity/res[0][1]}}
#-------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------
    _columns = {
        'demande_id': fields.many2one('athletic_purchase.demande_achat','Demande achat',ondelete='cascade'),
        'date_dem': fields.related('demande_id', 'date_dem', type='date',  string='Date de la demande',store=True),
        'state': fields.related('demande_id', 'state', type='selection',selection=[('draft','Brouillon'),('resp_dem','Validé par le responsable du demandeur'),('resp_fin','Validé par le responsable financier'),('dir_frma','Validé par le directeur FRMA')],  string='Statut'),
        'prod_name': fields.many2one('product.product', u'''Article''',required=True),
        'unit': fields.char('Unité Principale', size=256),
        'unit_sec': fields.char('Unité Secondaire', size=256),
        'quantity': fields.float('Quantité (UDM)'),
        'quantity_sec': fields.float('Quantité (UDS)'),
        'date_prev': fields.date('Prévu pour',required=True),
        'acheter': fields.boolean('Sélectionner'),
        'manual': fields.text('commentaire'),

    }
#-------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------
    _defaults = {
    }
#-------------------------------------------------------------------------------------------------------------------------------
athletic_purchase_demande_achat_articles()
#===============================================================================================================================
#                           Articles TMP
#===============================================================================================================================

#===============================================================================================================================
#                           Statut marché & convention
#===============================================================================================================================
class athletic_purchase_demande_achat_critere_evaluation_offre(osv.osv):
    _name = "athletic_purchase.demande_achat_critere_evaluation_offre"
    _columns = {
        'demande_id': fields.many2one('athletic_purchase.demande_achat','Demande achat'),
        'name':fields.char('Libellé du critère', size=256,required=True),
    }
athletic_purchase_demande_achat_critere_evaluation_offre()

#===============================================================================================================================
#                           Heritage de la fournisseur ajouter le fax
#===============================================================================================================================
class res_partner(osv.osv):
    _name="res.partner"
    _inherit="res.partner"
    _table="res_partner"

    _columns={

        'fax': fields.related('address', 'fax', type='char', string='Fax'),

    }
res_partner()
#===============================================================================================================================
#                           Purchase_order:Notification pour la confirmation de la commande
#===============================================================================================================================
class purchase_order(osv.osv):
    _name = "purchase.order"
    _inherit = 'purchase.order'
    _table = 'purchase_order'

#-------------------------------------------------------------------------------------------------------------------------------
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            if not po.order_line:
                raise osv.except_osv(_('Error !'),_('You can not confirm purchase order without Purchase Order Lines.'))
            for line in po.order_line:
                if line.state=='draft':
                    todo.append(line.id)
            message = _("Purchase order '%s' is confirmed.") % (po.name,)
            self.log(cr, uid, po.id, message)
#        current_name = self.name_get(cr, uid, ids)[0][1]
        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid})
        marche_obj = self.pool.get('edmaj_exp.gestion_marche_convention')
        bordr_obj = self.pool.get('edmaj_exp.bordereau_prix')
        oline_obj = self.pool.get('purchase.order.line')
        for po in self.browse(cr, uid, ids, context=context):
            if po.reference_type:
                marche_id=po.reference_type.id
                marche_obj.write(cr, uid, [marche_id], {'adjucataire' : po.partner_id.id})
                for line in po.order_line:
                    name=oline_obj.read(cr,uid,line.id,['product_id'])['product_id'][0]
                    libelle=oline_obj.read(cr,uid,line.id,['name'])['name']
                    prix_unit=oline_obj.read(cr,uid,line.id,['price_unit'])['price_unit']
                    product_qty=oline_obj.read(cr,uid,line.id,['product_qty'])['product_qty']
                    prix=prix_unit*product_qty
                    bordr_obj.create(cr,uid,{'name': name,'libelle': libelle,'quantite': product_qty,'prix': prix,'marche_id':marche_id})
#-----------------------------------------------Notifications------------------------------------------
        users_ids,liste_var=[],[]
        liste_var=utils.get_variables_commande(self,cr,uid,ids)
 #--> emailto
        group_obj = self.pool.get('res.groups')
        groups_ids = group_obj.search(cr, uid, [('name','in',('Warehouse / Manager','Accounting / Manager'))])
        sql_query = 'select distinct uid from res_groups_users_rel where gid in (' + ','.join(map(str, groups_ids)) + ')'
        cr.execute(sql_query)
        users_ids = map(lambda x: x[0], cr.fetchall())   # list(set(maliste)) or select distinct
        if users_ids:
            dispatcher.notify_set(self, cr, uid, "purchase.extended.notification","bon_commande","purchase.extended.notification.commande","commande_valide", liste_var, users_ids, context={})
        return True
#-------------------------------------------------------------------------------------------------------------------------------
purchase_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
