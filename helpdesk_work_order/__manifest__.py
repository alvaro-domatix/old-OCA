# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Helpdesk_Work_Order',
    'summary': """
        Helpdesk vinculation with Work Order""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Domatix',
    'depends': [
        'helpdesk',
        'work_order',
    ],
    'data': [
        'views/helpdesk_ticket_views.xml',
        'views/work_order_views.xml'
    ],
    'application': False,
    'installable': True,
}
