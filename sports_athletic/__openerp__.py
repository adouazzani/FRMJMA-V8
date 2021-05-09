# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Sports athletic Management",
    "version": "1.0",
    "category": "Sports athletic Management",
    "sequence": 15,
    "summary": "Sports athletic AAMS/ Rachad Abdelhadi",
    "description": """ """,
    "website": "https://www.aams.com",
    "depends": ["stock", "product", "account","base", "report","purchase","purchase_requisition","hr","hr_contract"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        #"report/fiche.xml",
        "wizard/affiliation_reaffiliation.xml",
        "wizard/renouvellement.xml",
        "wizard/invitation_participants.xml",
        "wizard/engages_participants.xml",
        "views/report_fiche_athlete.xml",
        "employee_view.xml",
         #"mileage_allowance_view.xml",
        "sports_athletic_view.xml",
        "res_users_view.xml",
        "sport_athletic_parametre_view.xml",
         #"sport_athletic_sequence2.xml",
        "sport_athletic_report.xml",
        "sports_competitions_view.xml",
        "achat_view.xml",
        "sa_mission_order_view.xml",
         #"sa_expense_view.xml",
        "annual_calendar_view.xml",
        'report/layouts.xml',
        'report/achat_demande_report.xml',
        'report/mission_order_report.xml',
        'report/sa_expense_report.xml',
        'report/purchase_quotation_report.xml',
        'report/athlete_cart_report.xml',
        'report/member_list_report.xml',
        'report/reports.xml',
        "wizard/wizard_liasse.xml",
        #"wizard/bordereau_assurance_excel_view.xml",
        #"wizard/bordereau_carteslicences_view.xml",

    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
