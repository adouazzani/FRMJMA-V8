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




####Catégories d'âges / Sexe


class SportsCategory_age_Sexe(models.Model):
    _name = "sports.category_age.sexe"

    name = fields.Char(string='Désignation')
    category_age_id = fields.Many2one('sports.category_age', string='Catégories')
    sexe = fields.Selection([('h', 'Masculin'), ('f', 'Féminin')], string='Sexe')




#### Epreuve


class sport_epreuve_familles(models.Model):
    _name = "sports.epreuve.familles"

    name = fields.Char(string='Nom')
    um = fields.Selection([ ('Temps', 'Temps'),('Metre', 'Métre')], string='Unité de mesure')
    

class sport_epreuve_formatresultat(models.Model):
    _name = "sports.epreuve.formatresultat"

    name = fields.Char(string='Nom')    





class sport_epreuve(models.Model):
    _name = "sports.epreuve"

    @api.onchange('familles_id')
    def onchange_familles(self):
        self.um = self.familles_id.um
        
    name = fields.Char(string='Code épreuve')
    libelle_court = fields.Char(string='Libellé Court')
    libelle_complet = fields.Char(string='Libellé Complet')
    familles_id = fields.Many2one('sports.epreuve.familles', string='Famille')
    formatresultat_id = fields.Many2one('sports.epreuve.formatresultat', string='Format résultat')
    
    
   
    
    
    ordre_tri = fields.Selection([ ('Croissant', 'Croissant'),('Decroissant', 'Décroissant')], string='Ordre de Tri des résultats')

    category_age_id = fields.Many2many('sports.category_age.sexe', string='Catégorie d\'âges')
    
    nbr_participants = fields.Integer(string='Nombre de Participants')
    participants_seuil = fields.Boolean('Seuil de Participants ?')
    
    obligation_minimas = fields.Boolean('Obligation de réaliser le Minimas?')
    performance = fields.Text(string='Performance')
    
    um = fields.Selection([ ('Temps', 'Temps'),('Metre', 'Métre')], string='Unité de mesure')
    heure =  fields.Integer('Heures')
    minute =  fields.Integer('Minutes')
    seconde = fields.Integer('Secondes')
    milliseconde =  fields.Integer('1/10')
    centseconde =  fields.Integer('1/100')
    point = fields.Integer('Points')
    
    
    centimetre = fields.Integer('Centimètres')
    metre = fields.Integer('Mètres')
    kilometre = fields.Integer('Kilomètres')
    
    is_kilometre = fields.Boolean('Kilomètre')
    is_metre = fields.Boolean('Mètre')
    is_centimetre =  fields.Boolean('Centimètre')
    
    
    is_heure =  fields.Boolean('Heures')
    is_minute = fields.Boolean('Minutes')
    is_seconde = fields.Boolean('Secondes')
    is_milliseconde =  fields.Boolean('1/10')
    is_centseconde =  fields.Boolean('1/100')
    
    performance_temps =  fields.Integer('Performance Temps')
    performance_distance = fields.Integer('Performance Distance')
    performance = fields.Char('Performance', size=256, select=True)
    is_point = fields.Boolean('point')

    
    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].next_by_code('sports.epreuve')
        result = super(sport_epreuve, self).create(vals)
        return result
    

#######Calendriers


    
 
#### Compétitions



class sport_competition_familles(models.Model):
    _name = "sports.competition.familles"

    name = fields.Selection([ ('Meetings Regionaux', 'Meetings Régionaux'),('Meetings Nationaux', 'Meetings Nationaux'),('Circuit Federal', 'Circuit Fédéral'),('Championnat National', 'Championnat National'),('Les coupes', 'Les coupes'),('Competitions Internationales', 'Compétitions Internationales'),('Cross Regionaux', 'Cross Régionaux'),('Cross de zone', 'Cross de zone'),('Championnat National', 'Championnat National'),('Cross Circuit Federal', 'Cross Circuit Fédéral'),('Competitions Internationales', 'Compétitions Internationales'),('Les coupes', 'Les coupes'),('Course sur Route', 'Course sur Route'),(' 	Competitions Internationales', 'Compétitions Internationales')], string='Famille')
    
    type = fields.Selection([ ('Athletisme', 'Athlétisme'),('Cross country', 'Cross country'),('Course sur route', 'Course sur route')], string='Type')
    
   

