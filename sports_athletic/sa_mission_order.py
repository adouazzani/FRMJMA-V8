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

class mission_order(models.Model):
    _name = "sa.mission.order"

    name = fields.Char(string="N° demande", readonly=True)
    applicant = fields.Many2one("hr.employee", string="Demandeur", required=True)
    job = fields.Many2one(string="Poste", related="applicant.job_id", store=True)
    start_date = fields.Date(string="Date début", required=True)
    end_date = fields.Date(string="Date fin", required=True)
    start_hour = fields.Char(string="Heure de départ (HH:mm)")
    end_hour = fields.Char(string="Heure d'arrivée (HH:mm)")
    destination = fields.Char(string="Destination")
    accompanist = fields.Char(string="Accompagnateur de")
    means_of_transport = fields.Char(string="Moyen de transport")
    reason = fields.Text(string="Motif")
    state = fields.Selection([("draft", "Brouillon"), ("validate", "validé"),
                              ], string="Etat", default="draft")
    lang = fields.Selection(string='Language', selection='_get_lang')

    @api.model
    def _get_lang(self):
        langs = self.env['res.lang'].search([])
        return [(lang.code, lang.name) for lang in langs]

    @api.model
    def create(self, vals):
        vals["name"] = self.env["ir.sequence"].next_by_code("sa.mission.order")
        return super(mission_order, self).create(vals)

    @api.multi
    def action_validate(self):
        self.write({"state": "validate"})

    @api.multi
    def action_draft(self):
        self.write({"state": "draft"})

mission_order()