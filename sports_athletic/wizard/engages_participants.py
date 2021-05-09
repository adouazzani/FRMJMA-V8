# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp


class EngagesParticipants(models.TransientModel):
    _name = "sport.engages.participants"
    _description = "sport.engages.participants"
    
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
               
        

    competition_id = fields.Many2one('sports.competition', string='Competition', default=_get_default_competition_id)

    participants_competition_ids = fields.Many2many(comodel_name='sports.competition.participants',
                        relation='competition_participants_rel',
                        column1='competition_id',
                        column2='participants_id', string="Participants")

  

    @api.multi
    def engages_participants(self):

       
        
        for competition in self.participants_competition_ids:

            competition.write({
            
            'competition_rel_id': self.competition_id.id,
            'engage':True,

     
            
     	   })


        

   
