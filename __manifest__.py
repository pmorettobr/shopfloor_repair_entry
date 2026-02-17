# -*- coding: utf-8 -*-
{
    'name': 'Shopfloor Repair Entry - Entrada de Equipamentos',
    'version': '16.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Entrada de cilindros de clientes e geração automática de OP de reparo',
    'description': """
        Fluxo simplificado para chão de fábrica (Community Edition):
        - Registro de entrada de equipamentos de clientes
        - Checklist de recebimento (estado, avarias, acessórios)
        - Geração automática de OP com Tipo = Reparo
        - Roteiro Padrão de Operações (como registro)
        - Rastreabilidade completa por número de série
        - COMPATÍVEL COM ODOO 16 COMMUNITY
    """,
    'author': 'Paulo Moretto',
    'license': 'LGPL-3',
    'depends': [
        'mrp',              # ✅ Community
        'mrp_production_type',  # ✅ Seu módulo 2
        'stock',            # ✅ Community
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/repair_standard_operations_data.xml',
        'views/repair_standard_operations_views.xml',
        'views/equipment_entry_views.xml',
        'views/mrp_production_inherit_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
