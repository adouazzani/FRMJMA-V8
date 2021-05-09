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


####Demande d'achat

class sa_expense(models.Model):
    _name = "sa.expense"

    name = fields.Char(string="N° Note de Frais", readonly=True)
    applicant = fields.Many2one("hr.employee", string="Demandeur", required=True)
    mileage_allowance = fields.Many2one(related="applicant.mileage_allowance", string="Indémnité")
    job = fields.Many2one(string="Poste", related="applicant.job_id", store=True)
    department = fields.Many2one(string="Département", related="applicant.department_id", store=True)
    start_date = fields.Date(string="Du", required=True)
    end_date = fields.Date(string="Au", required=True)
    amount_total_expense = fields.Float(string="Total Général de la Note de Frais", compute="_get_amount_total_expense")
    reason = fields.Text(string="Motif")
    state = fields.Selection([("draft", "Brouillon"), ("validate", "validé"),
                              ], string="Etat", default="draft")
    lang = fields.Selection(string='Language', selection='_get_lang')
    expense_line = fields.One2many("sa.expense.line", "expense", string="Ligne de note de frais")

    @api.model
    def _get_lang(self):
        langs = self.env['res.lang'].search([])
        return [(lang.code, lang.name) for lang in langs]

    @api.model
    def create(self, vals):
        vals["name"] = self.env["ir.sequence"].next_by_code("sa.expense")
        return super(sa_expense, self).create(vals)

    @api.multi
    def action_validate(self):
        self.write({"state": "validate"})

    @api.multi
    def action_draft(self):
        self.write({"state": "draft"})

    @api.one
    @api.depends('expense_line.amount_total')
    def _get_amount_total_expense(self):
        for line in self.expense_line:
            self.amount_total_expense += line.amount_total

sa_expense()

class sa_expense_line(models.Model):
    _name = "sa.expense.line"

    object = fields.Text('Objet', required=True)
    start_date = fields.Date(string="Date de départ", required=True)
    end_date = fields.Date(string="Date de retour", required=True)
    destination = fields.Char(string="Destination", required=True)
    means_of_transport = fields.Char(string="Moyen de transport")
    meal = fields.Float(string="Repas")
    traveled_km = fields.Float(string="KM Parcourus")
    mileage_allowance = fields.Float('Indémnité Kilométrique')
    ticket = fields.Float(string="Tickets")
    overnight = fields.Float(string="Nuitée")
    various = fields.Float(string="Divers")
    notes = fields.Char(string="Remarques")
    amount_total = fields.Float(string="Total", compute="_get_amount_total")
    expense = fields.Many2one("sa.expense", string="Note de frais")
    applicant = fields.Many2one(related="expense.applicant", string="Demandeur")
    mileage_allowance_applicant = fields.Many2one(related="applicant.mileage_allowance", string="Indémnité")

    @api.one
    @api.depends('meal', 'mileage_allowance', 'ticket', 'overnight', 'various')
    def _get_amount_total(self):
        self.amount_total = self.meal + self.mileage_allowance + self.ticket + self.overnight + self.various

    @api.onchange('traveled_km')
    def onchange_traveled_km(self):
        self.mileage_allowance = 0.0
        if self.mileage_allowance_applicant:
            self.mileage_allowance = self.traveled_km * self.mileage_allowance_applicant.price

sa_expense_line()

class mileage_allowance(models.Model):
    _name = "mileage.allowance"

    name = fields.Char(string="Puissance Fiscale du Véhicule", required=True)
    price = fields.Float(string="Indémnité Kilométrique en DH", required=True)

mileage_allowance()