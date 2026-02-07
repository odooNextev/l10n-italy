# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AssetDepreciation(models.Model):
    _inherit = 'account.asset.depreciation'

    currency_id = fields.Many2one('res.currency', string='Currency')
    category_id = fields.Many2one(
        "asset.category",
        related="l10n_it_asset_id.category_id",
        store=True,
        string="Category",
    )

    # Your additional fields and methods go here