# -*- coding: utf-8 -*-
from odoo import models, fields

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    equipment_entry_id = fields.Many2one('equipment.entry', string='Entrada de Equipamento', copy=False, readonly=True)
