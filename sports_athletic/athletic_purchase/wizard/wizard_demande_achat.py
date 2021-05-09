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

class wizard_athletic_purchase_demande_achat(osv.osv_memory):
    _name = 'wizard_athletic_purchase.demande_achat'
    _description = 'Traitement des demandes achat'




    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value':{'partner_address_id': False, 'fiscal_position': False}}
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['default'])
        part = self.pool.get('res.partner').browse(cr, uid, part)
        pricelist = part.property_product_pricelist_purchase.id
        fiscal_position = part.property_account_position and part.property_account_position.id or False
        return {'value':{'partner_address_id': addr['default'], 'pricelist_id': pricelist}}
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Fournisseur'),
        'partner_address_id':fields.many2one('res.partner.address', 'Adresse',domain="[('partner_id', '=', partner_id)]"),
        'location_id': fields.many2one('stock.location', 'Destination'),
        'pricelist_id':fields.many2one('product.pricelist', 'Liste de prix'),

        'date_du':fields.date('Du',required=True),
        'date_au':fields.date('Au',required=True),
        'service_dem': fields.many2one('hr.department','Service demandeur',required=True),
        'state': fields.selection([('step1',u'''Choix de la période des demandes'''),('step2',u'''Choix des articles'''),('step3',u'''Appel d\'offre crée'''),('step4',u'''Bon de commande crée''')], 'Statut', readonly=True),
        'articles_ids': fields.one2many('wizard_athletic_purchase.demande_achat_articles', 'traitement_id', 'Articles'),
    }
    _defaults = {  
        'state': 'step1',
        'partner_address_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['default'])['default'],
        'pricelist_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').browse(cr, uid, context['partner_id']).property_product_pricelist_purchase.id,
                }

    def afficher_articles(self, cr, uid, ids, context=None):
        obj_demandes=self.pool.get("athletic_purchase.demande_achat")
        obj_articles=self.pool.get("athletic_purchase.demande_achat_articles")
        obj_articles_tmp=self.pool.get("wizard_athletic_purchase.demande_achat_articles")
#        obj_articles=self.pool.get("")
        art,liste_art,articles_ids=[],[],[]
        value = {}
        if context is None:
            context = {}
        datas = {}
        res_value={}
        res1 = self.read(cr, uid, ids, ['date_du','date_au','service_dem'], context=context)
        res2 = res1 and res1[0] or {}
        datas['form'] = res2


        demandes_achat=obj_demandes.search(cr,uid,[('date_dem','>=',datas['form']['date_du']),('date_dem','<=',datas['form']['date_au']),('state','=','dir_frma'),('service_dem','=',datas['form']['service_dem'])])
        if demandes_achat:
            for i in demandes_achat:
                articles_search=obj_articles.search(cr,uid,[('demande_id','=',i)])
                if articles_search:
                    for j in articles_search:
                        articles_ids.append(j)
        else:
            raise osv.except_osv(_('Alerte!'), _('Pas de demande confirmé dans cette periode'))
        if ids:
#---------suppression des articles du wizard---------
            articles_old=obj_articles_tmp.search(cr,uid,[('traitement_id','=',ids[0])])
            if articles_old:
                obj_articles_tmp.unlink(cr,uid,articles_old)

#            articles_ids=obj_articles.search(cr,uid,res[0])
            if articles_ids:
                liste_art=obj_articles.read(cr,uid,articles_ids,['demande_id','date_dem','prod_name','unit','unit_sec','quantity','quantity_sec','date_prev'])
                if liste_art:
                    for art in liste_art:
                        if art['demande_id']:
                            art['demande_id']=art['demande_id'][0]
                        if art['prod_name']:
                            art['prod_name']=art['prod_name'][0]
#                        if art['unit']:
#                            art['unit']=art['unit'][0]
#                        if art['unit_sec']:
#                            art['unit_sec']=art['unit_sec'][0]
                        art['traitement_id']=ids[0]
                        if art.get('id',False):
                            del art['id']
                        obj_articles_tmp.create(cr,uid,art)
#-----------Changement de statut------------
            res_value['state']='step2'
            self.write(cr,uid,ids,res_value)
        return True

    def appel_offre(self, cr, uid, ids, context=None):
        obj_demandes=self.pool.get("athletic_purchase.demande_achat")
        obj_articles=self.pool.get("athletic_purchase.demande_achat_articles")
        obj_articles_tmp=self.pool.get("wizard_athletic_purchase.demande_achat_articles")
        obj_offre=self.pool.get("purchase.requisition")
        obj_offre_line=self.pool.get("purchase.requisition.line")
        obj_produit=self.pool.get("product.product")
        obj_tmpl=self.pool.get("product.template")
        res_value={}
        if context is None:
            context = {}
        datas = {}
        res_value={}
        res1 = self.read(cr, uid, ids, ['date_du','date_au','service_dem'], context=context)
        res2 = res1 and res1[0] or {}
        datas['form'] = res2
        res_value={}
 
        articles_idss=obj_articles_tmp.search(cr,uid,[('traitement_id','=',ids[0])])