class sport_competition_formatresultat(models.Model):
    _name = "sports.competition.prise_compte"

    name = fields.Char(string='Nom')     
    
    

class sport_competition(models.Model):
    _name = "sports.competition" 
    
    @api.model
    def _get_default_saison(self):

        return self.env['sports.saison'].search([('state', '=', 'active')])
    
    name = fields.Char(string='Num Compétition')
    name_competition = fields.Char(string='Nom')
    saison_id = fields.Many2one('sports.saison', string='Saison sportive', default=_get_default_saison)
    date_debut = fields.Date(string='Date Début')
    date_fin = fields.Date(string='Date Fin')
    organisateur = fields.Selection([ ('Club', 'Club'),('Ligue', 'Ligue'),('IAAF', 'IAAF'),('FRMA', 'FRMA'),('Autre', 'Autre')], string='Organisateur')
    
    calendar_id = fields.Many2one('athletic.athlete.wkf.annual.calendar', string='Calendrier', track_visibility='onchange')
    

    club_id = fields.Many2one('sports.club', string='Club', track_visibility='onchange')
    ligue_id = fields.Many2one('sports.ligue', string='Ligue', track_visibility='onchange')
    autre_organisateur = fields.Char(string='Autre Organisateur')
    
    type = fields.Selection([ ('Athletisme', 'Athlétisme'),('Cross country', 'Cross country'),('Course sur route', 'Course sur route')], string='Type')
    
    niveau = fields.Selection([ ('Internationale', 'Internationale'),('Nationale', 'Nationale'),('Federale', 'Fédérale'),('Zone', 'Zone'),('Regionale', 'Régionale'),('Locale', 'Locale')], string='Niveau')
    
    lieu = fields.Char(string='Lieu')
    
    respect_cahier_charge = fields.Selection([ ('Oui', 'Oui'),('Non', 'Non')], string='Respect du cahier de charge')
    
    
   
    
    timing = fields.Selection([ ('manuel', 'Manuel'),('electrique', 'Electrique')], string='Chronomètre')
    
    familles_id = fields.Many2one('sports.competition.familles', string='Famille', track_visibility='onchange')
   
    prise_compte_frma_ids = fields.Many2many(comodel_name='sports.competition.prise_compte',
                        relation='competition_prise_compte_rel',
                        column1='competition_id',
                        column2='prise_compte_id', string="Prises en compte par la FRMA")
    
    
    participation_competition = fields.Selection([ ('Ouverte', 'Ouverte'),('Sur Invitation', 'Sur Invitation'),('Sur Qualification', 'Sur Qualification')], string='Participation à la Compétition')
    
    critere_invitation_qualification = fields.Selection([ ('Personnalise', 'Personnalisé'),('Championnat national et circuit federal', 'Championnat national et circuit fédéral — Athlétisme'),('Coupe de trone', 'Coupe de trône — Athlétisme'),('Coupe des jeunes', 'Coupe des jeunes — Athlétisme'),('Championnat national', 'Championnat national — Cross'),('Competitions Internationales', 'Compétitions Internationales — Athlétisme'),('Meetings Regionaux', ' Meetings Régionaux — Athlétisme'),('Meetings Nationaux', 'Meetings Nationaux — Athlétisme')], string='Critère Qualification/Invitation')
    
    
    
    
    state = fields.Selection([ ('brouillon','Brouillon'),('en_att_valid','En Attente de Validation'),('en_att_org','En Attente d\'organisation'),('att_val_pre_eng','En Attente de Pré-engagements'),('att_val_eng','En Attente de Validation des Engagements'),('att_conf_eng','En Attente de Confirmation des Engagements'),('liste_eng_conf','Engagements Confirmée'),('calcul_pt_club','Points Calculés'), ('dem_rejetee','''Demande Rejetée''')], string='Statut', readonly=True, default="brouillon")
    
    
    
    
    objectif = fields.Char(string='Objectif')
    
    epreuves_disputees = fields.Selection([ ('categories_age', 'Catégories d’âge'),('tous', 'Toutes catégories confondues')], string='Epreuves Disputées Par')
   
    category_age_ids = fields.Many2many('sports.category_age.sexe', string='Catégorie d\'âges')
    
    epreuve_ids = fields.Many2many('sports.epreuve', string='Epreuves')
    
    epreuve_competition_ids = fields.One2many('sports.epreuve.competition', 'competition_id', 'Epreuves Competition')
    
    participants_ids = fields.One2many('sports.competition.participants', 'competition_id', 'Participants')
    
    engagement_ids = fields.One2many('sports.competition.participants', 'competition_rel_id', 'Liste des Engagements')
    
    feuille_comp_ids = fields.One2many('sports.competition.participants', 'competition_rel_id', 'Liste des Engagements', domain=[('engage','=',True)])
    
    
    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].next_by_code('sports.competition')
        result = super(sport_competition, self).create(vals)
        return result


    @api.multi
    def generer_epreuve(self):
    
        for order in self:
	    
		if not order.epreuve_competition_ids:
		
		   if order.epreuves_disputees == "tous":
		      print " tous"
		      for epreuve in order.epreuve_ids:
		      
		          for category_age in epreuve.category_age_id:
		              print " Je suis ICI 1"
		              order.env['sports.epreuve.competition'].create({'name': epreuve.libelle_court +category_age.name , 'libelle_court': epreuve.libelle_court,'formatresultat_id': epreuve.formatresultat_id.id,'sexe': category_age.sexe ,'category_age_id': category_age.category_age_id.id,'epreuve_id ':epreuve.id, 'ordre_tri': epreuve.ordre_tri,'competition_id':order.id,'chronometre':order.timing, 'um':epreuve.um, 'is_metre':epreuve.is_metre, 'is_kilometre':epreuve.is_kilometre,'is_centimetre':epreuve.is_centimetre,'is_heure':epreuve.is_heure,'is_minute':epreuve.is_minute, 'is_seconde':epreuve.is_seconde,'is_milliseconde':epreuve.is_milliseconde,'is_centseconde':epreuve.is_centseconde})
		   
		       
		       
		   elif self.epreuves_disputees == "categories_age":
		   
		        
		        for epreuve in self.epreuve_ids:
		          for competition_age  in  order.category_age_ids:
		              i = 0
		              for category_age in epreuve.category_age_id:
		                  if category_age.id == competition_age.id:
		                         i = 1 + i 
		              if i > 0: 
		                 print " Je suis ICI 2"
		                 
		                 order.env['sports.epreuve.competition'].create( {'name': epreuve.libelle_court +category_age.name, 'libelle_court': epreuve.libelle_court,'formatresultat_id': epreuve.formatresultat_id.id,'sexe': competition_age.sexe ,'epreuve_id ':epreuve.id, 'ordre_tri': epreuve.ordre_tri,'competition_id':order.id,'category_age_id': competition_age.category_age_id.id,'chronometre':order.timing, 'um':epreuve.um, 'is_metre':epreuve.is_metre, 'is_kilometre':epreuve.is_kilometre,'is_centimetre':epreuve.is_centimetre,'is_heure':epreuve.is_heure,'is_minute':epreuve.is_minute, 'is_seconde':epreuve.is_seconde,'is_milliseconde':epreuve.is_milliseconde,'is_centseconde':epreuve.is_centseconde}) 
		                
        return True           
                                  
                      
                      
                      
                  
                  
                  
                      
        
        
        



