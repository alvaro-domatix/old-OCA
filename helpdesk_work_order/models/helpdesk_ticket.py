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

        if self.number in self.env['work.order'].search([]).mapped('origin_document'):
            raise UserError(_(
                "This ticket already has a work order."))

        work_order = work_order_obj.create({
            'partner_id': self.partner_id.id,
            'origin_document': self.number,
            'address_id': self.partner_id.id,
            'priority': self.priority,
            'ticket_description':
                (header + self.description) if self.description else header,
        })

        message = _("This Work Order has been created from: <a href=# data-oe-model=helpdesk.ticket data-oe-id=%d>%s</a>") % (self.id, self.number)
        work_order.message_post(body=message)

        self.write({
            'work_order_id': work_order.id
        })

    def action_view_work_order_id(self):
        self.ensure_one()
        return {
            'name': _('Work orders'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'work.order',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('work_order.view_work_order_form').id,
            'target': 'current',
            'res_id': self.work_order_id.id,
        }
