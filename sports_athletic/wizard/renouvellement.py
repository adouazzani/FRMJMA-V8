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

from openerp import api, fields, models

class sport_renouvellement_category_age_change(models.TransientModel):
    _name = "sport.renouvellement.category_age_change"
    _description = "Renouvellement category age change"

    image = fields.Binary('Nouvelle Photo')
    cinjuniorsseniors = fields.Binary('CIN pour les Séniors et Juniors')
    certificatmedical = fields.Binary('Cértificat Médical')
    cartesejour = fields.Binary('Carte Séjour')
    autorisationparents = fields.Binary('Autorisation des Parents')
    autorisationetrangere = fields.Binary('Autorisation étrangère')
    certificatscolarite = fields.Binary('Cértificat de Scolarité')
    attestationscolarite = fields.Binary('Attestation de Scolarité')
    actenaissance = fields.Binary('Extrait d\'acte de Naissance')
    cin = fields.Char('CIN')


    @api.multi
    def make_renouvellement(self):
        print self._context
        if 'active_id' in self._context:
            athlete = self.env['sports.athletes'].search([('id', '=', self._context['active_id'])])
            if athlete:
                if self.cin:
                    athlete.cin = self.cin
                if self.cinjuniorsseniors:
                    athlete.cinjuniorsseniors = self.cinjuniorsseniors
                if self.certificatmedical:
                    athlete.certificatmedical = self.certificatmedical
                if self.cartesejour:
                    athlete.cartesejour = self.cartesejour
                if self.autorisationparents:
                    athlete.autorisationparents = self.autorisationparents
                if self.autorisationetrangere:
                    athlete.autorisationetrangere = self.autorisationetrangere
                if self.certificatscolarite:
                    athlete.certificatscolarite = self.certificatscolarite
                if self.attestationscolarite:
                    athlete.attestationscolarite = self.attestationscolarite
                if self.actenaissance:
                    athlete.actenaissance = self.actenaissance
        # order_obj = self.pool.get('sports.athletes')
        # if context is None:
        #     context = {}
        # athletes_obj = self.pool.get('sports.athletes')
        # wizard = self.browse(cr, uid, ids[0], context)
        # athletes_ids = context.get('active_ids', [])
        #
        # result = []
        # for athletes in athletes_obj.browse(cr, uid, athletes_ids, context=context):
        #
        #     val = athletes_obj.renouvellement_id_change(cr, uid,athletes.id,wizard.image,wizard.cinjuniorsseniors,wizard.certificatmedical,wizard.cartesejour,wizard.autorisationparents,wizard.autorisationetrangere,wizard.certificatscolarite,wizard.attestationscolarite,wizard.actenaissance,wizard.cin)
        #
        # return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
