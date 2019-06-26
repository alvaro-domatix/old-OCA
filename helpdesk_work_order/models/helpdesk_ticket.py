from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):

    _inherit = 'helpdesk.ticket'

    work_order_id = fields.Many2one(
        comodel_name='work.order',
        string='Work Order')

    def action_create_work_order(self):
        if not self.partner_id:
            raise UserError(_(
                "The Ticket must have partner to create a work order."))

        work_order_obj = self.env['work.order']

        header = 'Helpdesk Ticket: ' + self.number + ' - ' + self.name + '\n'

        work_order = work_order_obj.create({
            'partner_id': self.partner_id.id,
            'origin_document': self.number,
            'ticket_description':
                (header + self.description) if self.description else header,
        })

        message = _("This Work Order has been created from: <a href=# data-oe-model=helpdesk.ticket data-oe-id=%d>%s</a>") % (self.id, self.number)
        work_order.message_post(body=message)

        self.write({
            'work_order_id': work_order.id
        })
