# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
import time
from openerp.report import report_sxw
from openerp import _


class ParserAssurance(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ParserAssurance, self).__init__(cr, uid, name, context)

        lang = context.get('lang', 'fr_FR')
        assurances = self.get_assurances()
        self.localcontext.update({
            'lang': lang,
            'assurances': self.get_assurances,
          
        })


    def get_assurances(self, context=None):
        
        if not context:
            context = {}
        
        domain = [('id', '>=', 0)]
        

        assurances_ids = self.pool[sports.excel.assurances].search(
            self.cr, self.uid, domain, context=context)

        assurances = self.pool[sports.excel.assurances].browse(
            self.cr, self.uid, assurances_ids, context=context)
        return assurances
