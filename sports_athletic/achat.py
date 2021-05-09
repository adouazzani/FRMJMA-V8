# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
import math
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, tools, models, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import ValidationError
from openerp.osv import osv

####Demande d'achat

class achat_demande(models.Model):
    _name = "achat.demande"

    name = fields.Char(string="N° demande", readonly=True)
    user_responsible = fields.Many2one('res.users', string="Responsable utilisateur", compute="_get_user_responsible", store=True)
    responsable_id = fields.Many2one("res.users", string="Service utilisateur", default=lambda self: self.env.user)
    date = fields.Date(string="Date", default=fields.Datetime.now)
    logistics_manager = fields.Many2one("hr.employee", string="Responsable Logistique", compute="_get_employee")
    frma_director = fields.Many2one("hr.employee", string="Directeur FRMA", compute="_get_employee")
    financial_director = fields.Many2one("hr.employee", string="Directeur Financier", compute="_get_employee")
    partner_id = fields.Many2one("res.partner", "Fournisseur")
    commentaires = fields.Text(string="Commentaires")
    budget = fields.Float(string="Montant budget")
    compte_charge = fields.Char(string="compte de charge")
    commentaires_ids = fields.One2many("achat.commentaires", "demande_id", string="Commentaires")
    demande_line_ids = fields.One2many("achat.demande.line", "demande_id", string="Ligne Demande d'achat")
    order_line = fields.One2many("purchase.order.line", "demande_id", "Ligne Demande d'achat")
    object = fields.Char(string="Objet de la demande d'achat", required=True)
    state = fields.Selection([("draft", "Brouillon"),
                              ("submitted_user", "Soumis Utilisateur"),
                              ("user_resp_validate", "Validé Resp Utilisateur"),
                              ("logistics_manager_validate", "Approuvé Resp Logistique"),
                              ("financial_director_validate", "Approuvé Dir Financier"),
                              ("frma_director_validate", "Approuvé Dir FRMA"),
                              ], string="Etat", default="draft")
    po_count = fields.Integer(string="Nombre BC", compute="_get_po_count")
    purchase_orders = fields.One2many("purchase.order", "demande_id", string="Bon de commande")
    purchase_requisitions = fields.One2many("purchase.requisition", "demande_id", string="Appel d'offre")
    history = fields.One2many("achat.demande.history", "demande_id", string="Historique des actions")
    pr_count = fields.Integer(string="Nombre BC", compute="_get_pr_count")
    lang = fields.Selection(string='Language', selection='_get_lang')
    date_submitted_user = fields.Date(string="Date soumission Utilisateur")
    date_user_resp_validate = fields.Date(string="Date validation Responsable utilisateur")
    date_logistics_manager_validate = fields.Date(string="Date approbation Responsable logistique")
    date_financial_director_validate = fields.Date(string="Date approbation Directeur financier")
    date_frma_director_validate = fields.Date(string="Date approbation Directeur FRMA")
    type = fields.Selection([("AO", "Appel d'offre"),
                             ("BC", "Bon de commande"),
                             ], string="Type demande d'achat", default="", compute="_get_type", store=True)
    is_write = fields.Boolean(string="Modifié", compute="_get_is_write", default=True)
    view_cancel = fields.Boolean(string="Afficher le bouton Annuler ?", compute="_get_view_cancel")

    @api.one
    @api.depends('state')
    def _get_view_cancel(self):
        for group in self.env.user.groups_id:
            if (group.name == "Responsable Logistique" and self.state == "user_resp_validate") or \
                    (group.name == "Directeur Financier" and self.state == "logistics_manager_validate") or \
                    (group.name == "Directeur FRMA" and self.state == "financial_director_validate"):
                self.view_cancel = True

    @api.one
    def _get_is_write(self):
        self.is_write = False
        for group in self.env.user.groups_id:
            if group.name in ('Directeur FRMA', 'Directeur Financier'):
                self.is_write = True
            if group.name == "Responsable Logistique" and self.state in ('', 'draft', 'submitted_user', 'user_resp_validate'):
                self.is_write = True
            if group.name in ("Demande d'achat / Utilisateur", "Demande d'achat / Responsable") and self.state in ('' ,'draft', 'submitted_user'):
                self.is_write = True

    @api.onchange("demande_line_ids")
    def onchange_demande_line(self):
        t = 0.0
        for line in self.demande_line_ids:
            t += line.price_subtotal
        self.budget = t

    @api.one
    @api.depends('budget')
    def _get_type(self):
        if self.budget == 0:
            self.type = ""
        else:
            if self.budget > 100000.0:
                self.type = "AO"
            else:
                self.type = "BC"

    @api.model
    def _get_lang(self):
        langs = self.env['res.lang'].search([])
        return [(lang.code, lang.name) for lang in langs]

    @api.one
    @api.depends('purchase_orders')
    def _get_po_count(self):
        lines = self.env['purchase.requisition'].search([('demande_id', '=', self.id), ('type', '=', 'BC')])
        self.po_count = len(lines)

    @api.one
    @api.depends('purchase_requisitions')
    def _get_pr_count(self):
        lines = self.env['purchase.requisition'].search([('demande_id', '=', self.id), ('type', '=', 'AO')])
        self.pr_count = len(lines)

    @api.one
    @api.depends('responsable_id')
    def _get_user_responsible(self):
        employee = self.env['hr.employee'].search([('user_id', '=', self._uid)])
        if employee:
            if employee.parent_id:
                if employee.parent_id.user_id:
                    self.user_responsible = employee.parent_id.user_id.id

    @api.one
    @api.depends('responsable_id')
    def _get_employee(self):
        posts = ["Directeur FRMA", "Directeur Financier", "Responsable Logistique"]
        for p in posts:
            post = self.sudo().env["hr.job"].search([("name", "=", p)])
            if post:
                employee = self.env["hr.employee"].search([("job_id", "=", post.id)])
                if employee:
                    if p == "Directeur FRMA":
                        self.frma_director = employee.id
                    if p == "Directeur Financier":
                        self.financial_director = employee.id
                    if p == "Responsable Logistique":
                        self.logistics_manager = employee.id

    @api.multi
    def action_cancel_request(self):
        if self.state == "user_resp_validate":
            self.send_mail([self.responsable_id, self.user_responsible], "Annulation de la demande d'achat " + self.name,
                           "La demande d'achat a été annulé par le responsable logistique " + (self.logistics_manager.name).encode(
                               'utf_8'), [])
            self.write({"state": "submitted_user"})
        if self.state == "logistics_manager_validate":
            self.send_mail([self.responsable_id, self.user_responsible],
                           "Annulation de la demande d'achat " + self.name,
                           "La demande d'achat a été annulé par le directeur financier " + ( self.financial_director.name).encode(
                               'utf_8'), [self.logistics_manager, self.financial_director])
            self.write({"state": "user_resp_validate"})
        if self.state == "financial_director_validate":
            self.send_mail([self.responsable_id, self.user_responsible],
                           "Annulation de la demande d'achat " + self.name,
                           "La demande d'achat a été annulé par le directeur FRMA " + ( self.frma_director.name).encode(
                               'utf_8'), [self.logistics_manager, self.financial_director, self.frma_director])
            self.write({"state": "logistics_manager_validate"})

    @api.multi
    def action_submitted_user(self):
        # self.send_mail([self.responsable_id, self.user_responsible], "Soumission de la demande d'achat "+self.name,
        #                "La demande d'achat a été soumis par l'utilisateur "+(self.responsable_id.name).encode('utf_8'), [])
        self.write({"state": "submitted_user"})
        self.date_submitted_user = fields.Datetime.now()

    @api.multi
    def action_user_resp_validate(self):
        # self.send_mail([self.responsable_id, self.user_responsible], "Validation de la demande d'achat " + self.name,
        #                "La demande d'achat a été validé par le responsable utilisateur " + (self.user_responsible.name).encode(
        #                   'utf_8'), [self.logistics_manager])
        self.write({"state": "user_resp_validate"})
        self.date_user_resp_validate = fields.Datetime.now()

    @api.multi
    def action_logistics_manager_validate(self):
        # self.send_mail([self.responsable_id, self.user_responsible], "Validation de la demande d'achat " + self.name,
        #                "La demande d'achat a été approuvé par le responsable logistique " + (self.logistics_manager.name).encode(
        #                    'utf_8'), [self.logistics_manager, self.financial_director])
        self.write({"state": "logistics_manager_validate"})
        self.date_logistics_manager_validate = fields.Datetime.now()

    @api.multi
    def action_financial_director_validate(self):
        # self.send_mail([self.responsable_id, self.user_responsible], "Approbation de la demande d'achat " + self.name,
        #                "La demande d'achat a été approuvé par le directeur financier " + (self.financial_director.name).encode(
        #                    'utf_8'), [self.logistics_manager, self.financial_director, self.frma_director])
        self.write({"state": "financial_director_validate"})
        self.date_financial_director_validate = fields.Datetime.now()

    @api.multi
    def action_frma_director_validate(self):
        # self.send_mail([self.responsable_id, self.user_responsible], "Approbation de la demande d'achat " + self.name,
        #                "La demande d'achat a été approuvé par le directeur FRMA " + (self.frma_director.name).encode(
        #                    'utf_8'), [self.logistics_manager, self.financial_director, self.frma_director])
        purchase_team = []
        group = self.env['res.groups'].search([('name', '=', 'Equipe achat')])
        if group:
            for user in group.users:
                employee = self.env['hr.employee'].search([('user_id', '=', user.id)])
                if employee:
                    purchase_team.append(employee)
        if purchase_team:
            self.send_mail([],
                           "Approbation de la demande d'achat " + self.name,
                           "La demande d'achat a été approuvé par le directeur FRMA " + (
                               self.frma_director.name).encode(
                               'utf_8'), purchase_team)
        self.write({"state": "frma_director_validate"})
        self.date_frma_director_validate = fields.Datetime.now()

    @api.model
    def create(self, vals):
        vals["name"] = self.env["ir.sequence"].next_by_code("achat.demande")
        result = super(achat_demande, self).create(vals)
        try:
            self.env['achat.demande.history'].create({
                'name': "Création de la demande d'achat "+str(vals['name']),
                'operation': "Création",
                'demande_id': result.id,
            })
        except:
            print "error"
        return result

    @api.multi
    def write(self, vals):
        if 'object' in vals:
            try:
                self.env['achat.demande.history'].create({
                    'name': "Modification de l'objet de la demande d'achat",
                    'operation': "Modification",
                    'demande_id': self.id,
                    'old_value': self.object,
                    'new_value': vals['object'],
                })
            except:
                print "error"
        if 'date' in vals:
            try:
                self.env['achat.demande.history'].create({
                    'name': "Modification de la date de la demande d'achat",
                    'operation': "Modification",
                    'demande_id': self.id,
                    'old_value': datetime.strptime(self.date, '%Y-%m-%d').strftime("%d/%m/%Y"),
                    'new_value': datetime.strptime(vals['date'], '%Y-%m-%d').strftime("%d/%m/%Y"),
                })
            except:
                print "error"
        return super(achat_demande, self).write(vals)

    @api.multi
    def send_mail(self, users, msg_subject, msg_body, employees):
        emailfrom = "noreply.odoo@frma.ma"
        # send mail
        IrMailServer = self.env['ir.mail_server']
        # data
        recipients_email = []
        email_from = [emailfrom]
        for user in users:
            employee = self.env['hr.employee'].search([('user_id', '=', user.id)])
            if employee and employee.work_email:
                recipients_email.append(employee.work_email)
        for emp in employees:
            if emp.work_email:
                recipients_email.append(emp.work_email)
        email_to = recipients_email
        subject = msg_subject
        body = msg_body
        body += "<br/><br/>" \
                "<strong>Réference système demande d'achat : "+(self.name).encode('utf_8')+"</strong><br/>" \
                                                                                           "<strong>Objet demande d'achat : "+(self.object).encode('utf_8')+"</strong><br/>" \
                                                                                                                                                            "Veuillez cliquer sur le boutton suivant pour accéder directement a la demande d'achat : <a href=http://196.217.244.225:8069/web#id="+str(self.id)+"&view_type=form&model=achat.demande&menu_id=505&action=480>Lien vers la demande d'achat</a>"
        body += "<br/><br/>" \
                "Ce mail a été envoyé par ODOO-FRMA"
        subtype = "html"
        if recipients_email:
            emailto = ""
            i = 1
            for mail in email_to:
                try:
                    emailto += mail
                except:
                    print "error"
                if len(email_to) != i:
                    emailto += ","
                i += 1

            mail_values = {
                'email_from': emailfrom,
                'reply_to': emailfrom,
                'email_to': emailto,
                'subject': subject,
                'body_html': body,
                'notification': True,
                # 'mailing_id': mailing.id,
                # 'attachment_ids': attachments,
            }
            msg = IrMailServer.build_email(
                email_from=email_from,
                email_to=email_to,
                subject=subject,
                body=body,
                subtype=subtype,
                # body_alternative=email.get('body_alternative'),
                # email_cc="odoo_for@gmail.com",
                # reply_to="odoo_replay_for@gmail.com",
                #attachments=attachments,
                # message_id=mail.message_id,
                # references=mail.references,
                # object_id=mail.res_id and ('%s-%s' % (mail.res_id, mail.model)),
                # subtype_alternative='plain',
                # headers=headers
            )
            # send mail
            try:
                #res = IrMailServer.send_email(msg, mail_server_id=1)
                print "Mail sent"
            except:
                print "error"
        return True

