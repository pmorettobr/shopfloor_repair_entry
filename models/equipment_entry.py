# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class EquipmentEntry(models.Model):
    _name = 'equipment.entry'
    _description = 'Entrada de Equipamento para Reparo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    # ========== DADOS DO CLIENTE ==========
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True, tracking=True)
    
    # ========== DADOS DO CILINDRO ==========
    equipment_name = fields.Char(string='Nome do Equipamento', required=True, default='Cilindro Hidráulico')
    serial_number = fields.Char(string='Número de Série', tracking=True)
    equipment_model = fields.Char(string='Modelo', tracking=True)
    dimensions = fields.Char(string='Dimensões (Curso x Diâmetro)', help='Ex: 500mm x 80mm')
    
    # ========== CHECKLIST DE RECEBIMENTO ==========
    arrival_date = fields.Datetime(string='Data de Chegada', default=fields.Datetime.now, required=True)
    arrival_state = fields.Selection(
        selection=[('good', 'Bom'), ('regular', 'Regular'), ('bad', 'Ruim')],
        string='Estado de Chegada', default='regular', required=True
    )
    damage_description = fields.Text(string='Descrição de Avarias', placeholder='Descreva as avarias visíveis...')
    accessories = fields.Text(string='Acessórios Incluídos', placeholder='Ex: Mangueiras, conexões, suportes...')
    photos = fields.Many2many('ir.attachment', string='Fotos do Equipamento')
    
    # ========== VÍNCULO COM OP ==========
    mrp_production_id = fields.Many2one('mrp.production', string='Ordem de Produção Vinculada', copy=False, readonly=True)
    state = fields.Selection(
        selection=[('draft', 'Rascunho'), ('confirmed', 'Confirmado'), ('in_progress', 'Em Andamento'), ('done', 'Concluído'), ('cancelled', 'Cancelado')],
        string='Status', default='draft', tracking=True
    )
    
    # ========== CAMPOS DE RASTREIO ==========
    current_workcenter_id = fields.Many2one('mrp.workcenter', string='Máquina Atual')
    current_operation = fields.Char(string='Operação Atual')
    
    # ========== ROTEIRO ==========
    standard_route_id = fields.Many2one(
        'repair.standard.route',
        string='Roteiro Padrão',
        default=lambda self: self.env['repair.standard.route'].search([('active', '=', True)], limit=1)
    )

    def action_confirm_entry(self):
        """Confirma a entrada e gera a OP de reparo automaticamente"""
        for entry in self:
            if entry.state != 'draft':
                continue
            
            if entry.mrp_production_id:
                raise UserError(_('Já existe uma Ordem de Produção vinculada a esta entrada.'))
            
            # Cria a OP de Reparo
            production_vals = {
                'product_id': entry._get_or_create_repair_product().id,
                'product_qty': 1,
                'product_uom_id': entry._get_or_create_repair_product().uom_id.id,
                'origin': f'Entrada: {entry.id}',
                'production_type': 'repair',  # Módulo 2
                'equipment_entry_id': entry.id,
                # 'partner_id': entry.partner_id.id,  # ❌ REMOVIDO - Não existe no Community
                'note': entry._build_operations_note(),
            }
            
            production = self.env['mrp.production'].create(production_vals)
            
            entry.write({
                'mrp_production_id': production.id,
                'state': 'confirmed'
            })
        
        return True

    def _build_operations_note(self):
        """Cria uma nota com as operações do roteiro (Community)"""
        self.ensure_one()
        if not self.standard_route_id or not self.standard_route_id.operation_ids:
            return ''
        
        note = "=== ROTEIRO DE OPERAÇÕES ===\n\n"
        for op in self.standard_route_id.operation_ids.sorted('sequence'):
            note += f"▸ {op.name}\n"
            note += f"  Máquina: {op.workcenter_id.name}\n"
            note += f"  Tempo estimado: {op.time_cycle}h\n"
            if op.note:
                note += f"  Obs: {op.note}\n"
            note += "\n"
        
        return note

    def action_view_production(self):
        self.ensure_one()
        if not self.mrp_production_id:
            raise UserError(_('Nenhuma Ordem de Produção vinculada.'))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ordem de Produção',
            'res_model': 'mrp.production',
            'res_id': self.mrp_production_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_cancel_entry(self):
        for entry in self:
            if entry.mrp_production_id and entry.mrp_production_id.state not in ('cancel', 'done'):
                entry.mrp_production_id.action_cancel()
            entry.state = 'cancelled'
        return True

    def action_finish_entry(self):
        for entry in self:
            entry.state = 'done'
        return True

    def _get_or_create_repair_product(self):
        product = self.env['product.product'].search([('default_code', '=', 'REPAIR-SERVICE')], limit=1)
        if not product:
            product = self.env['product.product'].create({
                'name': 'Serviço de Reparo - Cilindro Hidráulico',
                'default_code': 'REPAIR-SERVICE',
                'type': 'service',
                'uom_id': self.env.ref('uom.product_uom_unit').id,
                'uom_po_id': self.env.ref('uom.product_uom_unit').id,
            })
        return product
