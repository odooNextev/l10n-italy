    currency_id = fields.Many2one(...)
    category_id = fields.Many2one(
        "asset.category",
        related="l10n_it_asset_id.category_id",
        store=True,
        string="Category",
    )