achat_demande()

class achat_demande_line(models.Model):
    _name = "achat.demande.line"

    product = fields.Many2one("product.product", string="Article", required=True)
    description = fields.Text(string="Description", required=True)
    product_qty = fields.Float(string="Quantité", required=True)
    product_uom = fields.Many2one("product.uom", string="Unité de mesure", required=True)
    price_unit = fields.Float(string="Prix unitaire", required=True)
    price_subtotal = fields.Float(string="Sous-total", compute="_get_price_subtotal")
    demande_id = fields.Many2one("achat.demande", string="Demande d'achat")
    date_planned = fields.Date(string="Date demandée", default=fields.Datetime.now)

    # @api.onchange('demande_id.date')
    # def onchange_date_da(self):
    #     if self.demande_id.date:
    #         self.date_planned = self.demande_id.date

    @api.multi
    def write(self, vals):
        if 'product' in vals:
            product = self.env['product.product'].search([('id', '=', vals['product'])])
            try:
                self.env['achat.demande.history'].create({
                    'name': "Modification du nom de produit",
                    'operation': "Modification",
                    'demande_id': self.demande_id.id,
                    'old_value': self.product.name,
                    'new_value': product.name,
                })
            except:
                print "error"
        if 'product_qty' in vals:
            try:
                self.env['achat.demande.history'].create({
                    'name': "Modification de la Qté du produit "+(self.product.name).encode('utf_8'),
                    'operation': "Modification",
                    'demande_id': self.demande_id.id,
                    'old_value': self.product_qty,
                    'new_value': vals['product_qty'],
                })
            except:
                print "error"
        if 'price_unit' in vals:
            try:
                self.env['achat.demande.history'].create({
                    'name': "Modification du PU du produit "+(self.product.name).encode('utf_8'),
                    'operation': "Modification",
                    'demande_id': self.demande_id.id,
                    'old_value': self.price_unit,
                    'new_value': vals['price_unit'],
                })
            except:
                print "error"
        if 'product_uom' in vals:
            product_uom = self.env['product.uom'].search([('id', '=', vals['product_uom'])])
            try:
                self.env['achat.demande.history'].create({
                    'name': "Modification de l'unité de mesure du produit "+(self.product.name).encode('utf_8'),
                    'operation': "Modification",
                    'demande_id': self.demande_id.id,
                    'old_value': self.product_uom.name,
                    'new_value': product_uom.name,
                })
            except:
                print "error"
        return super(achat_demande_line, self).write(vals)

    @api.onchange('product')
    def onchange_product(self):
        self.product_uom = self.product.uom_po_id
        if self.demande_id.date:
            self.date_planned = self.demande_id.date

    @api.one
    @api.depends('product_qty', 'price_unit')
    def _get_price_subtotal(self):
        self.price_subtotal = self.product_qty * self.price_unit

