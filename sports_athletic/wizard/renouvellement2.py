# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp


class renouvellementcategory_age_change(models.TransientModel):
    _name = "sport.renouvellement.category_age_change"
    _description = "Renouvellement  category age change"

  
    

    image = fields.Binary("Nouvelle Photo", attachment=True)
    cinjuniorsseniors = fields.Binary('CIN pour les Séniors et Juniors')
    certificatmedical = fields.Binary('Cértificat Médical')
    cartesejour = fields.Binary('Carte Séjour')
    autorisationparents = fields.Binary('Autorisation des Parents')
    autorisationetrangere = fields.Binary('Autorisation étrangère')
    actenaissance = fields.Binary('Extrait d\'acte de Naissance')
    certificatscolarite = fields.Binary('Cértificat de Scolarité')
    attestationscolarite = fields.Binary('Attestation de Scolarité')
 

    @api.multi
    def create_reaffiliation(self):

        reaffiliation = self.env['sports.reaffiliation']
        athletes = self.env['sports.athletes']

        reaffiliation_id = self.env['sports.reaffiliation'].search([('responsable_id', '=', self.responsable_id.id),('state', '=', 'bord_attente_envoi')])

        if reaffiliation_id:
            a = reaffiliation_id
            print " reaffiliation :  "
	    print a
            b = reaffiliation_id.athletes3_ids
            print "============"
            print b
            reaffiliation_id.write({ 'athletes3_ids': [(6, 0, [x.id for x in self.licence_id])],})
        else:
            reaffiliation = reaffiliation.create({
            'name': self.env['ir.sequence'].next_by_code('sports.reaffiliation'),
            'club_id': self.club_id.id,
            'ligue_id': self.club_id.ligue_id.id,
            'athletes3_ids': [(6, 0, [x.id for x in self.licence_id])],
     	   })


        

   
