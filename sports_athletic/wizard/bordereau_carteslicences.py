# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from openerp.osv import fields, osv




class athletic_bordereau_carteslicences(osv.osv_memory):
    _name = 'athletic.bordereau.carteslicences'
    _columns = {
    

        'entraineur': fields.boolean('Entraineur'),
        'dirigeant': fields.boolean('Dirigeant'),
        'officiel': fields.boolean('Officiel'),
        
        'sportif_interne': fields.boolean('Sportif-Interne'),
        'sportif_mre': fields.boolean('Sportif-MRE'),
         'sportif_etranger': fields.boolean('Sportif-Etranger'),
      
    }

    _defaults = {
        'sportif_interne': True,
        'sportif_mre': True,
        'sportif_etranger': True,
    }






athletic_bordereau_carteslicences()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

