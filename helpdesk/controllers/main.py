import werkzeug
import logging
import odoo.http as http
import requests
from openerp.http import request
_logger = logging.getLogger(__name__)


class HelpdeskTicketController(http.Controller):

    @http.route('/ticket/close', type="http", auth="user")
    def support_ticket_close(self, **kw):
        """Close the support ticket"""
        values = {}
        for field_name, field_value in kw.items():
            values[field_name] = field_value
        ticket = http.request.env['helpdesk.ticket'].sudo().\
            search([('id', '=', values['ticket_id'])])
        ticket.stage_id = int(values.get('stage_id'))

        return werkzeug.utils.redirect("/my/ticket/" + str(ticket.id))

    @http.route('/new/ticket', type="http", auth="user", website=True)
    def create_new_ticket(self, **kw):

        categories = http.request.env['helpdesk.ticket.category'].sudo().search([('active', '=', True)])
        email = http.request.env.user.email
        name = http.request.env.user.name

        return http.request.render('helpdesk.portal_create_ticket', {'categories': categories, 'email': email, 'name': name})

    @http.route('/submitted/ticket', type="http", auth="user", website=True, csrf=True)
    def submit_ticket(self, **kw):
        vals = {}

        for field_name, field_value in kw.items():
            vals[field_name] = field_value

        new_ticket = {
                    'partner_name': vals['name'],
                    'category_id': vals['category'],
                    'partner_email': vals['email'],
                    'description': vals['description'],
                    'name': vals['subject'],
                    # 'attachment_ids': vals['attachment'],
                    'channel_id':request.env['helpdesk.ticket.channel'].sudo().search([('name', '=', 'Web')]).id,
                    'partner_id': request.env['res.partner'].sudo().search([('name', '=', vals['name']), ('email', '=', vals['email'])]).id
                 }
        new_ticket_id = request.env['helpdesk.ticket'].sudo().create(new_ticket)

        return werkzeug.utils.redirect("/my/tickets")
