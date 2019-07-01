from odoo import fields, models, api


class WorkOrder(models.Model):
    _inherit = "work.order"

    ticket_description = fields.Html(
        string='Ticket Description')
