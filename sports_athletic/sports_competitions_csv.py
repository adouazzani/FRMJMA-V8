# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Joel Grand-Guillaume and Vincent Renaville Copyright 2013 Camptocamp SA
#    CSV data formating inspired from http://docs.python.org/2.7/library/csv.html?highlight=csv#examples
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

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time

import openerp
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools.safe_eval import safe_eval as eval

import openerp.addons.decimal_precision as dp

import wizard
import re
import datetime
import itertools
import time
import tempfile
import StringIO
import cStringIO
import base64
import openerp.netsvc
import csv
import codecs

import base64





class competitionsUnicodeWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        # created a writer with Excel formating settings
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        #we ensure that we do not try to encode none or bool
        row = (x or u'' for x in row)

        encoded_row = [c.encode("utf-8") if isinstance(c, unicode) else c for c in row]

        self.writer.writerow(encoded_row)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)



class competitioncsv(osv.osv):
    _inherit = 'sports.competition'
    
    def name_get(self, cr, uid, ids, context=None):
		if not len(ids):
		    return []
		reads = self.read(cr, uid, ids, ['name'], context=context)
		res = []
		x = " "
		for record in reads:
		   
		    x = str(record['name'])
		    name = "competition_"+x.replace('/','-') + ".csv"
		    res.append((record['id'], name))
		return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
		res = self.name_get(cr, uid, ids, context=context)
		return dict(res)
    

    _columns = {
        'data': fields.binary('Fichier CSV',readonly=True),

        'export_filename': fields.function(_name_get_fnc, method=True, type="char", string='Liste des Engagements'),
    }

    

    #_defaults = {
    #             'export_filename' : 'engagements_liste.csv'}

    def action_manual_export_competition(self, cr, uid, ids, context=None):

        this = self.browse(cr, uid, ids)[0]
        rows = self.get_data(cr, uid, ids)
            
        file_data = StringIO.StringIO()
        try:
            writer = competitionsUnicodeWriter(file_data)
            writer.writerows(rows)
            file_value = file_data.getvalue()    
            self.write(cr, uid, ids,
                       {'data': base64.encodestring(file_value)},
                       )
            
                  
            
                       
        finally:
            file_data.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sports.competition',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }


    def _get_header_competition(self, cr, uid, ids):
        return [_(u'ID'),
                _(u'Num Licence'),
                _(u'Club'),
                _(u'Nom'),
                _(u'Prénom'),
                _(u'Epreuve'),
                ]

    def _get_rows_competition(self, cr, uid, ids):
        """
        Return list to generate rows of the CSV file
        """
        form = self.browse(cr, uid, ids[0])
        _id = form.id
        cr.execute('''
               
                select sbl.id,sbl.athletes_id.name,dd.name,sbl.name,sbl.athletes_name,sbl.athletes_prenom,sbl.epreuve_id.name
                        from sports_competition as sb, sports_competition_participants as sbl, sports_club dd 
                        where sbl.competition_rel_id=sb.id
                        and sb.id=%s 
                        and dd.id=sbl.club_id.id
                
                
                
                ''', (_id))

        res = cr.fetchall()

        rows = []
        for line in res:
            rows.append(list(line))
        return rows

    
    def get_data(self, cr, uid, ids):
        get_header_func = getattr(self,("_get_header_competition"))
        get_rows_func = getattr(self,("_get_rows_competition"))
        
        form = self.browse(cr, uid, ids[0])
        _id2 = form.id
        
        
        rows = itertools.chain((get_header_func(cr, uid, ids)),
                               get_rows_func(cr, uid, ids,
                                             _id2)
        
                               )
         
        
                             
                               
                        
        return rows
        
competitioncsv()       

    
