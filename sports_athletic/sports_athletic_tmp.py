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


####Impression des assurances

class sport_print_assurance(models.Model):
    _name = "sports.print_assurance"

    name = fields.Integer(string='Nombre des athlètes en attribution a chargé')
    renouvellement = fields.Integer(string='Nombre des athlètes en renouvellement a chargé')
    reaffiliation = fields.Integer(string='Nombre des athlètes en réaffiliation a chargé')
    active = fields.Boolean(string="Paramétrage activé")


####Impression des cartes Licences


class sport_print_carte(models.Model):
    _name = "sports.print_carte"

    name = fields.Integer(string='Nombre des athlètes en attribution a chargé')
    renouvellement = fields.Integer(string='Nombre des athlètes en renouvellement a chargé')
    reaffiliation = fields.Integer(string='Nombre des athlètes en réaffiliation a chargé')
    active = fields.Boolean(string="Paramétrage activé")


####Saison sportive


class SportsSaison(models.Model):
    _name = "sports.saison"
    _order = 'date_start desc, id desc'

    @api.onchange('date_start', 'date_end', 'name')
    def _date_saison_id(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the SO.
        """
        for order in self:
            if order.date_start and order.date_end:
                year = str(order.date_start).split('-')[0]
                year2 = str(order.date_end).split('-')[0]
                order.name = str(year) + '/' + str(year2)

    name = fields.Char(string='Saison sportive', track_visibility='onchange')
    date_start = fields.Date(string='Date début', track_visibility='onchange')
    date_end = fields.Date(string='Date fin', track_visibility='onchange')

    state = fields.Selection([('future', 'Future'), ('active', 'Active'), ('cloturee', u'Cloturée')], 'Statut',
                             readonly=True, copy=False, index=True, track_visibility='onchange', default='future')
    date_start_comp = fields.Date(u"Date Début Compétition")
    date_end_comp = fields.Date(u"Date Fin Compétition")
    label_saison = fields.Char('Libellé', track_visibility='onchange')

    # Zoubida: Contraintes sur les dates debut et fin

    @api.onchange('name')
    def onchange_date(self):
        fmt = '%Y-%m-%d'
        from_date = self.date_start
        to_date = self.date_end
        if from_date and to_date:
            d1 = datetime.strptime(from_date, fmt).year
            d2 = datetime.strptime(to_date, fmt).year
            yearsDiff = str((d2 - d1))
            if d2 < d1:
                raise ValidationError("La date fin est inférieure à la date de début!!!")
            elif int(yearsDiff) != 1:
                raise ValidationError("La saison sportive ne peut avoir qu'une durrée d'un an!!!")

    # Zoubida: Contrainte unique sur la saison sportive

    _sql_constraints = [
        ('field_unique',
         'unique(name)',
         'Merci de vérifier vos informations! La saison sportive n\'est pas unique!')
    ]

    @api.multi
    def action_active(self):
        saison_ids = self.env['sports.saison'].search([('state', '=', 'active')])
        if len(saison_ids) == 1 or len(saison_ids) > 1:
            # raise ValidationError("Vous pouvez pas activer deux Saisons sportives, il faut Cloturer les Saisons sportives précédantes ")

            raise ValidationError(
                "Vous pouvez pas activer deux Saisons sportives, il faut Cloturer les Saisons sportives précédantes ")
        else:
            self.write({'state': 'active'})

        athletes_ids = self.env['sports.athletes'].search([('id', '>=', 0)])
        # category_age_change


        for athletes in athletes_ids:
            athletes.write({'saison_id': self.id, 'assure': False, 'impression': False})

        for athletes in athletes_ids:

            b = self.env['sports.category_age'].search(
                [('age_debut', '<=', athletes.age), ('age_fin', '>=', athletes.age)])

            if b and b[0] != athletes.category_age_id:
                a = b[0]
                if a and athletes.category_age_id:
                    category_age_change = True
                    athletes.write({'category_age_id': b.id, 'category_age_change': category_age_change})
            else:

                category_age_change = False
                athletes.write({'category_age_change': category_age_change})

    @api.multi
    def action_cloturee(self):

        athletes_ids = self.env['sports.athletes'].search([('id', '>=', 0)])
        for athletes in athletes_ids:
            if athletes.licence == "Athlete":

                if athletes.state == "actif":

                    athletes.write({'state': 'renouvellement'})
                elif athletes.state == "renouvellement":
                    athletes.write({'state': 'inactif'})
            else:
                athletes.write({'state': 'inactif'})
        self.write({'state': 'cloturee'})


####zone

class zone(models.Model):
    _name = "sports.zone"

    name = fields.Char(string='Zone')


####centres


class centres(models.Model):
    _name = "sports.centres"
    id_old = fields.Char(string='OLD ID')
    name = fields.Char(string='Libellé du centre')
    code = fields.Char(string='N° du centre')
    name_ar = fields.Char(string='إسم المعهد')
    adresse = fields.Char(string='Adresse')


####Ligue


class SportsLigue(models.Model):
    _name = "sports.ligue"

    id_old = fields.Char(string='OLD ID')
    name = fields.Char(string='Nom de la Ligue')
    name_ar = fields.Char(string='إسم العصبة')
    num = fields.Char(string='Numéro de la Ligue')
    saison_id = fields.Many2one('sports.saison', string='Saison sportive')
    zone_id = fields.Many2one('sports.zone', string='Zone')

    date = fields.Date(string='Date de création')

    adresse = fields.Text(string='Adresse')
    tel = fields.Char(string='Téléphone')
    fax = fields.Char(string='Fax')
    mail = fields.Char(string='E-Mail')
    situation_admin = fields.Selection([
        ('Non Conforme', 'Non Conforme'),
        ('Conforme', 'Conforme'),
    ], string='Situation Administrative')

    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
                          )
    image_medium = fields.Binary("Medium-sized image",
                                 compute='_compute_images', inverse='_inverse_image_medium', store=True,
                                 attachment=True,
                                 help="Medium-sized image of this contact. It is automatically " \
                                      "resized as a 128x128px image, with aspect ratio preserved. " \
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image",
                                compute='_compute_images', inverse='_inverse_image_small', store=True, attachment=True,
                                help="Small-sized image of this contact. It is automatically " \
                                     "resized as a 64x64px image, with aspect ratio preserved. " \
                                     "Use this field anywhere a small image is required.")

    @api.depends('image')
    def _compute_images(self):
        for rec in self:
            rec.image_medium = tools.image_resize_image_medium(rec.image)
            rec.image_small = tools.image_resize_image_small(rec.image)

    def _inverse_image_medium(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_medium)

    def _inverse_image_small(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_small)


#### Club

class SportsClub(models.Model):
    _name = "sports.club"

    @api.model
    def _get_default_saison(self):

        return self.env['sports.saison'].search([('state', '=', 'active')])

    id_old = fields.Char(string='OLD ID')
    name = fields.Char(string='Nom')
    name_ar = fields.Char(string='الإسم')
    num = fields.Char(string='Sigle du Club')
    contact = fields.Char(string='Contact')

    code = fields.Char(string='Code Club')  # Code champs a saire  ++++ 01062016
    saison_id = fields.Many2one('sports.saison', string='Saison sportive', default=_get_default_saison)
    code = fields.Char(string='Code')

    ligue_id = fields.Many2one('sports.ligue', string='Ligue')

    adresse = fields.Text(string='Adresse')

    region = fields.Char(string='Région')  # ++++ 01062016
    commune = fields.Char(string='Ville')  # ++++ 01062016
    zone_id = fields.Many2one('sports.zone', string='Zone')

    tel = fields.Char(string='Téléphone')
    gsm = fields.Char(string='GSM')  # ++++ 01062016s
    fax = fields.Char(string='Fax')
    mail = fields.Char(string='E-Mail')
    situation_admin = fields.Selection([
        ('Non Conforme', 'Non Conforme'),
        ('Conforme', 'Conforme'),
    ], string='Situation Administrative')

    date = fields.Date(string='Date de création')

    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
                          )
    image_medium = fields.Binary("Medium-sized image",
                                 compute='_compute_images', inverse='_inverse_image_medium', store=True,
                                 attachment=True,
                                 help="Medium-sized image of this contact. It is automatically " \
                                      "resized as a 128x128px image, with aspect ratio preserved. " \
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image",
                                compute='_compute_images', inverse='_inverse_image_small', store=True, attachment=True,
                                help="Small-sized image of this contact. It is automatically " \
                                     "resized as a 64x64px image, with aspect ratio preserved. " \
                                     "Use this field anywhere a small image is required.")

    @api.depends('image')
    def _compute_images(self):
        for rec in self:
            rec.image_medium = tools.image_resize_image_medium(rec.image)
            rec.image_small = tools.image_resize_image_small(rec.image)

    def _inverse_image_medium(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_medium)

    def _inverse_image_small(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_small)


#####Catégories d’âges


class SportsCategory_age(models.Model):
    _name = "sports.category_age"

    name = fields.Char(string='Désignation')
    description = fields.Text(string='Description')
    age_debut = fields.Integer(string='Age debut')
    age_fin = fields.Integer(string='Age Fin')
    order = fields.Integer(string='Order')


#####Type licence


class SportsLicence(models.Model):
    _name = "sports.licence"

    name = fields.Char(string='Licence')


#####Objectifs


class SportsObjectif(models.Model):
    _name = "sports.objectif"

    name = fields.Char(string='Objectif')


#####discipline


class Sportsdiscipline(models.Model):
    _name = "sports.discipline"

    name = fields.Char(string='Discipline')


######theme


class Sportstheme(models.Model):
    _name = "sports.theme"

    name = fields.Char(string='Théme')


######Degré de similitude


class SportsDegresimilitude(models.Model):
    _name = "sports.degresimilitude"

    name = fields.Char(string='Degré de similitude')


######Niveau scolaire


class SportsNiveauscolaire(models.Model):
    _name = "sports.niveauscolaire"

    name = fields.Char(string='Niveau scolaire')


######Banque


class SportsBanque(models.Model):
    _name = "sports.banque"

    name = fields.Char(string='Banque')


######Statut licence athléte


class SportsStatutlicence(models.Model):
    _name = "sports.statutlicence"

    name = fields.Char(string='Statut licence athléte')


##### Demande d’affiliation


class SportsAffiliation(models.Model):
    _name = "sports.affiliation"
    _description = "affiliation"

    @api.model
    def _get_default_saison(self):

        return self.env['sports.saison'].search([('state', '=', 'active')])

    saison_id = fields.Many2one('sports.saison', string='Saison sportive', default=_get_default_saison)
    name = fields.Char(string='N° de demande', required=True, copy=False, readonly=True, index=True, default='Nouveau')
    ligue_id = fields.Many2one('sports.ligue', string='Ligue', track_visibility='onchange')
    club_id = fields.Many2one('sports.club', string='Club', track_visibility='onchange')

    athletes_ids = fields.One2many('sports.athletes', 'affiliation_id', string='Athletes')

    licence = fields.Selection([
        ('Athlete', 'Athléte'),
        ('Entraineur', 'Entraineur'),
        ('Dirigeant', 'Dirigeant'),
        ('Officiel', 'Officiel'),

    ], string='Type Affiliation')
    responsable_id = fields.Many2one('res.users', string='Responsable', index=True, track_visibility='onchange',
                                     default=lambda self: self.env.user)
    date_create = fields.Datetime(string='Date de Création', copy=False, default=fields.Datetime.now)

    state = fields.Selection(
        [("bord_attente_envoi", "Attente d'envoi"), ("dem_attente_verif", " Attente  Vérification"),
         ("ath_attente_crea", "Attente Création"), ("edition_licence_assu", "Attente Edition"), ("edition", "Edition"),
         ("licence_attente_dispo_club", "Mise à disposition"), ("licence_attente_recup", "A Rrécupérer"),
         ("licence_recuperees", "Récupérée"), ("affiliation_rejetee", "Rejetées")], 'Statut', readonly=True, copy=False,
        index=True, track_visibility='onchange', default='bord_attente_envoi')

    mode_creation_ath = fields.Selection([("normal", "Pas de blocage"), ('blocage', 'Blocage si un athlète existant')],
                                         'Politique de création des athlètes',
                                         help="Blocage lorsqu\'un athlète(Nom,Prénom,Date naissance) est déja dans le système",
                                         readonly=False, copy=False, index=True, track_visibility='onchange',
                                         default='blocage')

    date_init_bord_attente_envoi = fields.Datetime('Date initiale de l\'Envoi du Bordereau le', readonly=True)
    user_init_bord_attente_envoi = fields.Many2one('res.users', 'Par', readonly=True)
    date_bord_attente_envoi = fields.Datetime('Envoi du Bordereau le', readonly=True)
    user_bord_attente_envoi = fields.Many2one('res.users', 'Par', readonly=True)
    date_dem_attente_verif = fields.Datetime('Vérification et Validation de la Demande le', readonly=True)
    user_dem_attente_verif = fields.Many2one('res.users', 'Par', readonly=True)
    date_ath_attente_crea = fields.Datetime('Création des Athlètes le', readonly=True)
    user_ath_attente_crea = fields.Many2one('res.users', 'Par', readonly=True)
    date_edition_licence_assu = fields.Datetime('Edition des licences et Assurances le', readonly=True)
    user_edition_licence_assu = fields.Many2one('res.users', 'Par', readonly=True)
    date_licence_attente_dispo_club = fields.Datetime('Mise à Disposition des Licences au Club le', readonly=True)
    user_licence_attente_dispo_club = fields.Many2one('res.users', 'Par', readonly=True)
    date_licence_attente_recup = fields.Datetime('Licences récupérées par le Club', readonly=True)
    user_licence_attente_recup = fields.Many2one('res.users', 'Par', readonly=True)
    date_affiliation_rejetee = fields.Datetime('Demandes d\'affiliations rejetées le', readonly=True)
    user_affiliation_rejetee = fields.Many2one('res.users', 'Par', readonly=True)
    # Zoubida: fields imprime et assure avec computes

    is_assure = fields.Boolean('Assuré', default=False, compute='_compute_is_assure')
    is_imprime = fields.Boolean('Imprimé', default=False, compute='_compute_is_imprime')

    @api.multi
    def _compute_is_assure(self):
        assure = False
        for obj in self.athletes_ids:
            if obj.assure:
                assure = True
            else:
                assure = False
        if assure:
            self.is_assure = True
        else:
            self.is_assure = False

    @api.multi
    def _compute_is_imprime(self):
        imprime = False
        for obj in self.athletes_ids:
            if obj.impression:
                imprime = True
            else:
                imprime = False
        if imprime:
            self.is_imprime = True
        else:
            self.is_imprime = False

    @api.onchange('club_id')
    def _ligue_id(self):

        for order in self:
            a = self.env['sports.ligue'].search([('id', '=', order.club_id.ligue_id.id)])
            order.ligue_id = a

    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].next_by_code('sports.affiliation')
        result = super(SportsAffiliation, self).create(vals)
        return result

    @api.multi
    def action_envoyer(self):
        self.write({'state': 'dem_attente_verif',
                    'date_init_bord_attente_envoi': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'user_init_bord_attente_envoi': self.env.uid,
                    'date_bord_attente_envoi': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'user_bord_attente_envoi': self.env.uid})

    @api.multi
    def generate_report(self):

        report_ids = self.env['ir.actions.report.xml'].search([('report_type', '=', 'aeroo'),
                                                               ('model', '=', 'sports.affiliation'),
                                                               ('report_name', '=', 'report_affiliation_ods')])
        return self.env['report'].get_action(
            self, report_ids.report_name)

    @api.multi
    def action_verification(self):
        if self.athletes_ids:

            for athlete in self.athletes_ids:
                y = ""
                message = title = ""
                a = self.env['sports.athletes'].search(
                    [('prenom', '=', str(athlete.prenom).upper()), ('name_at', '=', str(athlete.name_at).upper()),
                     ('id', '!=', athlete.id)])
                # a = self.env['sports.athletes'].search([('prenom', '=', athlete.prenom),('name_at', '=', athlete.name_at),('id', '!=',athlete.id)])
                z = self.env['sports.athletes'].search(
                    [('prenom', '=', str(athlete.prenom).upper()), ('name_at', '=', str(athlete.name_at).upper()),
                     ('id', '!=', athlete.id), ('id', '!=', athlete.id), ('affiliation_id', '=', self.id)])
                # z =self.env['sports.athletes'].search([('prenom', '=', athlete.prenom),('name_at', '=', athlete.name_at),('id', '!=',athlete.id),('affiliation_id', '=',self.id)])
                if len(z) > 1 or len(z) == 1:
                    for d in z:
                        # raise ValidationError("Vous avez saisie une demande d\'affiliation en double")
                        # message = "Vous avez saisie une demande d\'affiliation en double !!!"
                        raise ValidationError("Vous avez saisie une demande d\'affiliation en double!!!")
                if len(a) > 1 or len(a) == 1:
                    for b in a:
                        self.env['sports.doublon'].create({'athletes_id': b.id})
                        y = '---> N° Licence :' + str(b.name) + ' N°Affiliation : ' + str(
                            b.affiliation_id.name) + ' ' + y
                    athlete.write({'doublon': y, 'double': True})
                # raise ValidationError("Vous avez des doublons !!!")

                athlete.write({'situation_etat': 'Attribution'})
            self.write(
                {'state': 'ath_attente_crea', 'date_dem_attente_verif': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                 'user_dem_attente_verif': self.env.uid})
        else:

            # raise ValidationError("Vous devez créer une ou plusieurs demandes!!!")
            raise ValidationError("Vous devez créer une ou plusieurs demandes!!!")

    @api.multi
    def action_creation(self):
        if self.athletes_ids:

            if self.club_id.situation_admin != "Conforme":
                # raise ValidationError("La Situation Administrative du Club doit être conforme")
                raise ValidationError("La Situation Administrative du Club doit être conforme!!!")

            for athletes in self.athletes_ids:

                if athletes.double == True and athletes.force == False:
                    raise ValidationError(
                        "Vous avez des demandes d\'affilation en double merci de supprimer la demande / forcer ca création")
                else:
                    # dev Zoubida
                    if athletes.state != "nonConforme" and athletes.name == 'Nouveau':
                        athletes.write(
                            {'state': 'actif', 'name': self.env['ir.sequence'].next_by_code('sports.athletes')})

            self.write({'state': 'edition_licence_assu',
                        'date_ath_attente_crea': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'user_ath_attente_crea': self.env.uid})
        else:
            raise ValidationError("Vous devez créer une ou plusieurs demandes")

    @api.multi
    def action_edition(self):
        if self.athletes_ids:

            if self.club_id.situation_admin != "Conforme":
                raise ValidationError("La Situation Administrative du Club doit être conforme")

            for athletes in self.athletes_ids:
                if athletes.name == 'Nouveau':
                    athletes.write({'state': 'actif', 'name': self.env['ir.sequence'].next_by_code('sports.athletes')})

            self.write({'state': 'edition', 'date_edition_licence_assu': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'user_edition_licence_assu': self.env.uid})
        else:
            raise ValidationError("Vous devez créer une ou plusieurs demandes")

    @api.multi
    def action_edition(self):
        if self.athletes_ids:

            if self.club_id.situation_admin != "Conforme":
                raise ValidationError("La Situation Administrative du Club doit être conforme")

            for athletes in self.athletes_ids:
                if athletes.name == 'Nouveau':
                    athletes.write({'state': 'actif', 'name': self.env['ir.sequence'].next_by_code('sports.athletes')})

            self.write({'state': 'edition', 'date_edition_licence_assu': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'user_edition_licence_assu': self.env.uid})
        else:
            raise ValidationError("Vous devez créer une ou plusieurs demandes")

    @api.multi
    def action_licence_attente_dispo_club(self):
        if self.athletes_ids:

            if self.club_id.situation_admin != "Conforme":
                raise ValidationError("La Situation Administrative du Club doit être conforme")

            self.write({'state': 'licence_attente_dispo_club',
                        'date_licence_attente_dispo_club': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'user_licence_attente_dispo_club': self.env.uid})
        else:
            raise ValidationError("Vous devez créer une ou plusieurs demandes")

    @api.multi
    def action_licence_attente_recup(self):
        if self.athletes_ids:

            if self.club_id.situation_admin != "Conforme":
                raise ValidationError("La Situation Administrative du Club doit être conforme")

            self.write({'state': 'licence_attente_recup',
                        'date_licence_attente_recup': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'user_licence_attente_recup': self.env.uid})
        else:
            raise ValidationError("Vous devez créer une ou plusieurs demandes")

    @api.multi
    def action_licence_recuperees(self):
        if self.athletes_ids:

            if self.club_id.situation_admin != "Conforme":
                raise ValidationError("La Situation Administrative du Club doit être conforme")

            self.write({'state': 'licence_recuperees',
                        'date_licence_attente_recup': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'user_licence_attente_recup': self.env.uid})
        else:
            raise ValidationError("Vous devez créer une ou plusieurs demandes")

    @api.multi
    def action_affiliation_rejetee(self):
        if self.athletes_ids:

            if self.club_id.situation_admin != "Conforme":
                raise ValidationError("La Situation Administrative du Club doit être conforme")

            for athletes in self.athletes_ids:
                if athletes.name == 'Nouveau':
                    athletes.write({'state': 'Rejete'})

            self.write({'state': 'affiliation_rejetee',
                        'date_affiliation_rejetee': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'user_affiliation_rejetee': self.env.uid})
        else:
            raise ValidationError("Vous devez créer une ou plusieurs demandes")


##### Demande Renouvellement des Licences

class Sportsrenouvellement(models.Model):
    _name = "sports.renouvellement"
    _description = "Renouvellement des licences"

    @api.model
    def _get_default_saison(self):

        return self.env['sports.saison'].search([('state', '=', 'active')])

    saison_id = fields.Many2one('sports.saison', string='Saison sportive', default=_get_default_saison)

    name = fields.Char('N°', required=True, copy=False, readonly=True, index=True, default='Nouveau')
    message1 = fields.Text('message1', readonly=True)
    message2 = fields.Text('message2', readonly=True)
    ligue_id = fields.Many2one('sports.ligue', string='Ligue', track_visibility='onchange')
    club_id = fields.Many2one('sports.club', string='Club', track_visibility='onchange')

    athletes2_ids = fields.Many2many('sports.athletes', string='Athletes')

    state = fields.Selection(
        [('dem_att_verif', 'Attente de Renouvellement'), ("edition_licence_attente", "Attente d'édition"),
         ("edition_licence_assu", "Edition"), ('ren_rejete', 'Rejeté')], 'Statut', readonly=True, copy=False,
        index=True, track_visibility='onchange', default='dem_att_verif')

    responsable_id = fields.Many2one('res.users', string='Responsable', index=True, track_visibility='onchange',
                                     default=lambda self: self.env.user)
    date_create = fields.Datetime(string='Date de Création', copy=False, default=fields.Datetime.now)

    user_dem_att_verif = fields.Many2one('res.users', 'Par', readonly=True)
    date_dem_att_verif = fields.Datetime('Vérification de la demande le', readonly=True)
    user_att_ren_lic = fields.Many2one('res.users', 'Par', readonly=True)
    date_att_ren_lic = fields.Datetime('Renouvellement des licences le', readonly=True)
    date_edition_licence_assu = fields.Datetime('Edition des licences et Assurances le', readonly=True)
    user_edition_licence_assu = fields.Many2one('res.users', 'Par', readonly=True)
    user_att_dispo_club = fields.Many2one('res.users', 'Par', readonly=True)
    date_att_dispo_club = fields.Datetime('Mise à Disposition des cartes licences le', readonly=True)
    user_att_recup_club = fields.Many2one('res.users', 'Par', readonly=True)
    date_att_recup_club = fields.Datetime('Récupération des cartes le', readonly=True)
    user_ren_rejete = fields.Many2one('res.users', 'Par', readonly=True)
    date_ren_rejete = fields.Datetime('Renouvellement Rejeté le', readonly=True)
    responsable_id = fields.Many2one('res.users', string='Responsable', index=True, track_visibility='onchange',
                                     default=lambda self: self.env.user)
    date_create = fields.Datetime(string='Date de Création', copy=False, default=fields.Datetime.now)
    afficher_button = fields.Boolean('Afficher button')
    licence = fields.Selection([
        ('Athlete', 'Athléte'),
        ('Entraineur', 'Entraineur'),
        ('Dirigeant', 'Dirigeant'),
        ('Officiel', 'Officiel'),

    ], string='Type de Renouvellement')

    # Zoubida: fields imprime et assure avec computes

    is_assure = fields.Boolean('Assuré', default=False, compute='_compute_is_assure')
    is_imprime = fields.Boolean('Imprimé', default=False, compute='_compute_is_imprime')

    @api.multi
    def _compute_is_imprime(self):
        imprime = False
        for obj in self.athletes2_ids:
            if obj.impression:
                imprime = True
            else:
                imprime = False
        if imprime:
            self.is_imprime = True
        else:
            self.is_imprime = False

    @api.multi
    def _compute_is_assure(self):
        assure = False
        for obj in self.athletes2_ids:
            if obj.assure:
                assure = True
            else:
                assure = False
        if assure:
            self.is_assure = True
        else:
            self.is_assure = False

    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].next_by_code('sports.renouvellement')
        result = super(Sportsrenouvellement, self).create(vals)
        return result

    @api.onchange('club_id')
    def _ligue_id(self):

        for order in self:
            a = self.env['sports.ligue'].search([('id', '=', order.club_id.ligue_id.id)])
            order.ligue_id = a

    @api.multi
    def action_att_ren_lic(self):
        self.write(
            {'state': 'edition_licence_attente', 'date_dem_att_verif': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
             'user_dem_att_verif': self.env.uid})

    @api.multi
    def generate_report(self):

        report_ids = self.env['ir.actions.report.xml'].search([('report_type', '=', 'aeroo'),
                                                               ('model', '=', 'sports.renouvellement'),
                                                               ('report_name', '=', 'report_renouvellement_ods')])
        return self.env['report'].get_action(
            self, report_ids.report_name)

    @api.multi
    def action_edition_licence_assu(self):
        if self.athletes2_ids:

            if self.club_id.situation_admin != "Conforme":
                raise ValidationError("La Situation Administrative du Club doit être conforme")

            for athletes in self.athletes2_ids:
                athletes.write({'state': 'actif', 'situation_etat': 'Renouvellement'})

            self.write(
                {'state': 'edition_licence_assu', 'date_att_ren_lic': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                 'user_att_ren_lic': self.env.uid})
        else:
            raise ValidationError("Vous devez créer une ou plusieurs demandes")


##### Demande Réaffiliation des Licences

class Sportsreaffiliation(models.Model):
    _name = "sports.reaffiliation"
    _description = "Reaffiliation des licences"

    @api.model
    def _get_default_saison(self):

        return self.env['sports.saison'].search([('state', '=', 'active')])

    saison_id = fields.Many2one('sports.saison', string='Saison sportive', default=_get_default_saison)

    name = fields.Char('N° Demande', required=True, copy=False, readonly=True, index=True, default='Nouveau')
    ligue_id = fields.Many2one('sports.ligue', string='Ligue', track_visibility='onchange')
    club_id = fields.Many2one('sports.club', string='Club', track_visibility='onchange')

    # athletes_reaffiliation_ids = fields.One2many('sports.athletes.reaffiliation', 'reaffiliation_id', string='Athletes')

    athletes3_ids = fields.Many2many('sports.athletes', string='Athletes')

    state = fields.Selection([("bord_attente_envoi", "Attente d'envoi"),
                              ("dem_attente_verif", "Attente  Vérification"),
                              ("ath_attente_crea", "Attente Création"),
                              ("edition_licence_assu", "Attente Edition"),
                              ("edition", "Edition"),
                              ("licence_dispo_club", "Attente de mise à disposition aux clubs"),
                              ("licence_attente_recup", "Licences à récupérer par le Club"),
                              ("licence_recuperees", "Licences récupérées par le Club"),
                              ("affiliation_rejetee", "Rejetées")], 'Statut', readonly=True, copy=False, index=True,
                             track_visibility='onchange', default='bord_attente_envoi')

    user_init_bord_attente_envoi = fields.Many2one('res.users', 'Par', readonly=True)
    date_bord_attente_envoi = fields.Datetime('Création du Bordereau le', readonly=True)
    user_bord_attente_envoi = fields.Many2one('res.users', 'Par', readonly=True)
    date_dem_attente_verif = fields.Datetime('Vérification et Validation de la Demande le', readonly=True)
    user_dem_attente_verif = fields.Many2one('res.users', 'Par', readonly=True)
    date_ath_attente_crea = fields.Datetime('Mise à jour des fiches athlètes le', readonly=True)
    user_ath_attente_crea = fields.Many2one('res.users', 'Par', readonly=True)
    date_edition_licence_assu = fields.Datetime('Edition des licences et Assurances le', readonly=True)
    user_edition_licence_assu = fields.Many2one('res.users', 'Par', readonly=True)
    date_comp_licence_assu = fields.Datetime('Envoyer la liste des licences à la compangnie d\'assurances le',
                                             readonly=True)
    user_comp_licence_assu = fields.Many2one('res.users', 'Par', readonly=True)
    date_licence_attente_dispo_club = fields.Datetime('Mise à Disposition des Licences au Club le', readonly=True)
    user_licence_attente_dispo_club = fields.Many2one('res.users', 'Par', readonly=True)
    date_licence_attente_recup = fields.Datetime('Licences récupérées par le Club', readonly=True)
    user_licence_attente_recup = fields.Many2one('res.users', 'Par', readonly=True)
    date_affiliation_rejetee = fields.Datetime('Demandes d\'affiliations rejetées le', readonly=True)
    user_affiliation_rejetee = fields.Many2one('res.users', 'Par', readonly=True)

    responsable_id = fields.Many2one('res.users', string='Responsable', index=True, track_visibility='onchange',
                                     default=lambda self: self.env.user)
    date_create = fields.Datetime(string='Date de Création', copy=False, default=fields.Datetime.now)
    afficher_button = fields.Boolean('Afficher button'),
    licence = fields.Selection([
        ('Athlete', 'Athléte'),
        ('Entraineur', 'Entraineur'),
        ('Dirigeant', 'Dirigeant'),
        ('Officiel', 'Officiel'),

    ], string='Type de Réaffiliation')

    # Zoubida: fields imprime et assure avec computes

    is_assure = fields.Boolean('Assuré', default=False, compute='_compute_is_assure')
    is_imprime = fields.Boolean('Imprimé', default=False, compute='_compute_is_imprime')

    @api.multi
    def _compute_is_imprime(self):
        imprime = False
        for obj in self.athletes3_ids:
            if obj.impression:
                imprime = True
            else:
                imprime = False
        if imprime:
            self.is_imprime = True
        else:
            self.is_imprime = False

    @api.multi
    def _compute_is_assure(self):
        assure = False
        for obj in self.athletes3_ids:
            if obj.assure:
                assure = True
            else:
                assure = False
        if assure:
            self.is_assure = True
        else:
            self.is_assure = False

    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].next_by_code('sports.reaffiliation')
        result = super(Sportsreaffiliation, self).create(vals)
        return result

    @api.onchange('club_id')
    def _ligue_id(self):

        for order in self:
            a = self.env['sports.ligue'].search([('id', '=', order.club_id.ligue_id.id)])
            order.ligue_id = a

    @api.multi
    def action_verification(self):
        if self.athletes3_ids:

            self.write(
                {'state': 'ath_attente_crea', 'date_dem_attente_verif': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                 'user_dem_attente_verif': self.env.uid})

        else:

            raise ValidationError("Vous devez créer une ou plusieurs demandes!!!")

    @api.multi
    def generate_report(self):

        report_ids = self.env['ir.actions.report.xml'].search([('report_type', '=', 'aeroo'),
                                                               ('model', '=', 'sports.reaffiliation'),
                                                               ('report_name', '=', 'report_reaffiliation_ods')])
        return self.env['report'].get_action(
            self, report_ids.report_name)

    @api.multi
    def action_envoyer(self):
        self.write({'state': 'dem_attente_verif',
                    'date_init_bord_attente_envoi': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'user_init_bord_attente_envoi': self.env.uid,
                    'date_bord_attente_envoi': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'user_bord_attente_envoi': self.env.uid})

    @api.multi
    def action_creation(self):
        if self.athletes3_ids:

            if self.club_id.situation_admin != "Conforme":
                raise ValidationError("La Situation Administrative du Club doit être conforme")

            for athletes in self.athletes3_ids:

                if athletes.state != "nonConforme":
                    athletes.write(
                        {'state': 'attente_activation', 'club_id': self.club_id.id, 'ligue_id': self.ligue_id.id})

            self.write({'state': 'edition_licence_assu',
                        'date_ath_attente_crea': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'user_ath_attente_crea': self.env.uid})
        else:
            raise ValidationError("Vous devez créer une ou plusieurs demandes")

    @api.multi
    def action_edition(self):
        if self.athletes3_ids:

            if self.club_id.situation_admin != "Conforme":
                raise ValidationError("La Situation Administrative du Club doit être conforme")

            for athletes in self.athletes3_ids:
                if athletes.name == 'Nouveau':
                    athletes.write({'state': 'actif', 'situation_etat': 'Renouvellement'})

            self.write({'state': 'edition', 'date_edition_licence_assu': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'user_edition_licence_assu': self.env.uid})
        else:
            raise ValidationError("Vous devez créer une ou plusieurs demandes")


class SportsReaffiliationAthletes(models.Model):
    _name = "sports.athletes.reaffiliation"
    _description = "Reaffiliation athletes "

    name = fields.Char('Nom', required=True, copy=False, readonly=True, index=True, default='Nouveau')
    athletes_id = fields.Many2one('sports.athletes', 'N° Licence')
    reaffiliation_id = fields.Many2one('sports.reaffiliation', 'N° de la demande de Réaffiliation', readonly=True)

    actenaissance = fields.Binary('Extrait d\'acte de Naissance')
    actenaissance_filename = fields.Char("Extrait d\'acte de Naissance Filename")

    cinjuniorsseniors = fields.Binary('CIN pour les Séniors et Juniors')
    cinjuniorsseniors_filename = fields.Char("CIN pour les Séniors et Juniors Filename")

    certificatmedical = fields.Binary('Cértificat Médical')
    certificatmedical_filename = fields.Char("Cértificat Médical Filename")

    autorisationparents = fields.Binary('Autorisation des Parents')
    autorisationparents_filename = fields.Char("Autorisation des Parents Filename")

    cartesejour = fields.Binary('Carte Séjour')
    cartesejour_filename = fields.Char("Carte Séjour Filename")

    autorisationetrangere = fields.Binary('Autorisation étrangère')
    autorisationetrangere_filename = fields.Char("Autorisation étrangère Filename")

    certificatscolarite = fields.Binary('Cértificat de Scolarité')
    certificatscolarite_filename = fields.Char("Cértificat de Scolarité Filename")

    attestationscolarite = fields.Binary('Attestation de Scolarité')
    attestationscolarite_filename = fields.Char("Attestation de Scolarité Filename")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sports.athletes.reaffiliation')
        result = super(SportsReaffiliationAthletes, self).create(vals)
        return result


class SportsAthletes(models.Model):
    _name = "sports.athletes"

    @api.depends('datenaissance', 'category_age_id', 'saison_id')
    def _compute_age(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.datenaissance and line.saison_id:
                datenaissance = line.datenaissance
                year = str(line.datenaissance).split('-')[0]
                datenow = line.saison_id.date_end
                year2 = str(datenow).split('-')[0]
                age = (int(year2) - int(year)) - 1
            else:
                age = 0

            line.update({
                'age': age,

            })

    @api.onchange('age', 'datenaissance', 'saison_id', 'category_age_id')
    def _category_age_id(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the SO.
        """
        for order in self:
            if order.age > 0:
                b = self.env['sports.category_age'].search(
                    [('age_debut', '<=', order.age), ('age_fin', '>=', order.age)])

                if b:
                    a = b[0]
                    order.category_age_id = a

    @api.onchange('cin', 'name_at', 'prenom')
    def _cin(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the SO.
        """
        for order in self:
            if order.cin:
                a = self.env['sports.athletes'].search([('cin', '=', order.cin), ('state', '!=', 'nonConforme')])
                if len(a) == 1 or len(a) > 1:
                    # raise ValidationError("Le numéro de CIN est déja utilisé")
                    raise ValidationError("Le numéro de CIN est déja utilisé'")
                order.cin = str(order.cin).upper()

    @api.onchange('name_at', 'prenom')
    def _name_prenom1(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the SO.
        """
        for order in self:
            if order.name_at:
                order.name_at = str(order.name_at).upper()
            if order.prenom:
                order.prenom = str(order.prenom).upper()

    @api.onchange('licence', 'name_ar')
    def _name_prenom(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the SO.
        """
        for order in self:
            if order.name_at:
                order.name_at = str(order.name_at).upper()
            if order.prenom:
                order.prenom = str(order.prenom).upper()
            if order.name_at and order.prenom:
                a = self.env['sports.athletes'].search(
                    [('prenom', '=', str(order.prenom).upper()), ('name_at', '=', str(order.name_at).upper())])

                if len(a) == 1 or len(a) > 1:
                    # raise ValidationError("Le nom et le prénom sont déja utilisés")
                    raise ValidationError("Le nom et le prénom sont déja utilisés")

    @api.model
    def _get_default_saison(self):

        return self.env['sports.saison'].search([('state', '=', 'active')])

    @api.model
    def _get_default_category_age(self):
        if self.env['sports.category_age'].search([('age_debut', '<=', self.age), ('age_fin', '>=', self.age)]):
            return self.env['sports.category_age'].search([('age_debut', '<=', self.age), ('age_fin', '>=', self.age)])[
                0]

    @api.multi
    def name_get(self):
        res = []
        name = ""
        for record in self:
            if record.name:
                name = "["+record.name+"]"
            if record.cin:
                name = "[ " + record.name + " / " + record.cin + " ]"
            if record.name_at:
                name = name + " " + record.name_at
            if record.prenom:
                name = name + " " + record.prenom
            res.append((record.id, name))
        return res

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        ids = []
        if name:
            ids = self.search(cr, user, [('name', 'ilike', name)] + args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('cin', 'ilike', name)] + args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('name_at', 'ilike', name)] + args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('prenom', 'ilike', name)] + args, limit=limit)
            if not ids and len(name.split()) >= 2:
                # Separating code and name for searching
                operand1, operand2 = name.split(' ', 1)  # name can contain spaces
                ids = self.search(cr, user, [('name_at', 'ilike', operand1), ('prenom', 'ilike', operand2)] + args,
                                  limit=limit)
                if not ids:
                    ids = self.search(cr, user, [('name_at', 'ilike', operand2), ('prenom', 'ilike', operand1)] + args,
                                      limit=limit)
        else:
            ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)

    saison_id = fields.Many2one('sports.saison', string='Saison sportive', default=_get_default_saison)

    name = fields.Char(string='N° licence', copy=False, readonly=False, index=True, default='Nouveau')
    name2 = fields.Char(string='OLD ID', copy=False, readonly=False)
    prenom = fields.Char(string='Prénom', track_visibility='onchange')

    name_ar = fields.Char(string='الاسم الكامل', track_visibility='onchange')

    name_at = fields.Char(string='Nom', track_visibility='onchange')

    category_age_id = fields.Many2one('sports.category_age', string='Catégorie d’âge',
                                      default=_get_default_category_age, track_visibility='onchange')

    licence = fields.Selection([
        ('Athlete', 'Athlete'),
        ('Entraineur', 'Entraineur'),
        ('Dirigeant', 'Dirigeant'),
        ('Officiel', 'Officiel')

    ], string='Type licence')

    sexe = fields.Selection([
        ('h', 'Masculin'),
        ('f', 'Féminin'),
    ], string='Sexe')

    situation_etat = fields.Selection([
        ('Attribution', 'Attribution'),
        ('Reaffiliations', 'Réaffiliations'),
        ('Renouvellement', 'Renouvellement'),
    ], string='Situation Actuel', readonly=True)

    lieu_naissance = fields.Char(string='Lieu de naissance')
    datenaissance = fields.Date(string='Date de naissance', track_visibility='onchange')

    adresse = fields.Char(string='Adresse')
    name_pere = fields.Char(string='Nom père')
    name_mere = fields.Char(string='Nom mère')
    adresse_adresse = fields.Char(string='Adresse Parent')
    cin = fields.Char(string='CIN', track_visibility='onchange')
    cinexpiration = fields.Date(string='Date Expiration CIN? ')

    far = fields.Boolean(string='Far')
    order_mission = fields.Char(string='Ordre de mission')
    date = fields.Date(string='Date d\'ordre')
    date_exp = fields.Date(string='Date d\'expiration')

    affiliation_id = fields.Many2one('sports.affiliation', string='N° d\'Affiliation', readonly=True)
    renouvellement_id = fields.Many2one('sports.renouvellement', string='N° de Renouvellement')

    renouvele = fields.Boolean(string='renouvellement ')
    inactif = fields.Boolean(string='Inactif')

    force = fields.Boolean(string='Forcé')
    double = fields.Boolean(string='Doublons ?')

    dateaffiliation = fields.Date(string='Date d\'Affiliation')
    daterenouvellement = fields.Date(string='Date de Renouvellement')
    dateassurance = fields.Datetime(string='Date d\'impression de l\'assurance')

    passeport = fields.Char(string='N° Passeport ')
    visaobtenu = fields.Char(string='Visa obtenu? ')
    sejour = fields.Char(string='Séjour')

    passeportexpiration = fields.Date(string='Date Expiration Passeport? ')
    visaobtenuexpiration = fields.Date(string='Date Expiration VISA?')
    sejourexpiration = fields.Date(string='Date Expiration Séjour?')

    numassurance = fields.Char(string='N° Assurance')
    numassuranceexpiration = fields.Date(string='Date Expiration Assurance?')

    banque_id = fields.Many2one('sports.banque', string='Banque')
    rib = fields.Char(string='RIB')
    telbanque = fields.Char(string='Tel')
    ruebanque = fields.Char(string='Rue')

    tel1 = fields.Char(string='N° Téléphone Fixe')
    tel2 = fields.Char(string='Téléphone Mobile')
    mail = fields.Char(string='Email')
    ville = fields.Char(string='Ville')
    code_postal = fields.Char(string='Code Postal ')
    code_postal2 = fields.Char(string='Code Postal parent ')

    telparent = fields.Char(string='Tel parent')

    # ligue_id = fields.Many2one(related='affiliation_id.ligue_id', store=True)
    # club_id = fields.Many2one(related='affiliation_id.club_id', store=True)
    # saison_id = fields.Many2one(related='affiliation_id.saison_id', store=True)

    ligue_id = fields.Many2one('sports.ligue', string='Ligue')
    club_id = fields.Many2one('sports.club', string='Club')

    entraineur_id = fields.Many2one('sports.athletes', string='Entraineur')

    # discipline = fields.Text(string='Discipline')
    discipline_id = fields.Many2one('sports.discipline', string='Discipline')

    doublon = fields.Text(string='Doublon ?')

    raison = fields.Text(string='Raison')

    note = fields.Text(string='Note')
    pointure = fields.Float('Pointure')
    taille = fields.Float('Taille')
    grade = fields.Float('Grade')
    montantbourse = fields.Float('Montant de la bourse')

    surclassement = fields.Selection([('non_surclasse', 'Non surclassé'), ('surclasse', 'surclassé')],
                                     'Surclassement ?', readonly=True, copy=False, index=True,
                                     track_visibility='onchange', default='non_surclasse')

    actenaissance = fields.Binary('Extrait d\'acte de Naissance')
    actenaissance_filename = fields.Char("Extrait d\'acte de Naissance Filename")

    cinjuniorsseniors = fields.Binary('CIN pour les Séniors et Juniors')
    cinjuniorsseniors_filename = fields.Char("CIN pour les Séniors et Juniors Filename")

    certificatmedical = fields.Binary('Cértificat Médical')
    certificatmedical_filename = fields.Char("Cértificat Médical Filename")

    autorisationparents = fields.Binary('Autorisation des Parents')
    autorisationparents_filename = fields.Char("Autorisation des Parents Filename")

    cartesejour = fields.Binary('Carte Séjour')
    cartesejour_filename = fields.Char("Carte Séjour Filename")

    autorisationetrangere = fields.Binary('Autorisation étrangère')
    autorisationetrangere_filename = fields.Char("Autorisation étrangère Filename")

    certificatscolarite = fields.Binary('Cértificat de Scolarité')
    certificatscolarite_filename = fields.Char("Cértificat de Scolarité Filename")

    attestationscolarite = fields.Binary('Attestation de Scolarité')
    attestationscolarite_filename = fields.Char("Attestation de Scolarité Filename")

    autre = fields.Binary('Autre')
    autre_filename = fields.Char("Autre Filename")

    ##One2Many
    reaffiliation_ids = fields.One2many('sports.athletes.reaffiliation', 'athletes_id', 'Reaffiliations')
    mutations_ids = fields.One2many('sports.mutations', 'athletes_id', 'Mutations')
    sanctions_ids = fields.One2many('sports.sanctions', 'athletes_id', 'Sanctions')
    anneeblanche_ids = fields.One2many('sports.anneeblanche', 'athletes_id', 'Années Blanches')

    doublon_ids = fields.One2many('sports.doublon', 'athletes_id', string='Doublons')

    age = fields.Integer(compute='_compute_age', string='Age', readonly=True, store=False, default=0,
                         track_visibility='onchange')

    state = fields.Selection([("draft", "Brouillon"), ("attente_activation", "Attente Activation"),
                              ("actif", "Actif"),
                              ("renouvellement", "Attente de Renouvellement "),
                              ("mutations", "Attente de Mutations "),
                              ("inactif", "Inactif"),
                              ("Rejete", "Rejeté"),
                              ("Sanctionne", "Sanctionné"),
                              ("nonConforme", "Non Conforme"),
                              ], 'Statut', readonly=False, copy=False, index=True, track_visibility='onchange',
                             default='draft')

    niveau_scolaire = fields.Selection([
        ('Primaire', 'Primaire'),
        ('College', 'Collége'),
        ('Secondaire', 'Secondaire'),
        ('Niveau bac', 'Niveau bac'),
        ('bachelier', 'Bachelier'),
        ('Bac2', 'Bac+2'),
        ('Bac3', 'Bac+3'),
        ('Bac4', 'Bac+4'),
        ('Bac5', 'Bac+5'),
        ('Plus', 'Plus')], string='Niveau scolaire')

    type_athletes = fields.Selection([('Sportif-Interne', 'Sportif-Interne'), ('Sportif-MRE', 'Sportif-MRE'),
                                      ('Sportif-Etranger', 'Sportif-Etranger')], string='Type Athlètes')

    # impression =  fields.Selection([('attente_impression', 'Attente d’impression'), ('Imprimee', 'Imprimée'),('Duplicata','Duplicata')], 'Impression Carte?', readonly=True, copy=False, index=True, track_visibility='onchange', default='attente_impression')

    assure = fields.Boolean(string='Assuré?', readonly=True)
    date_assure = fields.Datetime('Date Assurance', readonly=True)
    impression = fields.Boolean(string='Impression Carte?', readonly=True)
    date_impression = fields.Datetime('Date Impression carte', readonly=True)
    impression_duplicata = fields.Boolean(string='Impression Duplicata?')

    url = fields.Char(string='URL Image')

    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
                          )

    image1 = fields.Binary("Photo 1", attachment=True,
                           help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
                           )

    image2 = fields.Binary("Photo 2", attachment=True,
                           help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
                           )

    image3 = fields.Binary("Photo 3", attachment=True,
                           help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
                           )

    image4 = fields.Binary("Photo 4", attachment=True,
                           help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
                           )

    image_medium = fields.Binary("Medium-sized image",
                                 compute='_compute_images', inverse='_inverse_image_medium', store=True,
                                 attachment=True,
                                 help="Medium-sized image of this contact. It is automatically " \
                                      "resized as a 128x128px image, with aspect ratio preserved. " \
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image",
                                compute='_compute_images', inverse='_inverse_image_small', store=True, attachment=True,
                                help="Small-sized image of this contact. It is automatically " \
                                     "resized as a 64x64px image, with aspect ratio preserved. " \
                                     "Use this field anywhere a small image is required.")

    category_age_change = fields.Boolean(string='Catégorie d\'âge?')

    report_xml_id = fields.Many2one('ir.actions.report.xml', 'Report XML', )

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = 'Nouveau'
        if vals['cin']:
            a = self.env['sports.athletes'].search([('cin', '=', vals['cin']), ('state', '!=', 'nonConforme')])
            if len(a) == 1 or len(a) > 1:
                raise ValidationError("Le numéro de CIN est déja utilisé")
        result = super(SportsAthletes, self).create(vals)
        return result

    @api.depends('image')
    def _compute_images(self):
        for rec in self:
            rec.image_medium = tools.image_resize_image_medium(rec.image)
            rec.image_small = tools.image_resize_image_small(rec.image)

    def _inverse_image_medium(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_medium)

    def _inverse_image_small(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_small)

    @api.multi
    def action_view_mutations(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('sports_athletic.action_view_mutations_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }

        mutations_ids = sum([order.mutations_ids.ids for order in self], [])

        if len(mutations_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, mutations_ids)) + "])]"
        elif len(mutations_ids) == 1:
            form = self.env.ref('sports_athletic.view_mutations_form', False)
            form_id = form.id if form else False
            tree = self.env.ref('sports_athletic.view_mutations_tree', False)
            tree_id = tree.id if tree else False
            result['views'] = [(tree_id, 'tree'), (form_id, 'form')]
            result['res_id'] = mutations_ids[0]
        return result

    @api.multi
    def action_nonconforme(self):

        self.write({'state': 'nonConforme'})

    @api.one
    def action_surclasse(self):
        self.write({'surclassement': 'surclasse'})

    @api.multi
    def action_non_surclasse(self):

        for order in self:
            if order.category_age_id:
                newcategory_age = int(order.category_age_id.order) - 1
            else:
                newcategory_age = 0
        a = self.env['sports.category_age'].search([('order', '=', newcategory_age)])
        self.category_age_id = a

        self.write({'surclassement': 'non_surclasse'})

    @api.multi
    def action_category_age(self):

        athletes = self.env['sports.athletes'].search([('id', '>', 0)])

        for athlete in athletes:

            if self.env['sports.category_age'].search(
                    [('age_debut', '<=', athlete.age), ('age_fin', '>=', athlete.age)]):
                athlete.category_age_id = self.env['sports.category_age'].search(
                    [('age_debut', '<=', self.age), ('age_fin', '>=', self.age)])

        return True

    @api.multi
    def action_force(self):
        self.write({'force': True})

    @api.multi
    def action_reaffiliations(self):
        for order in self:
            if order.category_age_id:
                newcategory_age = int(order.category_age_id.order) + 1
            else:
                newcategory_age = 0
        a = self.env['sports.category_age'].search([('order', '=', newcategory_age)])
        self.category_age_id = a
        self.write({'surclassement': 'surclasse'})

    @api.multi
    def action_view_reaffiliations(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('sports_athletic.action_view_reaffiliationathletes_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }

        reaffiliation_ids = sum([order.reaffiliation_ids.ids for order in self], [])

        if len(reaffiliation_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, reaffiliation_ids)) + "])]"
        elif len(reaffiliation_ids) == 1:
            form = self.env.ref('sports_athletic.view_reaffiliationathletes_form', False)
            form_id = form.id if form else False
            tree = self.env.ref('sports_athletic.view_reaffiliationathletes_tree', False)
            tree_id = tree.id if tree else False
            result['views'] = [(tree_id, 'tree'), (form_id, 'form')]
            result['res_id'] = reaffiliation_ids[0]
        return result

    @api.multi
    def action_view_sanctions(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('sports_athletic.action_view_sanctions_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }

        sanctions_ids = sum([order.sanctions_ids.ids for order in self], [])

        if len(sanctions_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, sanctions_ids)) + "])]"
        elif len(sanctions_ids) == 1:
            form = self.env.ref('sports_athletic.view_sanctions_form', False)
            form_id = form.id if form else False
            tree = self.env.ref('sports_athletic.view_sanctions_tree', False)
            tree_id = tree.id if tree else False
            result['views'] = [(tree_id, 'tree'), (form_id, 'form')]
            result['res_id'] = sanctions_ids[0]
        return result

    @api.multi
    def action_view_anneeblanche(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('sports_athletic.action_view_anneeblanche_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }

        anneeblanche_ids = sum([order.anneeblanche_ids.ids for order in self], [])

        if len(anneeblanche_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, anneeblanche_ids)) + "])]"
        elif len(anneeblanche_ids) == 1:
            form = self.env.ref('sports_athletic.view_anneeblanche_form', False)
            form_id = form.id if form else False
            tree = self.env.ref('sports_athletic.view_anneeblanche_tree', False)
            tree_id = tree.id if tree else False
            result['views'] = [(tree_id, 'tree'), (form_id, 'form')]
            result['res_id'] = anneeblanche_ids[0]
        return result

    @api.multi
    def generate_report(self):

        report_ids = self.env['ir.actions.report.xml'].search([('report_type', '=', 'aeroo'),
                                                               ('model', '=', 'sports.athletes'),
                                                               ('report_name', '=', 'sports_report')])
        return self.env['report'].get_action(
            self, report_ids.report_name)

    @api.multi
    def generate_attestation_athlete_report(self):

        report_ids = self.env['ir.actions.report.xml'].search([('report_type', '=', 'aeroo'),
                                                               ('model', '=', 'sports.athletes'), ('report_name', '=',
                                                                                                   'sports_attestation_athlete_report')])
        return self.env['report'].get_action(
            self, report_ids.report_name)

    @api.multi
    def generate_attestation_bourse_athlete_report(self):

        report_ids = self.env['ir.actions.report.xml'].search([('report_type', '=', 'aeroo'),
                                                               ('model', '=', 'sports.athletes'), ('report_name', '=',
                                                                                                   'sports_attestation_de_bourse_report')])
        return self.env['report'].get_action(
            self, report_ids.report_name)

    @api.multi
    def generate_carte_report_duplicata(self):
        self.impression_duplicata = True
        report_ids = self.env['ir.actions.report.xml'].search([('report_type', '=', 'aeroo'),
                                                               ('model', '=', 'sports.athletes'),
                                                               ('report_name', '=', 'carte_report')])
        return self.env['report'].get_action(
            self, report_ids.report_name)


    @api.multi
    def generate_carte_report(self):

        report_ids = self.env['ir.actions.report.xml'].search([('report_type', '=', 'aeroo'),
                                                               ('model', '=', 'sports.athletes'),
                                                               ('report_name', '=', 'carte_report')])
        return self.env['report'].get_action(
            self, report_ids.report_name)


####Doublon

class doublon(models.Model):
    _name = "sports.doublon"

    athletes_id = fields.Many2one('sports.athletes', string='Athlete')

    prenom = fields.Char(related='athletes_id.prenom', store=True)

    name_ar = fields.Char(related='athletes_id.name_ar', store=True)

    name_at = fields.Char(related='athletes_id.name_at', store=True)

    image = fields.Binary(related='athletes_id.image', attachment=True, store=True)

    image_medium = fields.Binary("Medium-sized image",
                                 compute='_compute_images', inverse='_inverse_image_medium', store=True,
                                 attachment=True,
                                 help="Medium-sized image of this contact. It is automatically " \
                                      "resized as a 128x128px image, with aspect ratio preserved. " \
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image",
                                compute='_compute_images', inverse='_inverse_image_small', store=True, attachment=True,
                                help="Small-sized image of this contact. It is automatically " \
                                     "resized as a 64x64px image, with aspect ratio preserved. " \
                                     "Use this field anywhere a small image is required.")

    name_pere = fields.Char(related='athletes_id.name_pere', store=True)
    name_mere = fields.Char(related='athletes_id.name_mere', store=True)
    datenaissance = fields.Date(related='athletes_id.datenaissance', store=True)
    state = fields.Selection(related='athletes_id.state', store=True)
    name = fields.Char(related='athletes_id.name', store=True)

    @api.depends('image')
    def _compute_images(self):
        for rec in self:
            rec.image_medium = tools.image_resize_image_medium(rec.image)
            rec.image_small = tools.image_resize_image_small(rec.image)

    def _inverse_image_medium(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_medium)

    def _inverse_image_small(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_small)


##### Sanctions

class SportsSanctions(models.Model):
    _name = "sports.sanctions"
    _description = "Sanctions"

    @api.model
    def _get_default_saison(self):

        return self.env['sports.saison'].search([('state', '=', 'active')])

    name = fields.Char('N° Sanction', copy=False, readonly=True, index=True, default='Nouveau')
    ligue_id = fields.Many2one('sports.ligue', string='Ligue')
    club_id = fields.Many2one('sports.club', string='Club')
    saison_id = fields.Many2one('sports.saison', string='Saison sportive', default=_get_default_saison)
    athletes_id = fields.Many2one('sports.athletes', 'N° Licence')

    responsable_id = fields.Many2one('res.users', string='Responsable', index=True, track_visibility='onchange',
                                     default=lambda self: self.env.user)
    date_create = fields.Datetime(string='Date de Création', copy=False, default=fields.Datetime.now)

    statut_sanction = fields.Selection(
        [('none', ''), ('en_attente', 'En Attente'), ('sanctionne', u'''Sanctionné'''), ('annulee', u'''Annlée''')],
        'Statut Sanction', readonly=True, default='en_attente')
    state = fields.Selection(
        [('attente_envoi_demande', 'Attente d\'envoi'), ('attente_verif_csrl', 'Attente de Vérification (CSRL)'),
         ('attente_decision_comm', 'Attente de la Décision de la Commission Disciplinaire'),
         ('athlete_sanctionne', 'Sanctionné'), ('sanction_annulee', 'Annulée')], 'Statut', readonly=True,
        default='attente_envoi_demande')

    user_attente_envoi_demande = fields.Many2one('res.users', 'Envoi de la demande de Sanction Par', readonly=True)
    date_attente_envoi_demande = fields.Datetime('Fait le', readonly=True)
    user_attente_verif_csrl = fields.Many2one('res.users', 'Vérification de la Demande par la CSRL Par', readonly=True)
    date_attente_verif_csrl = fields.Datetime('Fait le', readonly=True)
    user_attente_decision_comm = fields.Many2one('res.users', 'Décision de la Commission Disciplinaire Par',
                                                 readonly=True)
    date_attente_decision_comm = fields.Datetime('Fait le', readonly=True)
    type_sanction = fields.Selection(
        [('none', ''), ('financiere', 'Financière'), ('arret', 'Arrét'), ('avertissement', 'Avertissement')],
        'Type de Sanctions', required=True)

    sanction = fields.Binary('Demande Sanction Format Electronique')
    sanction_filename = fields.Char("Demande Sanction Format Electronique Filename")

    sanction2 = fields.Binary('Sanction Format Electronique')
    sanction2_filename = fields.Char("Sanction Format Electronique Filename")

    date_dec_sanction = fields.Date('Date Décision', copy=False, default=fields.Datetime.now)
    date_start_sanction_csrl = fields.Date('Date Début Effet')
    date_end_sanction_csrl = fields.Date('Date Fin Effet')
    decision_csrl = fields.Selection([('none', ''), ('conforme', 'Conforme'), ('non_conforme', 'Non Conforme')],
                                     'Statut', readonly=False)
    motif = fields.Text("Motif")
    comment_csrl = fields.Text("Commentaire")
    duration_csrl = fields.Integer("Durée")
    unite_csrl = fields.Selection(
        [('none', ''), ('day', u'''Jour'''), ('week', u'''Semaine'''), ('year', u'''Année''')], 'Unité', readonly=False)
    date_start_sanction_comm = fields.Date('Date Début Effet')
    date_end_sanction_comm = fields.Date('Date Fin Effet')
    decision_comm = fields.Selection([('none', ''), ('conforme', 'Conforme'), ('non_conforme', 'Non Conforme')],
                                     'Statut', readonly=False)
    comment_comm = fields.Text("Commentaire")
    duration_comm = fields.Integer("Durée")
    unite_comm = fields.Selection([('none', ''), ('day', 'Jour'), ('week', 'Semaine'), ('year', u'''Année''')], 'Unité',
                                  readonly=False)

    @api.onchange('athletes_id')
    def onchange_athletes_id(self):
        if self.athletes_id:
            if self.athletes_id.club_id:
                self.club_id = self.athletes_id.club_id.id
                if self.athletes_id.club_id.ligue_id:
                    self.ligue_id = self.athletes_id.club_id.ligue_id.id
        else:
            self.club_id = False
            self.ligue_id = False

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sports.sanctions')
        print vals['name']
        result = super(SportsSanctions, self).create(vals)
        return result

    @api.one
    def action_sanctions_validate(self):
        self.write({'state': 'attente_verif_csrl',
                    'user_attente_envoi_demande': self.env.uid,
                    'date_attente_envoi_demande': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),})

    @api.one
    def action_sanctions_validate_csrl(self):
        self.write({'state': 'attente_decision_comm',
                    'user_attente_verif_csrl': self.env.uid,
                    'date_attente_verif_csrl': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    })

    @api.one
    def action_sanctions_validate_commission(self):
        self.write({'state': 'athlete_sanctionne',
                    'user_attente_decision_comm': self.env.uid,
                    'date_attente_decision_comm': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    })
        self.athletes_id.write({'state': 'Sanctionne'})

    @api.one
    def action_sanctions_effectuee(self):
        self.write({'state': 'athlete_sanctionne'})
        self.athletes_id.write({'state': 'Sanctionne'})


##### Mutations

class SportsMutations(models.Model):
    _name = "sports.mutations"
    _description = "Mutations"

    @api.onchange('athletes_id', 'club_giving_id', 'ligue_id')
    def _ligue_id(self):

        for order in self:
            a = self.env['sports.club'].search([('id', '=', order.athletes_id.club_id.id)])
            order.club_giving_id = a
            b = self.env['sports.ligue'].search([('id', '=', order.athletes_id.ligue_id.id)])
            order.ligue_id = b

    @api.model
    def _get_default_saison(self):

        return self.env['sports.saison'].search([('state', '=', 'active')])

    @api.onchange('athletes_id', 'club_giving_id', 'club_receiving_id')
    def _club_id(self):

        for order in self:
            if self.club_receiving_id and self.club_giving_id:
                if self.club_receiving_id == self.club_giving_id:
                    # raise ValidationError("Il faut que le club Cédant est différent du club Recevant")
                    raise ValidationError("Il faut que le club Cédant est différent du club Recevant'")
                    print "ici"
                else:
                    print "ok"

                    # zoubida onchange pour nom et prenom


    @api.onchange('athletes_id')
    def _change_nom_prenom(self):
        self.name_at = self.env['sports.athletes'].search([('name', '=', self.athletes_id.name)]).name_at
        self.prenom = self.env['sports.athletes'].search([('name', '=', self.athletes_id.name)]).prenom

    name = fields.Char('N° Mutation', required=True, copy=False, readonly=True, index=True, default='Nouveau')
    ligue_id = fields.Many2one('sports.ligue', string='Ligue', track_visibility='onchange')

    # zoubida: ajout de nom et prenom athlete onchange

    prenom = fields.Char(string='Prénom', track_visibility='onchange', readonly = True)
    name_at = fields.Char(string='Nom', track_visibility='onchange', readonly = True)

    club_giving_id = fields.Many2one('sports.club', 'Club Cédant', required=True, track_visibility='onchange')
    club_receiving_id = fields.Many2one('sports.club', 'Club Recevant', required=True, track_visibility='onchange')

    saison_id = fields.Many2one('sports.saison', string='Saison sportive', default=_get_default_saison)
    athletes_id = fields.Many2one('sports.athletes', 'N° Licence')

    date_dec_mutation = fields.Date('Date Mutation', copy=False, default=fields.Datetime.now)

    mutation = fields.Binary('Demande Mutation Format Electronique')
    mutation_filename = fields.Char("Demande Mutation Format Electronique Filename")

    mutation2 = fields.Binary('Mutation Format Electronique')
    mutation2_filename = fields.Char("Mutation Format Electronique Filename")

    condition_ids = fields.One2many('sports.mutation.condition', 'mutation_id', 'Conditions')
    decision_commission = fields.Selection([('none', ''), ('conforme', 'Conforme'), ('non_conforme', 'Non Conforme')],
                                           'Statut', readonly=False)
    motif = fields.Text("Motif")
    statut_mutation = fields.Selection(
        [('none', ''), ('en_cours', 'En cours'), ('mute', u'''Muté'''), ('annulee', u'''Annlée''')], 'Statut Mutation',
        readonly=True)
    state = fields.Selection(
        [('dem_attente_envoi', 'Attente Envoi'), ('dem_attente_val', 'Attente de Validation par la CSRL'),
         ('mutation_effectuee', 'Mutation Effectuée'), ('mutation_annulee', 'Mutation Annulée'),
         ('reaffiliation', 'Réaffiliation')], 'Statut', readonly=True, default='dem_attente_envoi')
    user_dem_attente_envoi = fields.Many2one('res.users', 'Par', readonly=True)
    date_dem_attente_envoi = fields.Datetime('Fait le', readonly=True)
    user_dem_attente_val = fields.Many2one('res.users', 'Par', readonly=True)
    date_dem_attente_val = fields.Datetime('Fait le', readonly=True)
    reaffiliation_id = fields.Many2one('sports.reaffiliation', string='Réaffiliation')

    responsable_id = fields.Many2one('res.users', string='Responsable', index=True, track_visibility='onchange',
                                     default=lambda self: self.env.user)
    date_create = fields.Datetime(string='Date de Création', copy=False, default=fields.Datetime.now)

    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].next_by_code('sports.mutations')
        result = super(SportsMutations, self).create(vals)
        return result

    @api.multi
    def action_dem_attente_val(self):
        self.write({'state': 'dem_attente_val'})

    @api.multi
    def action_mutation_annulee(self):
        self.write({'state': 'mutation_annulee'})

    @api.multi
    def action_mutation_effectuee(self):
        self.write({'state': 'mutation_effectuee'})
        self.athletes_id.write({'state': 'mutations'})

    @api.multi
    def create_reaffiliation(self):

        reaffiliation = self.env['sports.reaffiliation']
        athletes = self.env['sports.athletes']
        reaffiliation = reaffiliation.create({
            'name': self.env['ir.sequence'].next_by_code('sports.athletes.reaffiliation'),
            'club_id': self.club_receiving_id.id,
            'ligue_id': self.club_receiving_id.ligue_id.id,
            'athletes3_ids': [(6, 0, [x.id for x in self.athletes_id])],
        })
        self.write({'reaffiliation_id': reaffiliation.id, 'state': 'reaffiliation'})


####Code de la Condition Mutations

class MutationsConditionCode(models.Model):
    _name = "sports.mutation.code.condition"

    name = fields.Char(string='Code de la Condition')


####Condition Mutations

class MutationsCondition(models.Model):
    _name = "sports.mutation.condition"

    libelle_condition = fields.Char(string='Libelle de la Condition')
    valide = fields.Boolean(string='Valide')
    mutation_id = fields.Many2one('sports.mutations', 'Mutation', readonly=True)
    condition_id = fields.Many2one('sports.mutation.code.condition', 'Code de la Condition', readonly=True)


##### Année blanche

class SportsAnneeblanche(models.Model):
    _name = "sports.anneeblanche"
    _description = "Annee blanche"

    @api.onchange('athletes_id', 'club_giving_id', 'ligue_id')
    def _ligue_id(self):
        for order in self:
            a = self.env['sports.club'].search([('id', '=', order.athletes_id.club_id.id)])
            order.club_giving_id = a
            b = self.env['sports.ligue'].search([('id', '=', order.athletes_id.ligue_id.id)])
            order.ligue_id = b

    @api.model
    def _get_default_saison(self):
        return self.env['sports.saison'].search([('state', '=', 'active')])

    name = fields.Char('N° Année blanche', required=True, copy=False, readonly=True, index=True, default='Nouveau')
    ligue_id = fields.Many2one('sports.ligue', string='Ligue', track_visibility='onchange')

    club_id = fields.Many2one('sports.club', 'Club', required=True)

    saison_id = fields.Many2one('sports.saison', string='Saison sportive', default=_get_default_saison)
    athletes_id = fields.Many2one('sports.athletes', 'N° Licence')

    responsable_id = fields.Many2one('res.users', string='Responsable', index=True, track_visibility='onchange',
                                     default=lambda self: self.env.user)
    date_create = fields.Datetime(string='Date de Création', copy=False, default=fields.Datetime.now)

    state = fields.Selection(
        [('attente_envoi_demande', 'Attente d\'envoi'), ('attente_verif_csrl', 'Attente de Vérification (CSRL)'),
         ('attente_decision_comm', 'Attente de la Décision de la Commission Disciplinaire'),
         ('athlete_sanctionne', 'Année blanche'), ('sanction_annulee', 'Annulée')], 'Statut', readonly=True,
        default='attente_envoi_demande')

    user_attente_envoi_demande = fields.Many2one('res.users', 'Envoi de la demande  Par', readonly=True)
    date_attente_envoi_demande = fields.Datetime('Fait le', readonly=True)
    user_attente_verif_csrl = fields.Many2one('res.users', 'Vérification de la Demande par la CSRL Par', readonly=True)
    date_attente_verif_csrl = fields.Datetime('Fait le', readonly=True)
    user_attente_decision_comm = fields.Many2one('res.users', 'Décision de la Commission Disciplinaire Par',
                                                 readonly=True)
    date_attente_decision_comm = fields.Datetime('Fait le', readonly=True)

    sanction2 = fields.Binary('Sanction Format Electronique')
    sanction2_filename = fields.Char("Sanction Format Electronique Filename")

    date_dec_sanction = fields.Date('Date Décision', copy=False, default=fields.Datetime.now)
    date_start_sanction_csrl = fields.Date('Date Début Effet')
    date_end_sanction_csrl = fields.Date('Date Fin Effet')
    decision_csrl = fields.Selection([('none', ''), ('conforme', 'Conforme'), ('non_conforme', 'Non Conforme')],
                                     'Statut', readonly=False)
    motif = fields.Text("Motif")
    comment_csrl = fields.Text("Commentaire")
    duration_csrl = fields.Integer("Durée")
    unite_csrl = fields.Selection(
        [('none', ''), ('day', u'''Jour'''), ('week', u'''Semaine'''), ('year', u'''Année''')], 'Unité', readonly=False)
    date_start_sanction_comm = fields.Date('Date Début Effet')
    date_end_sanction_comm = fields.Date('Date Fin Effet')
    decision_comm = fields.Selection([('none', ''), ('conforme', 'Conforme'), ('non_conforme', 'Non Conforme')],
                                     'Statut', readonly=False)
    comment_comm = fields.Text("Commentaire")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sports.anneeblanche')
        result = super(SportsMutations, self).create(vals)
        return result

    @api.multi
    def action_anneeblanche_effectuee(self):
        self.write({'state': 'athlete_sanctionne'})
        self.athletes_id.write({'state': 'Sanctionne'})


####Edition des Assurances







class EditionAssurances(models.Model):
    _name = "sports.edition.assurances"

    @api.model
    def _get_default_saison(self):

        return self.env['sports.saison'].search([('state', '=', 'active')])

    @api.model
    def _get_nombre_attribution(self):
        val = 0
        param = self.env['sports.print_assurance'].search([('active', '=', True)])
        if param:
            val = param.name
        return val

    @api.model
    def _get_nombre_renouvellement(self):
        val = 0
        param = self.env['sports.print_assurance'].search([('active', '=', True)])
        if param:
            val = param.renouvellement
        return val

    @api.model
    def _get_nombre_reaffiliation(self):
        val = 0
        param = self.env['sports.print_assurance'].search([('active', '=', True)])
        if param:
            val = param.reaffiliation
        return val

    name = fields.Char(string='Référence', default='/')
    date = fields.Date('Date', copy=False, default=fields.Datetime.now, readonly=True)

    # Zoubida modifier les états
    state = fields.Selection([('draft', 'Brouillon'), ('en_cours', u'''Athlétes cherchés'''), ('valide', 'Validé'),
                              ('annulee', u'''Annlée''')],
                             'Etat', readonly=True, default='draft')

    format_imp = fields.Selection([('Excel', 'Excel'), ('PDF', 'PDF')], 'Format', readonly=False)

    # Zoubida : athletes

    athletes3_att_ids = fields.One2many('sports.athletes.assurances', 'assurances_id', string='Athlètes',
                                        domain=[('situation_etat', '=', 'Attribution')], readonly=True)
    athletes3_ren_ids = fields.One2many('sports.athletes.assurances', 'assurances_id', string='Athlètes',
                                        domain=[('situation_etat', '=', 'Renouvellement')], readonly=True)
    athletes3_reaf_ids = fields.One2many('sports.athletes.assurances', 'assurances_id', string='Athlètes',
                                         domain=[('situation_etat', '=', 'Reaffiliations')], readonly=True)

    responsable_id = fields.Many2one('res.users', string='Responsable', index=True, track_visibility='onchange',
                                     default=lambda self: self.env.user)
    saison_id = fields.Many2one('sports.saison', string='Saison sportive', default=_get_default_saison)

    nombre_attribution = fields.Integer(string='Nombre des athlètes en attribution',
                                        default=_get_nombre_attribution)
    nombre_renouvellement = fields.Integer(string='Nombre des athlètes en renouvellement',
                                           default=_get_nombre_renouvellement)
    nombre_reaffiliation = fields.Integer(string='Nombre des athlètes en reaffiliation',
                                          default=_get_nombre_reaffiliation)
    # Zoubida: fields imprime et assure avec computes

    is_assure = fields.Boolean('Assuré', default=False, compute='_compute_is_assure')

    @api.multi
    def _compute_is_assure(self):
        assure_att = False
        assure_ren = False
        assure_reaf = False

        if not self.athletes3_ren_ids and not self.athletes3_reaf_ids and not self.athletes3_att_ids:
            self.is_assure = False
        else:

            if self.athletes3_att_ids:
                for obj in self.athletes3_att_ids:
                    if obj.athletes_id.assure:
                        assure_att = True
                    else:
                        assure_att = False
            else:
                assure_att = True

            if self.athletes3_ren_ids:
                for obj in self.athletes3_ren_ids:
                    if obj.athletes_id.assure:
                        assure_ren = True
                    else:
                        assure_ren = False
            else:
                assure_ren = True

            if self.athletes3_reaf_ids:
                for obj in self.athletes3_reaf_ids:
                    if obj.athletes_id.assure:
                        assure_reaf = True
                    else:
                        assure_reaf = False
            else:
                assure_reaf = True

            if assure_att and assure_ren and assure_reaf:
                self.is_assure = True
            else:
                self.is_assure = False

    # Zoubida: enlever le changement du field assure, et ajout du changement de state

    @api.multi
    def action_verification(self):
        if not self.athletes3_att_ids and not self.athletes3_reaf_ids and not self.athletes3_ren_ids:

            c = 0
            nombre_attribution = self.nombre_attribution
            athletes_ids = self.env['sports.athletes'].search([('assure', '=', False), ('situation_etat', '=', "Attribution")])
            for athlete in athletes_ids:
                if c < nombre_attribution:
                    c = c + 1
                    self.env['sports.athletes.assurances'].create(
                        {'athletes_id': athlete.id, 'assurances_id': self.id, 'ligue_id': athlete.ligue_id.id,
                         'club_id': athlete.club_id.id, 'nom': athlete.name_at, 'prenom': athlete.prenom,
                         'sequence': c})

            c = 0
            nombre_renouvellement = self.nombre_renouvellement
            athletes_ids = self.env['sports.athletes'].search(
                [('assure', '=', False), ('situation_etat', '=', "Renouvellement")])
            for athlete in athletes_ids:
                if c < nombre_renouvellement:
                    c = c + 1
                    self.env['sports.athletes.assurances'].create(
                        {'athletes_id': athlete.id, 'assurances_id': self.id, 'ligue_id': athlete.ligue_id.id,
                         'club_id': athlete.club_id.id, 'nom': athlete.name_at, 'prenom': athlete.prenom,
                         'sequence': c})

            c = 0
            nombre_reaffiliation = self.nombre_reaffiliation
            athletes_ids = self.env['sports.athletes'].search(
                [('assure', '=', False), ('situation_etat', '=', "Reaffiliations")])
            for athlete in athletes_ids:
                if c < nombre_reaffiliation:
                    c = c + 1
                    self.env['sports.athletes.assurances'].create(
                        {'athletes_id': athlete.id, 'assurances_id': self.id, 'ligue_id': athlete.ligue_id.id,
                         'club_id': athlete.club_id.id, 'nom': athlete.name_at, 'prenom': athlete.prenom,
                         'sequence': c})


            if self.athletes3_att_ids or self.athletes3_ren_ids or self.athletes3_reaf_ids:
                self.state = 'en_cours'

    # Zoubida: validation assurance

    @api.multi
    def action_valider(self):
        if self.athletes3_att_ids or self.athletes3_reaf_ids or self.athletes3_ren_ids:

            for athlete_att in self.athletes3_att_ids:
                athlete_att.athletes_id.assure = True
                athlete_att.athletes_id.date_assure = self.date
            for athlete_reaf in self.athletes3_reaf_ids:
                athlete_reaf.athletes_id.assure = True
                athlete_reaf.athletes_id.date_assure = self.date
            for athlete_ren in self.athletes3_ren_ids:
                athlete_ren.athletes_id.assure = True
                athlete_ren.athletes_id.date_assure = self.date
        self.state = 'valide'

    # Zoubida: annuler assurance

    @api.multi
    def action_annuler(self):
        if self.athletes3_att_ids or self.athletes3_reaf_ids or self.athletes3_ren_ids:

            for athlete_att in self.athletes3_att_ids:
                athlete_att.athletes_id.assure = False
            for athlete_reaf in self.athletes3_reaf_ids:
                athlete_reaf.athletes_id.assure = False
            for athlete_ren in self.athletes3_ren_ids:
                athlete_ren.athletes_id.assure = False
        self.state = 'annulee'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sports.edition.assurances')
        result = super(EditionAssurances, self).create(vals)
        return result


####Assurances  Excel
class EditionAssurancesExcel(models.Model):
    _name = "sports.excel.assurances"

    @api.model
    def _get_default_saison(self):

        return self.env['sports.saison'].search([('state', '=', 'active')])

    name = fields.Char(string='Référence', default='/')
    state = fields.Selection([('en_cours', 'En cours'), ('valide', 'Validé'), ('annulee', u'''Annlée''')], 'Etat',
                             readonly=True, default='en_cours')

    recherche = fields.Selection([('date', 'Par Date'), ('tous', 'Tous')], 'Impression', default='tous')

    date_start = fields.Date('Date début', copy=False)
    date_end = fields.Date('Date Fin', copy=False)

    assurances_ids = fields.One2many('sports.athletes.assurances', 'assurances_excel_id', string='Athlétes')

    saison_id = fields.Many2one('sports.saison', string='Saison sportive', default=_get_default_saison)

    @api.onchange('recherche')
    def onchange_recherche(self):
        if self.recherche == "tous":
            self.date_start = False
            self.date_end = False

    @api.multi
    def generate_carte_report(self):

        report_ids = self.env['ir.actions.report.xml'].search([('report_type', '=', 'aeroo'),
                                                               ('model', '=', 'sports.excel.assurances'),
                                                               ('report_name', '=', 'report_assurance_ods3')])
        return self.env['report'].get_action(
            self, report_ids.report_name)

    @api.multi
    def action_verification(self):
        self.assurances_ids = False
        if self.recherche == "date":
            athletes_ids = self.env['sports.athletes.assurances'].search([('date', '>=', self.date_start),
                                                                          ('date', '<=', self.date_end)])
        else:
            athletes_ids = self.env['sports.athletes.assurances'].search([])

        for athlete in athletes_ids:
            athlete.write({'assurances_excel_id': self.id})

        return True

    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].next_by_code('sports.excel.assurances')
        result = super(EditionAssurancesExcel, self).create(vals)
        return result


#### athletes Assuré

class EditionAssurancesAthletes(models.Model):
    _name = "sports.athletes.assurances"

    name = fields.Char(string='Référence', invisible=True)

    athletes_id = fields.Many2one('sports.athletes', 'N° Licence', readonly=True)
    ligue_id = fields.Many2one('sports.ligue', string='Ligue', readonly=True)
    club_id = fields.Many2one('sports.club', 'Club', readonly=True)
    sequence = fields.Integer(string='séquence')

    nom = fields.Char(string='Nom')
    prenom = fields.Char(string='Prénom')

    assurances_id = fields.Many2one('sports.edition.assurances', 'Assurances', invisible=True)
    assurances_excel_id = fields.Many2one('sports.excel.assurances', 'Assurances', invisible=True)

    date = fields.Date(string='Date Assurances',
                       related='assurances_id.date')

    situation_etat = fields.Selection(string='Situation',
                                      related='athletes_id.situation_etat')


#####Edition des Cartes Licences


class EditionCartesLicences(models.Model):
    _name = "sports.edition.carteslicences"

    @api.model
    def _get_default_saison(self):

        return self.env['sports.saison'].search([('state', '=', 'active')])

    @api.model
    def _get_nombre_attribution(self):
        val = 0
        param = self.env['sports.print_carte'].search([('active', '=', True)])
        if param:
            val = param.name
        return val

    @api.model
    def _get_nombre_renouvellement(self):
        val = 0
        param = self.env['sports.print_carte'].search([('active', '=', True)])
        if param:
            val = param.renouvellement
        return val

    @api.model
    def _get_nombre_reaffiliation(self):
        val = 0
        param = self.env['sports.print_carte'].search([('active', '=', True)])
        if param:
            val = param.reaffiliation
        return val

    name = fields.Char(string='Référence', default='/')
    date = fields.Datetime('Date de création', copy=False, default=fields.Datetime.now, readonly=True)
    # Zoubida modifier les états
    state = fields.Selection([('draft', 'Brouillon'), ('en_cours', u'''Athlétes cherchés'''), ('valide', 'Validé'),
                              ('annulee', u'''Annlée''')],
                             'Etat', readonly=True, default='draft')

    nombre_attribution = fields.Integer(string='Nombre des athlètes en attribution',
                                        default=_get_nombre_attribution)
    nombre_renouvellement = fields.Integer(string='Nombre des athlètes en renouvellement',
                                           default=_get_nombre_renouvellement)
    nombre_reaffiliation = fields.Integer(string='Nombre des athlètes en reaffiliation',
                                          default=_get_nombre_reaffiliation)

    #athletes3_ids = fields.One2many('sports.athletes.carteslicences', 'carteslicences_id', string='Athlétes')


    # Zoubida : athletes

    athletes3_att_ids = fields.One2many('sports.athletes.carteslicences', 'carteslicences_id', string='Athlétes',
                                        domain=[('situation_etat', '=', 'Attribution')], readonly=True)
    athletes3_ren_ids = fields.One2many('sports.athletes.carteslicences', 'carteslicences_id', string='Athlétes',
                                        domain=[('situation_etat', '=', 'Renouvellement')], readonly=True)
    athletes3_reaf_ids = fields.One2many('sports.athletes.carteslicences', 'carteslicences_id', string='Athlétes',
                                         domain=[('situation_etat', '=', 'Reaffiliations')], readonly=True)

    responsable_id = fields.Many2one('res.users', string='Responsable', index=True, track_visibility='onchange',
                                     default=lambda self: self.env.user)

    saison_id = fields.Many2one('sports.saison', string='Saison sportive', default=_get_default_saison)

    # Zoubida : fields pour filtrer

    licence_athlete = fields.Boolean('Athléte', default=False)
    licence_entraineur = fields.Boolean('Entraineur', default=False)
    licence_dirigeant = fields.Boolean('Dirigeant', default=False)
    licence_officiel = fields.Boolean('Officiel', default=False)

    type_sportif_interne = fields.Boolean('Sportif-Interne', default=False)
    type_sportif_etranger = fields.Boolean('Sportif-Etranger', default=False)
    type_sportif_mre = fields.Boolean('Sportif-MRE', default=False)

    category_age_change = fields.Boolean(string='Catégorie d\'âge?', default=False)

    # Zoubida: fields imprime avec computes

    is_imprime = fields.Boolean('Imprimé', default=False, compute='_compute_is_imprime')

    @api.multi
    def _compute_is_imprime(self):
        imprime_att = False
        imprime_ren = False
        imprime_reaf = False

        if not self.athletes3_ren_ids and not self.athletes3_reaf_ids and not self.athletes3_att_ids:
            self.is_imprime = False
        else:

            if self.athletes3_att_ids:
                for obj in self.athletes3_att_ids:
                    if obj.athletes_id.impression:
                        imprime_att = True
                    else:
                        imprime_att = False
            else:
                imprime_att = True

            if self.athletes3_ren_ids:
                for obj in self.athletes3_ren_ids:
                    if obj.athletes_id.impression:
                        imprime_ren = True
                    else:
                        imprime_ren = False
            else:
                imprime_ren = True

            if self.athletes3_reaf_ids:
                for obj in self.athletes3_reaf_ids:
                    if obj.athletes_id.impression:
                        imprime_reaf = True
                    else:
                        imprime_reaf = False
            else:
                imprime_reaf = True

            if imprime_att and imprime_ren and imprime_reaf:
                self.is_imprime = True
            else:
                self.is_imprime = False

    # @api.multi
    # def action_verification(self):
    #             if not self.athletes3_ids:
    #
    #                 athletes_ids = self.env['sports.athletes'].search([('impression', '=', False)])
    #
    #                 k = 0
    #                 nombre_cartes = self.nombre_cartes
    #
    #                 for athlete in athletes_ids:
    #
    #                     if k < nombre_cartes:
    #                         k = k + 1
    #                     self.env['sports.athletes.carteslicences'].create(
    #                         {'athletes_id': athlete.id, 'carteslicences_id': self.id, 'ligue_id': athlete.ligue_id.id,
    #                          'club_id': athlete.club_id.id, 'nom': athlete.name_at, 'prenom': athlete.prenom,
    #                          'sequence': k})
    #
    #                     athlete.impression = True
    #                     athlete.date_impression = self.date
    #             else:
    #                 return True
    #
    #
    #
    #
    #


    # Zoubida: enlever le changement du field impression, et ajout du changement de state, avec application des filtres avec combinaisons possible

    @api.multi
    def action_verification(self):

        athletes_g_ids = self.env['sports.athletes']

        # licence_officiel = ''
        # licence_entraineur = ''
        # licence_dirigeant = ''
        # licence_athlete = ''
        # type_sportif_mre = ''
        # type_sportif_interne = ''
        # type_sportif_etranger = ''
        #
        # if self.type_sportif_etranger: type_sportif_etranger = 'Sportif-Etranger'
        # if self.type_sportif_interne: type_sportif_interne = 'Sportif-Interne'
        # if self.type_sportif_mre: type_sportif_mre = 'Sportif-MRE'
        #
        # if self.licence_officiel: licence_officiel = 'Officiel'
        # if self.licence_entraineur: licence_entraineur = 'Entraineur'
        # if self.licence_dirigeant: licence_dirigeant = 'Dirigeant'
        # if self.licence_athlete: licence_athlete = 'Athlete'


        if not self.athletes3_att_ids and not self.athletes3_reaf_ids and not self.athletes3_ren_ids:

            # athletes_ids = self.env['sports.athletes'].search([('impression', '=', False),'|','|',('licence', 'in', [licence_athlete,licence_entraineur,licence_officiel,licence_dirigeant]),
            #                                                    ('type_athletes', 'in', [type_sportif_interne,type_sportif_mre,type_sportif_etranger]),('category_age_change', '=', self.category_age_change)])

            athletes_ids = self.env['sports.athletes'].search([('impression', '=', False)])


            if self.licence_officiel:
                for a in athletes_ids:
                    if a.licence == 'Officiel':
                        athletes_g_ids += a
            if self.licence_entraineur:
                for a in athletes_ids:
                    if a.licence == 'Entraineur':
                        athletes_g_ids += a
            if self.licence_dirigeant:
                for a in athletes_ids:
                    if a.licence == 'Dirigeant':
                        athletes_g_ids += a
            if self.licence_athlete:
                if self.type_sportif_etranger:
                    for a in athletes_ids:
                        if a.type_athletes == 'Sportif-Etranger' and a.licence == 'Athlete':
                            athletes_g_ids += a
                elif self.type_sportif_interne:
                    for a in athletes_ids:
                        if a.type_athletes == 'Sportif-Interne' and a.licence == 'Athlete':
                            athletes_g_ids += a
                elif self.type_sportif_mre:
                    for a in athletes_ids:
                        if a.type_athletes == 'Sportif-MRE' and a.licence == 'Athlete':
                            athletes_g_ids += a
                elif not self.type_sportif_etranger and not self.type_sportif_interne and not self.type_sportif_mre:
                    for a in athletes_ids:
                        if a.licence == 'Athlete':
                            athletes_g_ids += a
            if self.category_age_change:
                for a in athletes_ids:
                    if a.category_age_change == True:
                        athletes_g_ids += a

            c = 0
            nombre_attribution = self.nombre_attribution
            athletes_ids = athletes_g_ids.search([('situation_etat', '=', "Attribution")])
            for athlete in athletes_ids:
                if c < nombre_attribution:
                    c = c + 1
                    self.env['sports.athletes.carteslicences'].create(
                        {'athletes_id': athlete.id, 'carteslicences_id': self.id, 'ligue_id': athlete.ligue_id.id,
                         'club_id': athlete.club_id.id, 'nom': athlete.name_at, 'prenom': athlete.prenom,
                         'sequence': c})

            c = 0
            nombre_renouvellement = self.nombre_renouvellement
            athletes_ids = athletes_g_ids.search([('situation_etat', '=', "Renouvellement")])
            for athlete in athletes_ids:
                if c < nombre_renouvellement:
                    c = c + 1
                    self.env['sports.athletes.carteslicences'].create(
                        {'athletes_id': athlete.id, 'carteslicences_id': self.id, 'ligue_id': athlete.ligue_id.id,
                         'club_id': athlete.club_id.id, 'nom': athlete.name_at, 'prenom': athlete.prenom,
                         'sequence': c})

            c = 0
            nombre_reaffiliation = self.nombre_reaffiliation
            athletes_ids = athletes_g_ids.search([('situation_etat', '=', "Reaffiliations")])
            for athlete in athletes_ids:
                if c < nombre_reaffiliation:
                    c = c + 1
                    self.env['sports.athletes.carteslicences'].create(
                        {'athletes_id': athlete.id, 'carteslicences_id': self.id, 'ligue_id': athlete.ligue_id.id,
                         'club_id': athlete.club_id.id, 'nom': athlete.name_at, 'prenom': athlete.prenom,
                         'sequence': c})

            if self.athletes3_att_ids or self.athletes3_ren_ids or self.athletes3_reaf_ids:
                self.state = 'en_cours'

                # Zoubida: validation impression

    @api.multi
    def action_valider(self):
        if self.athletes3_att_ids or self.athletes3_reaf_ids or self.athletes3_ren_ids:

            for athlete_att in self.athletes3_att_ids:
                athlete_att.athletes_id.impression = True
                athlete_att.athletes_id.date_impression = self.date
            for athlete_reaf in self.athletes3_reaf_ids:
                athlete_reaf.athletes_id.impression = True
                athlete_reaf.athletes_id.date_impression = self.date
            for athlete_ren in self.athletes3_ren_ids:
                athlete_ren.athletes_id.impression = True
                athlete_ren.athletes_id.date_impression = self.date
        self.state = 'valide'

        # Zoubida: annuler impression

    @api.multi
    def action_annuler(self):
        if self.athletes3_att_ids or self.athletes3_reaf_ids or self.athletes3_ren_ids:

            for athlete_att in self.athletes3_att_ids:
                athlete_att.athletes_id.impression = False
            for athlete_reaf in self.athletes3_reaf_ids:
                athlete_reaf.athletes_id.impression = False
            for athlete_ren in self.athletes3_ren_ids:
                athlete_ren.athletes_id.impression = False
        self.state = 'annulee'

    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].next_by_code('sports.edition.carteslicences')
        result = super(EditionCartesLicences, self).create(vals)
        return result



    @api.multi
    def generate_carte_report(self):

        report_ids = self.env['ir.actions.report.xml'].search([('report_type', '=', 'aeroo'),
                                                               ('model', '=', 'sports.edition.carteslicences'),
                                                               ('report_name', '=', 'edition_cartes_report')])
        return self.env['report'].get_action(
            self, report_ids.report_name)


class EditionCartesLicencesAthletes(models.Model):
    _name = "sports.athletes.carteslicences"

    name = fields.Char(string='Référence', invisible=True)

    athletes_id = fields.Many2one('sports.athletes', 'N° Licence', readonly=True)
    ligue_id = fields.Many2one('sports.ligue', string='Ligue', readonly=True)
    club_id = fields.Many2one('sports.club', 'Club', readonly=True)
    sequence = fields.Integer(string='séquence')

    nom = fields.Char(string='Nom')
    prenom = fields.Char(string='Prénom')

    carteslicences_id = fields.Many2one('sports.edition.carteslicences', ' Cartes Licences', invisible=True)

    # Zoubida: ajout de situation

    situation_etat = fields.Selection(string='Situation',
                                      related='athletes_id.situation_etat')


####adhérents avec passage de catégorie ===>  Liste des adhérents



class Editionpassagecategorie(models.Model):
    _name = "sports.passage.categorie"

    @api.model
    def _get_default_saison(self):

        return self.env['sports.saison'].search([('state', '=', 'active')])

    name = fields.Char(string='Référence', default='/')
    state = fields.Selection([('en_cours', 'En cours'), ('valide', 'Validé'), ('annulee', u'''Annlée''')], 'Etat',
                             readonly=True, default='en_cours')

    type_ = fields.Selection([('avec_changement_categorie', 'Avec changement de catégorie'),
                              ('sans_changement_categorie', 'Sans changement de catégorie')], 'Type', required=True)

    date = fields.Date('Date', copy=False)

    passage_ids = fields.One2many('sports.athletes.passage', 'passage_id', string='Athlétes')

    saison_id = fields.Many2one('sports.saison', string='Saison sportive', default=_get_default_saison)
    # club_id =  fields.Many2one('sports.club', 'Club')

    club_ids = fields.Many2many('sports.club', string='Clubs')

    @api.multi
    def generate_report(self):

        report_ids = self.env['ir.actions.report.xml'].search([('report_type', '=', 'aeroo'),
                                                               ('model', '=', 'sports.passage.categorie'),
                                                               ('report_name', '=', 'report_passage_categorie_ods')])
        return self.env['report'].get_action(
            self, report_ids.report_name)

    @api.multi
    def action_verification(self):
        if not self.passage_ids:

            # athletes_ids = self.env['sports.athletes'].search([('club_id', '=',self.club_id),('category_age_change', '=',True)])


            for club in self.club_ids:

                if self.type_ == 'avec_changement_categorie':

                    athletes_ids = self.env['sports.athletes'].search(
                        [('club_id', '=', club.id), ('category_age_change', '=', True)])

                else:

                    athletes_ids = self.env['sports.athletes'].search(
                        [('club_id', '=', club.id), ('category_age_change', '=', False)])

                for athlete in athletes_ids:
                    self.env['sports.athletes.passage'].create(
                        {'athletes_id': athlete.id, 'passage_id': self.id, 'club_id': athlete.club_id.id,
                         'nom': athlete.name_at, 'prenom': athlete.prenom, 'date': athlete.datenaissance,
                         'category_age_id': athlete.category_age_id.id})

            i = j = 0

            for passage in self.passage_ids:

                if j == 0:
                    passage.write({'afficher_club': True})
                    club = passage.club_id.id
                    j = j + 1

                if j > 0 and passage.club_id.id != club:
                    club = passage.club_id.id
                    passage.write({'afficher_club': True})
                    j = j + 1

                if i == 0:
                    passage.write({'afficher_button': True})
                    ca = passage.category_age_id.id
                    i = i + 1

                if i > 0 and passage.category_age_id.id != ca:
                    ca = passage.category_age_id.id
                    passage.write({'afficher_button': True})
                    i = i + 1

            return True

    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].next_by_code('sports.passage.categorie')
        result = super(Editionpassagecategorie, self).create(vals)
        return result


#### athletes passage

class EditionpassageAthletes(models.Model):
    _name = "sports.athletes.passage"
    _order = 'club_id desc, category_age_id desc, id desc'

    name = fields.Char(string='Référence', invisible=True)

    athletes_id = fields.Many2one('sports.athletes', 'N° Licence', readonly=True)

    club_id = fields.Many2one('sports.club', 'Club', readonly=True)
    nom = fields.Char(string='Nom', readonly=True)
    prenom = fields.Char(string='Prénom', readonly=True)
    date = fields.Date(string='Date Naissance', readonly=True)
    category_age_id = fields.Many2one('sports.category_age', string='Catégorie d’âge', readonly=True)
    passage_id = fields.Many2one('sports.passage.categorie', 'Passage categorie', invisible=True)
    afficher_button = fields.Boolean('Categorie Afficher')
    afficher_club = fields.Boolean('Afficher Club')
