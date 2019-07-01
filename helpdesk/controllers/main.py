import werkzeug
import logging
import odoo.http as http
import base64
from openerp.http import request
_logger = logging.getLogger(__name__)


class HelpdeskTicketController(http.Controller):

    @http.route('/ticket/close', type="http", auth="user")
    def support_ticket_close(self, **kw):
        """Close the support ticket"""
        values = {}
        for field_name, field_value in kw.items():
            values[field_name] = field_value
        ticket = http.request.env['helpdesk.ticket'].sudo(). \
            search([('id', '=', values['ticket_id'])])
        ticket.stage_id = int(values.get('stage_id'))

        return werkzeug.utils.redirect("/my/ticket/" + str(ticket.id))

    @http.route('/new/ticket', type="http", auth="user", website=True)
    def create_new_ticket(self, **kw):

        categories = http.request.env['helpdesk.ticket.category'].sudo(). \
            search([('active', '=', True)])
        email = http.request.env.user.email
        name = http.request.env.user.name

        return http.request.render('helpdesk.portal_create_ticket', {
            'categories': categories, 'email': email, 'name': name})

    @http.route('/submitted/ticket',
                type="http", auth="user", website=True, csrf=True)
    def submit_ticket(self, **kw):
        vals = {}

        for field_name, field_value in kw.items():
            vals[field_name] = field_value

        attachment = ""
        new_ticket = {
            'partner_name': vals.get('name'),
            'category_id': vals.get('category'),
            'partner_email': vals.get('email'),
            'description': vals.get('description'),
            'name': vals.get('subject'),
            'attachment_ids': attachment,
            'channel_id':
                request.env['helpdesk.ticket.channel'].
                sudo().search([('name', '=', 'Web')]).id,
            'partner_id':
                request.env['res.partner'].sudo().search([
                    ('name', '=', request.env.user.name),
                    ('email', '=', vals.get('email'))]).id
        }
        new_ticket_id = request.env['helpdesk.ticket'].sudo().create(
            new_ticket)
        new_ticket_id.message_subscribe_users(user_ids=request.env.user.id)

        if 'attachment' in vals:
            for c_file in request.httprequest.files.getlist('attachment'):
                data = c_file.read()

                if c_file.filename:
                    request.env['ir.attachment'].sudo().create({
                        'name': c_file.filename,
                        'datas': base64.b64encode(data),
                        'datas_fname': c_file.filename,
                        'res_model': 'helpdesk.ticket',
                        'res_id': new_ticket_id.id
                    })

        return werkzeug.utils.redirect("/my/tickets")