achat_demande_line()

class purchase_order_line(models.Model):
    _inherit = "purchase.order.line"

    demande_id = fields.Many2one("achat.demande", string="Demande d'achat")
    order_id = fields.Many2one("purchase.order", string="Bon de commande Achat", required=False)
    name = fields.Text(string='Description', required=True)
    supply = fields.Char(string="Fourniture")
    renting = fields.Char(string="Location")
    pose = fields.Char(string="Pose")
    depose = fields.Char(string="Depose")
    display_slip = fields.Boolean(related="order_id.display_slip", string="Afficher colonnes BP", store=True)

purchase_order_line()

class purchase_order(models.Model):
    _inherit = "purchase.order"

    demande_id = fields.Many2one("achat.demande", string="Demande d'achat")
    object = fields.Char(string="Objet de la demande d'achat", related="demande_id.object")
    display_slip = fields.Boolean(string="Afficher colonnes BP")

    def _choose_account_from_po_line(self, cr, uid, po_line, context=None):
        fiscal_obj = self.pool.get('account.fiscal.position')
        property_obj = self.pool.get('ir.property')
        acc_id = False
        if po_line.order_id.origin:
            pr_id = self.pool.get('purchase.requisition').search(cr, uid, [('name', '=', po_line.order_id.origin)],
                                                                 context=context)
            if pr_id:
                pr = self.pool.get('purchase.requisition').browse(cr, uid, pr_id, context=context)[0]
                if pr.demande_id:
                    if pr.demande_id.compte_charge:
                        account_id = self.pool.get('account.account').search(cr, uid, [
                            ('code', '=', pr.demande_id.compte_charge)], context=context)[0]
                        if account_id:
                            acc_id = account_id
        if not acc_id:
            if po_line.product_id:
                acc_id = po_line.product_id.property_account_expense.id
                if not acc_id:
                    acc_id = po_line.product_id.categ_id.property_account_expense_categ.id
                if not acc_id:
                    raise osv.except_osv(_('Error!'), _('Define an expense account for this product: "%s" (id:%d).') % (
                        po_line.product_id.name, po_line.product_id.id,))
            else:
                acc_id = property_obj.get(cr, uid, 'property_account_expense_categ', 'product.category',
                                          context=context).id
        fpos = po_line.order_id.fiscal_position or False
        return fiscal_obj.map_account(cr, uid, fpos, acc_id)

    @api.onchange('demande_id')
    def onchange_demande_achat(self):
        lines = []
        if self.demande_id:
            for line in self.demande_id.demande_line_ids:
                lines.append({
                    #'name': line.product.name_template,
                    'name': line.description,
                    'product_id': line.product.id,
                    'product_qty': line.product_qty,
                    'price_unit': line.price_unit,
                    'product_uom': line.product_uom.id,
                    'date_planned': line.date_planned,
                })
        self.order_line = lines

    @api.multi
    def action_print_purchase_quotation(self):
        try:
            return self.pool['report'].get_action(self._cr, self._uid, self.id,
                                                  'purchase.report_purchasequotation',
                                                  context=self._context)
        except:
            print "error printing"
        return True

    @api.multi
    def action_print_purchase_order(self):
        try:
            return self.pool['report'].get_action(self._cr, self._uid, self.id,
                                                  'purchase.report_purchaseorder',
                                                  context=self._context)
        except:
            print "error printing"
        return True

    @api.multi
    def open_purchase_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Demande de prix',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'target': 'current',
        }

