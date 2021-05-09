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
from osv import osv,fields 
import time
import tools


def alerte(message):
    raise osv.except_osv(('Avertissement !'),(message))


def get_group(self,cr, uid, group_model ,group_xml_name, context=None):
    '''Retourne les groupes en donnant en parametre les noms dans xml'''
    dataobj = self.pool.get('ir.model.data')
    result = []
    try:
        dummy,group_id = dataobj.get_object_reference(cr, 1, group_model, group_xml_name)
        if dummy=='res.groups':
            result.append(group_id)
    except ValueError:
        # If these groups does not exists anymore
        pass
    return result

def get_user_groups(self,cr,uid):
    '''Retourne les groupes de l'utilisateur'''
    obj_user=self.pool.get("res.users")
    groups_id=obj_user.read(cr,uid,uid,['groups_id'])['groups_id']
    return groups_id

URL = "https://194.204.222.18"
URL_DEMANDE = "/openerp/menu?active=551#url=%2Fopenerp%2Fform%2Fview%3Fmodel%3Dathletic_purchase.demande_achat%26id%3D"
URL_COMMANDE = "/openerp/menu?active=551#url=%2Fopenerp%2Fform%2Fview%3Fmodel%3Dpurchase.order%26id%3D"

def get_variables_demande(self,cr,uid,ids):
#Fonction generique qui rapporte les variables de la notif du wkf demande d'achats
    obj_demande=self.pool.get("athletic_purchase.demande_achat")
    demande_read=obj_demande.read(cr,uid,ids[0],['objet_dem','date_dem','code','service_dem','responsable_dem'])
    liste_var=[]
    if demande_read['code']:
        liste_var.append(('[[code_demande]]',demande_read['code']))
    #if demande_read['date_dem']:
    #    liste_var.append(('[[date_demande]]',demande_read['date_dem']))
    if demande_read['service_dem']:
        liste_var.append(('[[service_dem]]', demande_read['service_dem'][1] ) )
    else:
        liste_var.append(('[[service_dem]]', ""))
    if demande_read['responsable_dem']:
        liste_var.append(('[[responsable_dem]]', demande_read['responsable_dem'][1] ) )
    else:
        liste_var.append(('[[responsable_dem]]', ""))
    liste_var.append(('[[ref]]', demande_read.get('code',"") or ""))
    liste_var.append(('[[code]]', demande_read.get('code',"") or ""))
    liste_var.append(('[[date_dem]]', demande_read.get('date_dem',"") or ""))
    liste_var.append(('[[objet_dem]]', demande_read.get('objet_dem',"") or ""))
    
    obj_user=self.pool.get("res.users")
    responsable=obj_user.read(cr,uid,uid,['name'])['name']
    liste_var.append(('[[responsable]]',responsable))
    liste_var.append(('[[url]]', URL + URL_DEMANDE + str(ids[0])))
    print liste_var
    return liste_var


def get_variables_commande(self,cr,uid,ids):
#Fonction generique qui rapporte les variables de la notif du wkf achats
    ###print "utilsssssssssssssssssssssssssssssssssssssssssssssss"
    obj_demande=self.pool.get("purchase.order")
    demande_read=obj_demande.read(cr,uid,ids[0],['name','date_order','objet_cmd'])
    liste_var=[]
    if demande_read['name']:
        liste_var.append(('[[ref_commande]]',demande_read['name']))
    #if demande_read['date_order']:
    #    liste_var.append(('[[date_commande]]',demande_read['date_order']))

    liste_var.append(('[[ref]]', demande_read.get('name',"") or ""))
    liste_var.append(('[[date_order]]', demande_read.get('date_order',"") or ""))
    liste_var.append(('[[date_commande]]', demande_read.get('date_order',"") or ""))
    liste_var.append(('[[objet_cmd]]', demande_read.get('objet_cmd',"") or ""))

    obj_user=self.pool.get("res.users")
    responsable=obj_user.read(cr,uid,uid,['name'])['name']
    liste_var.append(('[[responsable]]',responsable))
    liste_var.append(('[[url]]', URL + URL_COMMANDE + str(ids[0])))
    return liste_var

def get_group_users(self, cr, uid,ids,group_id):
    u'''Retourne listes des ids des utilisateur appartenant au groupe group_id'''
    res,resu=[],[]
    sql_req= """SELECT * FROM res_groups_users_rel where gid=%d""" %(int(group_id))
    cr.execute(sql_req)
    res=cr.fetchall()
    if res:
        for r in res:
            if r :
                resu.append(r[0])

    return resu





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
