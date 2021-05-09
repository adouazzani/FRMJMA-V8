# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, tools, models, _

class Employee(models.Model):

    _inherit = 'hr.employee'

    cnss = fields.Char(string="numéro CNSS")
    mileage_allowance = fields.Many2one("mileage.allowance", "Indémnité")
    sa_expenses = fields.One2many("sa.expense", "applicant", string="Notes de Frais")
    city = fields.Char("Ville")
    address = fields.Text(string="Adresse")

Employee()

class ResPartnerBank(models.Model):

    _inherit = 'res.partner.bank'

    agency = fields.Char(string="Agence")

ResPartnerBank()

class HrContractType(models.Model):

    _inherit = 'hr.contract.type'

    note = fields.Char(string="Information")
    disposition_mise = fields.Char(string="Mise a la disposition")

HrContractType()

class HrContract(models.Model):

    _inherit = 'hr.contract'

    note = fields.Char(related="type_id.note", string="Information")

HrContractType()