purchase_order()

class purchase_requisition(models.Model):
    _inherit = "purchase.requisition"

    demande_id = fields.Many2one("achat.demande", string="Demande d'achat")
    object = fields.Char(string="Objet de la demande d'achat", related="demande_id.object", store=True)
    type = fields.Selection(string="Type demande d'achat", related="demande_id.type", store=True)
    date_end2 = fields.Datetime(string="Deuxième Date limite de soumission des offres")
    date_end3 = fields.Datetime(string="Troisième Date limite de soumission des offres")

    @api.onchange('demande_id')
    def onchange_demande_achat_req(self):
        lines = []
        if self.demande_id:
            for line in self.demande_id.demande_line_ids:
                lines.append({
                    #'name': line.product.name_template,
                    'product_id': line.product.id,
                    'name': line.description,
                    'product_qty': line.product_qty,
                    #'price_unit': line.price_unit,
                    'product_uom_id': line.product_uom.id,
                    'schedule_date': line.date_planned,
                })
        self.line_ids = lines
        if self.demande_id.type:
            if self.demande_id.type == "AO":
                self.name = "AO/"+self.name
            else:
                self.name = "D/" + self.name

purchase_requisition()

class purchase_requisition_line(models.Model):
    _inherit = "purchase.requisition.line"

    name = fields.Text(string="Description")

