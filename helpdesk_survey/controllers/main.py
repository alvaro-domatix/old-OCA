import werkzeug
import logging
import odoo.http as http
from odoo.http import request

class HelpdeskTicketController(http.Controller):

    @http.route('/ticket/survey/<token>', type='http', auth='public', website=True)
    def ticket_survey(self, token):
        """Display Survey"""
        ticket = request.env['helpdesk.ticket'].sudo().search([('access_token', '=', token)])

        if ticket.rating:
            return http.request.render('helpdesk_survey.survey_already_complete', {"ticket": ticket})
        else:
            return http.request.render('helpdesk_survey.helpdesk_ticket_survey_page', {"ticket": ticket})

    @http.route('/ticket/survey/completed/<token>', type='http', auth='public', website=True)
    def survey_completed(self, token, **kw):
        """Update ticket with survey response"""

        ticket = request.env['helpdesk.ticket'].sudo().search([('access_token', '=', token)])

        vals = {}
        for field_name, field_value in kw.items():
            vals[field_name] = field_value

        ticket.rating = vals['support_rating']
        ticket.comment = vals['comment']

        return http.request.render('helpdesk_survey.survey_completed_page', {"ticket": ticket})