#####  Epreuve competition 

class sport_epreuve_competition(models.Model):
    _name = "sports.epreuve.competition"

    name = fields.Char(string='Code épreuve')
    libelle_court = fields.Char(string='Epreuve')
    formatresultat_id = fields.Many2one('sports.epreuve.formatresultat', string='Format résultat')
   
    category_age_id = fields.Many2one('sports.category_age', string='Catégorie d\'âges')
    sexe = fields.Selection([ ('h', 'Masculin'),('f', 'Féminin')], string='Sexe')
    
    date = fields.Datetime(string='Date et heurs')
    
    epreuve_id = fields.Many2one('sports.epreuve', string='Origine')
    
    disputee = fields.Boolean('Disputée?')
    competition_id = fields.Many2one('sports.competition', string='Competition')
    
    chronometre = fields.Selection([ ('manuel', 'Manuel'),('electrique', 'Electrique')], string='Chronomètre')
    vent = fields.Selection([ ('regulier', 'Régulier'),('tout_vent', 'Tout Vent')], string='Vent')
    
    ordre_tri = fields.Selection([ ('Croissant', 'Croissant'),('Decroissant', 'Décroissant')], string='Ordre de Tri des résultats')
    
    um = fields.Selection([ ('Temps', 'Temps'),('Metre', 'Métre')], string='Unité de mesure')
    
    
    
    centimetre = fields.Integer('Centimètres')
    metre = fields.Integer('Mètres')
    kilometre = fields.Integer('Kilomètres')
    
    is_kilometre = fields.Boolean('Kilomètre')
    is_metre = fields.Boolean('Mètre')
    is_centimetre =  fields.Boolean('Centimètre')
    
    
    is_heure =  fields.Boolean('Heures')
    is_minute = fields.Boolean('Minutes')
    is_seconde = fields.Boolean('Secondes')
    is_milliseconde =  fields.Boolean('1/10')
    is_centseconde =  fields.Boolean('1/100')
    
    heure =  fields.Integer('Heures')
    minute =  fields.Integer('Minutes')
    seconde = fields.Integer('Secondes')
    milliseconde =  fields.Integer('1/10')
    centseconde =  fields.Integer('1/100')
    
    