#        articles=obj_articles_tmp.read(cr,uid,articles_idss)
        articles=[]
        tous_articles=[]
        liste_order=[]
        liste_article_tmp=[]
        for a in obj_articles_tmp.browse(cr,uid,articles_idss):
            if a.acheter==True:
                articles.append(a.id)
#        print "articles",articles
        offre_data = {'date_start':time.strftime('%Y-%m-%d'),'service_id':datas['form']['service_dem']}
        if len(articles)!=0:
            newoffre_id = obj_offre.create(cr, uid, offre_data)
            for i in articles:
                offre_line_data = {}
                product_id=obj_articles_tmp.read(cr,uid,i,['prod_name'])['prod_name']
                product_qty=obj_articles_tmp.read(cr,uid,i,['quantity'])['quantity']
                name=obj_produit.read(cr,uid,product_id,['name'])['name']
                tmpl_id=obj_produit.read(cr,uid,product_id,['product_tmpl_id'])['product_tmpl_id'][0]
                product_uom=obj_tmpl.read(cr,uid,tmpl_id,['uom_id'])['uom_id'][0]
                tous_articles.append([product_id,product_qty,name,product_uom,newoffre_id])
            for j in tous_articles:
                if j[0] in liste_article_tmp:
                    for lo in liste_order:
                        if lo[0]==j[0]:
                            lo[1]=lo[1]+j[1]
                else:
                    liste_article_tmp.append(j[0])
                    liste_order.append(j)
            for lo in liste_order:
                newoffre_line_id = obj_offre_line.create(cr, uid, {'product_id':lo[0],'product_qty':lo[1],'product_uom_id':lo[3],'requisition_id':lo[4] })
#                offre_line_data = {'product_id':product_id,'product_qty':product_qty,'product_uom_id':product_uom,'requisition_id':newoffre_id }
#                newoffre_line_id = obj_offre_line.create(cr, uid, offre_line_data)
            res_value['state']='step3'
            self.write(cr,uid,ids,res_value)
        return True


    def demande_prix(self, cr, uid, ids, context=None):
        obj_demandes=self.pool.get("athletic_purchase.demande_achat")
        obj_articles=self.pool.get("athletic_purchase.demande_achat_articles")
        obj_articles_tmp=self.pool.get("wizard_athletic_purchase.demande_achat_articles")
        obj_order=self.pool.get("purchase.order")
        obj_order_line=self.pool.get("purchase.order.line")
        obj_produit=self.pool.get("product.product")
        obj_tmpl=self.pool.get("product.template")
        res_value={}
        if context is None:
            context = {}
        datas = {}
        res_value={}
        res1 = self.read(cr, uid, ids, ['partner_id','partner_address_id','pricelist_id','location_id'], context=context)
        res2 = res1 and res1[0] or {}
        datas['form'] = res2
        order_data = {'date_order':time.strftime('%Y-%m-%d'),'partner_id': datas['form']['partner_id'],'pricelist_id':datas['form']['pricelist_id'],'partner_address_id':datas['form']['partner_address_id'],'location_id':datas['form']['location_id']}
#        print "ok"
        articles_idss=obj_articles_tmp.search(cr,uid,[('traitement_id','=',ids[0])])
#        articles=obj_articles_tmp.read(cr,uid,articles_idss)
        articles=[]
        for a in obj_articles_tmp.browse(cr,uid,articles_idss):
            if a.acheter==True:
                articles.append(a.id)
#        print "articles",articles
        if len(articles)!=0:
            neworder_id = obj_order.create(cr, uid, order_data)
#            print "neworder ",neworder_id
            for i in articles:
                order_line_data = {}
                product_id=obj_articles_tmp.read(cr,uid,i,['prod_name'])['prod_name']
                product_qty=obj_articles_tmp.read(cr,uid,i,['quantity'])['quantity']
#                quantity_sec=obj_articles_tmp.read(cr,uid,i,['quantity_sec'])['quantity_sec']
                date_planned=obj_articles_tmp.read(cr,uid,i,['date_prev'])['date_prev']
                name=obj_produit.read(cr,uid,product_id,['name'])['name']
                tmpl_id=obj_produit.read(cr,uid,product_id,['product_tmpl_id'])['product_tmpl_id'][0]
                price_unit=obj_tmpl.read(cr,uid,tmpl_id,['standard_price'])['standard_price']
                product_uom=obj_tmpl.read(cr,uid,tmpl_id,['uom_id'])['uom_id'][0]
                order_line_data = {'product_id':product_id,'product_qty':product_qty,'date_planned':date_planned,'name':name,'price_unit':price_unit,'product_uom':product_uom,'order_id':neworder_id }
                neworder_line_id = obj_order_line.create(cr, uid, order_line_data)
                print "neworder line",neworder_line_id
            res_value['state']='step3'
            self.write(cr,uid,ids,res_value)
        return True



    def bon_commande(self, cr, uid, ids, context=None):
        obj_demandes=self.pool.get("athletic_purchase.demande_achat")
        obj_articles=self.pool.get("athletic_purchase.demande_achat_articles")
        obj_articles_tmp=self.pool.get("wizard_athletic_purchase.demande_achat_articles")
        obj_order=self.pool.get("purchase.order")
        obj_order_line=self.pool.get("purchase.order.line")
        obj_produit=self.pool.get("product.product")
        obj_tmpl=self.pool.get("product.template")
        res_value={}
        if context is None:
            context = {}
        datas = {}
        res_value={}
        res1 = self.read(cr, uid, ids, ['partner_id','partner_address_id','pricelist_id','location_id','service_dem'], context=context)
        res2 = res1 and res1[0] or {}
        datas['form'] = res2
        order_data = {'date_order':time.strftime('%Y-%m-%d'),'partner_id': datas['form']['partner_id'],'pricelist_id':datas['form']['pricelist_id'],'partner_address_id':datas['form']['partner_address_id'],'location_id':datas['form']['location_id'],'service_id':datas['form']['service_dem']}
