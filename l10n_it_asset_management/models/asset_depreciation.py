import fields

# ... existing code ...

class AssetDepreciation(models.Model):
    _name = 'asset.depreciation'
    # ... existing fields ...

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
    )

    category_id = fields.Many2one(
        "asset.category",
        related="l10n_it_asset_id.category_id",
        store=True,
        string="Category",
    )

# ... existing code ...