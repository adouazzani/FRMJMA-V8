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

from osv import osv
from osv import fields
from tools.translate import _
import time
import pooler

import netsvc
import tools
import os
import smtpclient
from email import Encoders
from email.Message import Message
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate



def dispatch_request(cr, uid, subject, body, transmitter, recipients, data={}):
    """ Envoi de Requête Interne """
    request_obj = pooler.get_pool(cr.dbname).get('res.request')
    ###print transmitter, recipients
    for recipient in recipients:
        req_id = request_obj.create(cr, uid,
                        {'name': subject, 
                         'act_from': transmitter, 
                         'act_to': recipient, 
                         'body': body, 
                         'res_url': data.get('url',False),
                         'state': 'waiting'}
                   )
    return True
    
    

def dispatch_mail(self, cr, uid, subject, body, toemail):
    """ Envoi de Mail """
    obj_server = self.pool.get("email.smtpclient")
    server_ids = obj_server.search(cr,uid,[])
    for serverid in server_ids:
        con = obj_server.open_connection(cr, uid, server_ids, serverid)
        try:
            msg = MIMEText(body.encode('utf8') or '',_subtype='plain',_charset='utf-8')
        except:
            msg = MIMEText(body or '',_subtype='plain',_charset='utf-8')
        
        msg['To'] = toemail
        msg['From'] = tools.ustr(obj_server.server[serverid]['from_email'])
        
        msg['Subject'] = _(subject)
        message = msg.as_string()
        
        queue = pooler.get_pool(cr.dbname).get('email.smtpclient.queue')
        queue.create(cr, 1, {
                'to': toemail,
                'server_id': serverid,
                'name': msg['Subject'],
                'body': body,
                'serialized_message': message,
            })
    return True
    
    


def notify_set(self, cr, uid, notification_table,type_notification,notification_template,type_template, liste_var, user_ids, context={}):
    user_obj = self.pool.get('res.users')
    obj_notification=self.pool.get(notification_table)
    obj_notification_template=self.pool.get(notification_template)
    notification_id=obj_notification.search(cr,uid,[('type','=',type_notification)])
    ###print "NOTIFIFFIF"
    ###print notification_id
    if notification_id:
        template_id=obj_notification_template.search(cr,uid,[('notification_id','=',notification_id[0]),('type','=',type_template)])
        if template_id:
            subject=obj_notification_template.read(cr,uid,template_id[0],['subject'])['subject']
            body=obj_notification_template.read(cr,uid,template_id[0],['body'])['body']
            is_mail_active=obj_notification_template.read(cr,uid,template_id[0],['is_mail_active'])['is_mail_active']
            is_req_active=obj_notification_template.read(cr,uid,template_id[0],['is_req_active'])['is_req_active']
            res_data={}
            res_data['url']=""
            for var in liste_var:
                ####print liste_var
                ####print subject
                ####print body
                if var[0]=="[[url]]":
                    res_data['url'] = var[1]
                subject=subject.replace(var[0],var[1])
                body=body.replace(var[0],var[1])
                #print "subject ::::::   ", subject
                #print "body ::::::   ", body
            if user_ids:
                for user in user_obj.browse(cr, uid, user_ids):
                    mail = user_obj.read(cr, uid, user.id, ['user_email'])['user_email']
                    if is_req_active:
                        ###print "ENVOI REQ"
                        #dispatch_request(cr, uid, subject, body, uid, [user.id])
                        body_req = body.replace("<a target=\"_blank\" href=\"","").replace("\">Ouvrir la ressource</a>","")
                        dispatch_request(cr, uid, subject, body_req, uid, [user.id], res_data)
                    ###print user.user_email
                    if user.user_email and is_mail_active:
                        ###print "ENVOI MAIL"
                        dispatch_mail(self, cr, uid, subject, body, user.user_email)




    return True



