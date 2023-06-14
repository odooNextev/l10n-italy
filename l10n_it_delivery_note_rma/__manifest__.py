#  Copyright 2019 Simone Rubino - Agile Business Group
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "ITA - DDT - Portale",
    "summary": "Aggiunge i DDT nel portale.",
    "version": "14.0.1.0.0",
    "category": "Localization/Italy",
    "website": "https://github.com/OCA/l10n-italy",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "l10n_it_delivery_note",
        "portal",
    ],
    "data": [
        "views/portal_templates.xml",
        "views/portal_my_delivery_notes.xml",
        "security/ir.model.access.csv",
    ],
}