purchase_requisition_line()


class achat_commentaires(models.Model):
    _name = "achat.commentaires"

    name = fields.Text(string="Commentaire")
    date = fields.Datetime(string="Date", default=lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"))
    responsable_id = fields.Many2one("res.users", string="Demandeur", default=lambda self: self.env.user)
    demande_id = fields.Many2one("achat.demande", string="Demande d'achat")

achat_commentaires()

class achat_demande_history(models.Model):
    _name = "achat.demande.history"
    _order = "date desc"

    name = fields.Char(string="Action")
    date = fields.Datetime(string="Date", default=lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"))
    user = fields.Many2one("res.users", string="Utilisateur", default=lambda self: self.env.user)
    operation = fields.Char(string="Opération")
    old_value = fields.Char(string="Ancienne valeur")
    new_value = fields.Char(string="Nouvelle valeur")
    demande_id = fields.Many2one("achat.demande", string="Demande d'achat")

achat_demande_history()

class purchase_requisition_partner(models.Model):
    _inherit = "purchase.requisition.partner"

    partner_id = fields.Many2one("res.partner", string="Founisseur", domain=[('supplier', '=', True)], required=False)
    multiple_supplier = fields.Boolean(string="Créer DP pour plusieurs fournisseurs")
    partners = fields.One2many("res.partner", "requisition_partner_id", string="Fournisseurs", domain=[('supplier', '=', True)])

    def create_order(self, cr, uid, ids, context=None):
        active_ids = context and context.get('active_ids', [])
        data = self.browse(cr, uid, ids, context=context)[0]
        for partner in data.partners:
            self.pool.get('purchase.requisition').make_purchase_order(cr, uid, active_ids, partner.id,
                                                                      context=context)
        # if data.multiple_supplier:
        #     for partner in data.partners:
        #         self.pool.get('purchase.requisition').make_purchase_order(cr, uid, active_ids, partner.id,
        #                                                                   context=context)
        # else:
        #     self.pool.get('purchase.requisition').make_purchase_order(cr, uid, active_ids, data.partner_id.id,
        #                                                               context=context)
        return {'type': 'ir.actions.act_window_close'}

purchase_requisition_partner()


class ResPartner(models.Model):

    _inherit = 'res.partner'

    requisition_partner_id = fields.Many2one("purchase.requisition.partner", string="Demande appel d'offre")

    @api.multi
    def name_get(self):
        res = []
        name = ""
        for record in self:
            if record.supplier:
                if record.ref:
                    name = record.ref+" "
            if record.name:
                name += record.name
            res.append((record.id, name))
        return res

ResPartner()