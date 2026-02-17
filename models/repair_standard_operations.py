# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class RepairStandardOperation(models.Model):
    _name = 'repair.standard.operation'
    _description = 'Operação Padrão de Reparo'
    _order = 'sequence asc'

    name = fields.Char(string='Nome da Operação', required=True)
    sequence = fields.Integer(string='Sequência', default=10)
    workcenter_id = fields.Many2one('mrp.workcenter', string='Centro de Trabalho', required=True)
    time_cycle = fields.Float(string='Tempo Padrão (horas)', default=1.0)
    note = fields.Text(string='Instruções')
    active = fields.Boolean(string='Ativo', default=True)
    route_id = fields.Many2one('repair.standard.route', string='Roteiro', ondelete='cascade')

class RepairStandardRoute(models.Model):
    _name = 'repair.standard.route'
    _description = 'Roteiro Padrão de Reparo'

    name = fields.Char(string='Nome do Roteiro', required=True, default='Roteiro Padrão - Cilindros Hidráulicos')
    operation_ids = fields.One2many('repair.standard.operation', 'route_id', string='Operações')
    active = fields.Boolean(string='Ativo', default=True)

    def action_load_default_operations(self):
        """Carrega operações padrão se estiver vazio"""
        self.ensure_one()
        if not self.operation_ids:
            default_ops = [
                ('Desmontagem', 10, 'DESMONT', 2.0),
                ('Limpeza e Inspeção', 20, 'LIMPEZA', 1.0),
                ('Usinagem', 30, 'USINAGEM', 4.0),
                ('Solda', 40, 'SOLDA', 3.0),
                ('Polimento', 50, 'POLIM', 2.0),
                ('Montagem', 60, 'MONTAGEM', 2.0),
                ('Teste de Pressão', 70, 'TESTE', 1.0),
            ]
            for name, seq, code, time in default_ops:
                workcenter = self.env['mrp.workcenter'].search([('code', '=', code)], limit=1)
                if workcenter:
                    self.env['repair.standard.operation'].create({
                        'route_id': self.id,
                        'name': name,
                        'sequence': seq,
                        'workcenter_id': workcenter.id,
                        'time_cycle': time,
                    })
        return True
