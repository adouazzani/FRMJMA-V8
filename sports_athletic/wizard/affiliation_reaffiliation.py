# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from openerp.exceptions import ValidationError
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp


class AffiliationReaffiliation(models.TransientModel):
    _name = "sport.affiliation.reaffiliation"
    _description = "sport.affiliation.reaffiliation"


    @api.model
    def _get_club(self):
        if 1 == 1:
            athletes_obj = self.env['sports.athletes']
            order = athletes_obj.browse(self._context.get('active_ids'))[0]

        return order.club_id.id

    licence_id = fields.Many2one('sports.athletes', string='N° Licence')
    club_id = fields.Many2one('sports.club', string='Club', default=_get_club)
    responsable_id = fields.Many2one('res.users', string='Responsable', index=True, track_visibility='onchange', default=lambda self: self.env.user)

    @api.multi
    def create_reaffiliation(self):

        reaffiliation = self.env['sports.reaffiliation']
        athletes = self.env['sports.athletes']

        reaffiliation_id = self.env['sports.reaffiliation'].search([('responsable_id', '=', self.responsable_id.id),('state', '=', 'bord_attente_envoi')])

        if self.licence_id:
            saison = self.env['sports.saison'].search([('state', '=', 'active')])
            if not saison:
                raise ValidationError("Auncun saison active, merci de contacter l'administrateur.")
            if self.licence_id.state == "Sanctionne":
                sanction = self.env['sports.sanctions'].search([('athletes_id', '=', self.licence_id.id), ('saison_id', '=', saison.id), ('state', '=', "athlete_sanctionne")])
                if sanction:
                    raise ValidationError("l'athlète est en état de sanction pour cette année sportive, vous ne pouvez pas effectuer cette action.")
            if self.licence_id.state == "AnneeBlanche":
                ab = self.env['sports.anneeblanche'].search([('athletes_id', '=', self.licence_id.id), ('saison_id', '=', saison.id), ('state', '=', "athlete_sanctionne")])
                if ab:
                    raise ValidationError("l'athlète possède une année blanche pour cette année sportive, vous ne pouvez pas effectuer cette action.")
        affilia_athlete = False
        if 'active_model' in self._context and 'active_id' in self._context:
            athlete = self.env['sports.athletes'].search([('id', '=', self._context['active_id'])])
            if athlete:
                affilia_athlete = athlete.id
                # if athlete.cinjuniorsseniors:
                #     if self.licence_id.cinjuniorsseniors:
                #         self.env['attachment.history.athlete'].create({
                #             'athlete': self.licence_id.id,
                #             'type': 'cin',
                #             'attachment_filename': "CIN pour les séniors et Juniors"+".jpg",
                #             'attachment': self.licence_id.cinjuniorsseniors,
                #         })
                #     self.licence_id.cinjuniorsseniors = athlete.cinjuniorsseniors
                # if athlete.certificatmedical:
                #     self.licence_id.certificatmedical = athlete.certificatmedical
                # if athlete.cartesejour:
                #     self.licence_id.cartesejour = athlete.cartesejour
                # if athlete.autorisationparents:
                #     self.licence_id.autorisationparents = athlete.autorisationparents
                # if athlete.autorisationetrangere:
                #     self.licence_id.autorisationetrangere = athlete.autorisationetrangere
                # if athlete.certificatscolarite:
                #     self.licence_id.certificatscolarite = athlete.certificatscolarite
                # if athlete.attestationscolarite:
                #     self.licence_id.attestationscolarite = athlete.attestationscolarite
                # if athlete.actenaissance:
                #     self.licence_id.actenaissance = athlete.actenaissance

        if reaffiliation_id:
            #    a = reaffiliation_id
            #    print " reaffiliation :  "
            # print a
            #    b = reaffiliation_id.athletes3_ids
            #    print "============"
            #    print b
            reaffiliation_id.write({ 'athletes3_ids': [(6, 0, [x.id for x in self.licence_id])],
                                     'affilia_athlete': affilia_athlete, })
        else:
            reaffiliation = reaffiliation.create({
                'name': self.env['ir.sequence'].next_by_code('sports.reaffiliation'),
                'club_id': self.club_id.id,
                'ligue_id': self.club_id.ligue_id.id,
                'athletes3_ids': [(6, 0, [x.id for x in self.licence_id])],
                'affilia_athlete': affilia_athlete,
            })


        
AffiliationReaffiliation()
   