#####  Participants
class sport_competition_participants(models.Model):
    _name = "sports.competition.participants"



    competition_id = fields.Many2one('sports.competition', string='Compétition')
    competition_rel_id = fields.Many2one('sports.competition', string='Compétition')
    athletes_id = fields.Many2one('sports.athletes', string='Num Licence')
    athletes_name = fields.Char(string='Nom ')
    athletes_prenom = fields.Char(string='Prénom')
    
    
    epreuve_id = fields.Many2one('sports.epreuve.competition', string='Epreuve')
    formatresultat_id = fields.Many2one('sports.epreuve.formatresultat', string='Format résultat')
    
    format_resultat = fields.Char(string='Format résultat',related='formatresultat_id.name', store=True)
    
    
    club_id = fields.Many2one('sports.club', string='Club', track_visibility='onchange')
    ligue_id = fields.Many2one('sports.ligue', string='Ligue', track_visibility='onchange')
    engage = fields.Boolean('Engagé?')
    confirmation_engage = fields.Boolean('Confirmation Engagement?')
    
    pointage = fields.Selection([ ('none', ''), ('oui', 'Oui'),('non','Non')], string='Pointage Chambre d\'appel', default='non')
    point = fields.Integer('Points')
    heure = fields.Integer(string='Heures')
    minute = fields.Integer(string='Minutes')
    seconde = fields.Integer(string='Seconde')
    milliseconde = fields.Integer(string='Milliseconde')
    
    centimetre = fields.Integer(string='Centimètres')
    metre = fields.Integer(string='Mètres')
    kilometre = fields.Integer(string='Kilomètres')
    
    name = fields.Char(string='Code épreuve')
   
    sexe = fields.Selection([ ('h', 'Masculin'),('f', 'Féminin')], string='Sexe')
    serie = fields.Selection([ ('s1', 'Série 1'), ('s2', 'Série 2'),('s3','Série 3')], string='Série')
    position = fields.Selection([ ('p1', '1'), ('p2', '2'),('p3', '3'),('p4', '4'),('p5', '5'),('p6', '6'),('p7', '7'),('p8', '8')], string='Position')
    
    record = fields.Selection([('non', ''),('rn_battu', 'RN Battu'), ('rn_egale', 'RN égalé'),('sb', 'SB (Saison Best)'),('pb', 'PB (Personnal Best [tout temps])')], string='Record', default='non')
    
    performance = fields.Char(string='Performance')
    performance_temps = fields.Integer(string='Performance Temps')
    performance_distance = fields.Integer(string='Performance Distance')
    
    dossard = fields.Integer(string='Dossard')
    classement_final = fields.Integer(string='Classement Final')
   
    statut_participant = fields.Selection([('none',''),('dnf',u'''DNF'''),('dns',u'''DNS'''),('dq', u'''DQ'''), ('nc', u'''NC''')], string='Staut', default='dns')

 
    
    

    
       
    
