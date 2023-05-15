from . import models
from odoo import api, SUPERUSER_ID


def create_dn_types_init_hook(cr, sequence):
    """
    Create DN types and their sequences after installing the module
    if they're not already exist
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env["res.company"].search([])
    for company in companies:
        env["stock.delivery.note.type"].create_dn_types(company)
