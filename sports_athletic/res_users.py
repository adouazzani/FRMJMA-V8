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


#### Utilisateur

class ResUsers(models.Model):
    _inherit = "res.users"


    ligue_id = fields.Many2one('sports.ligue', string='Ligue')
    club_id = fields.Many2one('sports.club', string='Club')

    metie = fields.Selection([
        ('Ligue', 'Ligue'),
        ('Club', 'Club'),
        ('Relation', 'Relation'),
        ('commission', 'Commission'),
        ('Centre', 'Centre'),

        ('Centre_depart', 'Centre Départ'),
        ('Centre_acceuil', 'Centre Acceuil'),
        ('directeur_technique', 'Directeur technique'),
        ('service_financier', 'Service Financier'),
        ('direction_organisation', 'Direction Organisation'),
        ('Administrateur', 'Administrateur'),

        ], string='Metier')

    ligue_un = fields.Boolean(string='Est une Ligue')  
    centre_id = fields.Many2one('sports.centres', string='centre')
