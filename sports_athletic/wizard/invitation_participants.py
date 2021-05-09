# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp


class InvitationsParticipants(models.TransientModel):
    _name = "sport.invitation.participants"
    _description = "sport.invitation.participants"
    
    @api.model
    def _get_default_category_age_id(self):
        ###
        
        return self.epreuves_id.category_age_id.id


    @api.model
    def _get_default_sexe(self):
        ####
        return self.epreuves_id.sexe
        
        
    
    @api.model
    def _get_default_competition_id(self):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        return  docs.id 
        
        
    
    @api.onchange('epreuves_id')
    def _epreuves_id(self):
        
        for order in self:
            if self.epreuves_id:
                self.sexe = order.epreuves_id.sexe
                self.category_age_id = order.epreuves_id.category_age_id.id
                 
                
                
                    
        

    competition_id = fields.Many2one('sports.competition', string='Competition', default=_get_default_competition_id)
    club_id = fields.Many2one('sports.club', string='Club')
    league_id = fields.Many2one('sports.ligue', string='Ligue')
    epreuves_id = fields.Many2one('sports.epreuve.competition', string='Epreuves Competition' )
    athletes_competition_ids = fields.Many2many(comodel_name='sports.athletes',
                        relation='competition_athletes_rel',
                        column1='competition_id',
                        column2='athletes_id', string="Athletes")
                        
    sexe = fields.Selection([('h', 'Masculin'),('f', 'Féminin')], string='Sexe', default=_get_default_sexe)
    category_age_id = fields.Many2one('sports.category_age', string='Catégorie d’âge', default=_get_default_category_age_id)                    
    
  

    @api.multi
    def inviter_participants(self):

        participants = self.env['sports.competition.participants']
        
        for athletes in self.athletes_competition_ids:

            participants.create({
            
            'competition_id': self.competition_id.id,
            'athletes_id': athletes.id,
            'athletes_name': athletes.name,
            'athletes_prenom': athletes.prenom,
            'epreuve_id': self.epreuves_id.id,
            'club_id':self.club_id.id,
            'ligue_id':self.club_id.ligue_id.id,
            'name':self.epreuves_id.name,
            'sexe':self.sexe,
     
            
     	   })


        

   
