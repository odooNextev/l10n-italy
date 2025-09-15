# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from . import models

from odoo.tools import config

from openupgradelib import openupgrade, openupgrade_tools

from odoo.addons.base.models.ir_qweb_fields import Markup, nl2br, nl2br_enclose


def _l10n_it_fatturapa_pre_migration(env):
    RENAMED_FIELDS = [
        [
            (
                "res.company",
                "fatturapa_sender_partner",
            ),
            (
                "res.company",
                "l10n_edi_it_sender_partner",
            ),
        ],
        [
            (
                "account.move",
                "intermediary",
            ),
            (
                "account.move",
                "l10n_it_edi_intermediary_id",
            ),
        ],
    ]
    field_spec = []
    for renamed_field in RENAMED_FIELDS:
        (old_model, old_field), (new_model, new_field) = renamed_field
        field_spec.append(
            (
                old_model,
                new_model.replace(".", "_"),
                old_field,
                new_field,
            )
        )
    openupgrade.rename_fields(
        env,
        field_spec,
    )
