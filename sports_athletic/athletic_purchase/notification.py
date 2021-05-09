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


class purchase_extended_notification(osv.osv):
    u'''Les notifications'''
    _name="purchase.extended.notification"

    _columns={
        'name': fields.char('Nom', size=256,required=True),
        'type': fields.selection([('bon_commande','Bon de commande'),('demande_achats','Demande d\'achats')], 'Type',required=True),
        'notification_commande_ids': fields.one2many('purchase.extended.notification.commande','notification_id','Notifications', size=256),
        'notification_demande_ids': fields.one2many('purchase.extended.notification.demande','notification_id','Notifications', size=256),
        }
purchase_extended_notification()


class purchase_extended_notification_commande(osv.osv):
    u'''Bon de commande'''
    _name="purchase.extended.notification.commande"

    _columns={
        #'name': fields.char('Nom', size=256),
        'notification_id': fields.many2one('purchase.extended.notification','Notification', size=256,required=True),
        'type': fields.selection([('none','-------------------------'),('commande_valide','Bon de commande validé')], 'Type',required=True),
        'subject': fields.char('Objet', size=256,required=True),
        'body': fields.text('Template',required=True),
        'is_mail_active': fields.boolean('Mail'),
        'is_req_active': fields.boolean('Interne'),
        }

    _rec_name='type'

purchase_extended_notification_commande()


class purchase_extended_notification_demande(osv.osv):
    u'''Demandes achats'''
    _name="purchase.extended.notification.demande"

    _columns={
        #'name': fields.char('Nom', size=256),
        'notification_id': fields.many2one('purchase.extended.notification','Notification', size=256,required=True),
        'type': fields.selection([('dem_creee',"Demande d\'achats Créée"),('dem_val_rsachats',"Demande Validée Par le responsable des achats"),('dem_val_rsfinancier',"Demande Validée Par le responsable financier"),('dem_val_dir',"Demande Validée Par le directeur"),('dem_rejetee',"Demande Rejetée")], 'Type', readonly=False,required=True),
        'subject': fields.char('Objet', size=256,required=True),
        'body': fields.text('Template',required=True),
        'is_mail_active': fields.boolean('Mail'),
        'is_req_active': fields.boolean('Interne'),
        }

    _rec_name='type'

purchase_extended_notification_demande()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
