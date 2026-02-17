# -*- coding: utf-8 -*-
from odoo import models, fields

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    equipment_entry_id = fields.Many2one(
        'equipment.entry', 
        string='Entrada de Equipamento', 
        copy=False, 
        readonly=True
    )    
    # Community: Campos para rastreio manual
    current_workcenter_id = fields.Many2one(
        'mrp.workcenter', 
        string='Máquina Atual'
    )
    current_operation = fields.Char(
        string='Operação Atual'
    )