#        print "ok"
        articles_idss=obj_articles_tmp.search(cr,uid,[('traitement_id','=',ids[0])])
#        articles=obj_articles_tmp.read(cr,uid,articles_idss)
        articles=[]
        tous_articles=[]
        liste_article_tmp=[]
        liste_order=[]
        for a in obj_articles_tmp.browse(cr,uid,articles_idss):
            if a.acheter==True:
                articles.append(a.id)
#        print "articles",articles
        if len(articles)!=0:
            neworder_id = obj_order.create(cr, uid, order_data)
#            print "neworder ",neworder_id
            for i in articles:
                order_line_data = {}
                product_id=obj_articles_tmp.read(cr,uid,i,['prod_name'])['prod_name']
                product_qty=obj_articles_tmp.read(cr,uid,i,['quantity'])['quantity']
#                quantity_sec=obj_articles_tmp.read(cr,uid,i,['quantity_sec'])['quantity_sec']
                date_planned=obj_articles_tmp.read(cr,uid,i,['date_prev'])['date_prev']
                name=obj_produit.read(cr,uid,product_id,['name'])['name']
                tmpl_id=obj_produit.read(cr,uid,product_id,['product_tmpl_id'])['product_tmpl_id'][0]
                price_unit=obj_tmpl.read(cr,uid,tmpl_id,['standard_price'])['standard_price']
                product_uom=obj_tmpl.read(cr,uid,tmpl_id,['uom_id'])['uom_id'][0]
                tous_articles.append([product_id,product_qty,date_planned,name,price_unit,product_uom,neworder_id])

            for j in tous_articles:
                if j[0] in liste_article_tmp:
                    for lo in liste_order:
                        if lo[0]==j[0]:
                            lo[1]=lo[1]+j[1]
                else:
                    liste_article_tmp.append(j[0])
                    liste_order.append(j)
            for lo in liste_order:
                obj_order_line.create(cr, uid, {'product_id':lo[0],'product_qty':lo[1],'date_planned':lo[2],'name':lo[3],'price_unit':lo[4],'product_uom':lo[5],'order_id':lo[6] })
#                order_line_data = {'product_id':product_id,'product_qty':product_qty,'date_planned':date_planned,'name':name,'price_unit':price_unit,'product_uom':product_uom,'order_id':neworder_id }
#                neworder_line_id = obj_order_line.create(cr, uid, order_line_data)
#                print "neworder line",neworder_line_id
            res_value['state']='step4'
            self.write(cr,uid,ids,res_value)
        return True
wizard_athletic_purchase_demande_achat()

class wizard_athletic_purchase_demande_achat_articles(osv.osv_memory):
    _name = "wizard_athletic_purchase.demande_achat_articles"

    def onchange_exclusif_two(self, cr, uid, ids, champ1):
        u''' Si un champ est coché l'autre est décoché '''
        value = {}
        value['indicateur']=0
        if champ1==True:
            value['indicateur'] = 1
        return {'value': value}
#-------------------------------------------------------------------------------------------------------------------------------
    _columns = {
        'traitement_id': fields.many2one('wizard_athletic_purchase.demande_achat','Demande achat',ondelete='cascade'),
        'demande_id': fields.many2one('athletic_purchase.demande_achat','Demande achat'),
        'date_dem': fields.date('Date de la demande'),
        'prod_name': fields.many2one('product.product', u'''Article''',required=True),
        'unit': fields.char('Unité Principale', size=256),
        'unit_sec': fields.char('Unité Secondaire', size=256),
        'quantity': fields.float('Quantité (UDM)'),
        'quantity_sec': fields.float('Quantité (UDS)'),
        'date_prev': fields.date('Prévu pour'),
        'acheter': fields.boolean('Sélectionner'),

    }
#-------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------
    _defaults = {
    }
#-------------------------------------------------------------------------------------------------------------------------------
wizard_athletic_purchase_demande_achat_articles()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

