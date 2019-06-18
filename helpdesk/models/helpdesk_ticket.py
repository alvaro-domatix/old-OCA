from odoo import api, fields, models, _


class HelpdeskTicket(models.Model):

    _name = 'helpdesk.ticket'
    _rec_name = 'number'
    _order = 'number desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_stage_id(self):
        return self.env['helpdesk.ticket.stage'].search([], limit=1).id

    number = fields.Char(string='Ticket number', default="/",
                         readonly=True)
    name = fields.Char(string='Title', required=True)
    description = fields.Text(required=True)
    user_id = fields.Many2one(
        'res.users',
        string='Assigned user',)

    active = fields.Boolean(
        default=True)

    kanban_state = fields.Selection(
        [('normal', 'Grey'),
         ('done', 'Green'),
         ('blocked', 'Red')],
        string='kanban state',
        copy=False,
        default="normal",
        required=True,
        help="A task's kanban state indicates special situations affecting it: \n"
              " * Grey us the default situation\n"
              " * Red indicates something is preventing the progress of this task\n"
              " * Green indicates the task is ready to be pulled to the next stage")

    kanban_state_label = fields.Char(
        compute='_compute_kanban_state_label',
        string='Kanban state',
        track_visibility='onchange')

    legend_priority = fields.Char(
        string='Starred Explanation',
        translate=True,
        help="Explanation text to help users using the star on tasks or issues in this stage.")

    legend_blocked = fields.Char(
        'Red kanban Label',
        default=lambda s: _("Blocked"),
        translate=True,
        required=True,
        help='Override the default value displayed for the blocked state for kanban selection, when the task or issue is in that stage.')

    legend_done = fields.Char(
        'Green kanban Label',
        default=lambda s: _("Ready for Next Stage"),
        translate=True,
        required=True,
        help='Override the default value displayed for the done state for kanban selection, when the task or issue is in that stage.')

    legend_normal = fields.Char(
        'Grey Kanban Label',
        default=lambda s: _("In progress"),
        translate=True,
        required=True,
        help='Override the default value displayed for the normal state for kanban selection, when the task or issue is in that stage.')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['helpdesk.ticket.stage'].search([])
        return stage_ids

    stage_id = fields.Many2one(
        'helpdesk.ticket.stage',
        string='Stage',
        group_expand='_read_group_stage_ids',
        default=_get_default_stage_id,
        track_visibility='onchange',
    )
    partner_id = fields.Many2one('res.partner')
    partner_name = fields.Char()
    partner_email = fields.Char()

    last_stage_update = fields.Datetime(
        string='Last Stage Update',
        default=fields.Datetime.now(),
    )
    assigned_date = fields.Datetime(string='Assigned Date')
    closed_date = fields.Datetime(string='Closed Date')
    closed = fields.Boolean(related='stage_id.closed')
    unattended = fields.Boolean(related='stage_id.unattended')

    tag_ids = fields.Many2many('helpdesk.ticket.tag')
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get(
            'helpdesk.ticket')
    )
    channel_id = fields.Many2one(
        'helpdesk.ticket.channel',
        string='Channel',
        help='Channel indicates where the source of a ticket'
             'comes from (it could be a phone call, an email...)',
    )

    category_id = fields.Many2one('helpdesk.ticket.category',
                                  string='Category')

    team_id = fields.Many2one('helpdesk.ticket.team')
    priority = fields.Selection(selection=[
        ('0', _('Low')),
        ('1', _('Medium')),
        ('2', _('High')),
        ('3', _('Very High')),
    ], string='Priority', default='1')

    attachment_ids = fields.One2many(
        'ir.attachment', 'res_id',
        domain=[('res_model', '=', 'website.support.ticket')],
        string="Media Attachments")

    def send_user_mail(self):
        self.env.ref('helpdesk.assignment_email_template'). \
            send_mail(self.id)

    def assign_to_me(self):
        self.write({'user_id': self.env.user.id})

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            self.partner_email = self.partner_id.email

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for ticket in self:
            if ticket.kanban_state == 'normal':
                ticket.kanban_state_label = ticket.legend_normal
            elif ticket.kanban_state == 'blocked':
                ticket.kanban_state_label = ticket.legend_blocked
            else:
                ticket.kanban_state_label = ticket.legend_done
    # ---------------------------------------------------
    # CRUD
    # ---------------------------------------------------

    @api.model
    def create(self, vals):
        if vals.get('number', '/') == '/':
            vals['number'] = self.env['ir.sequence'].next_by_code(
                'helpdesk.ticket.sequence'
            ) or '/'
        res = super().create(vals)

        # Check if mail to the user has to be sent
        if vals.get('user_id') and res:
            res.send_user_mail()
        return res

    @api.multi
    def write(self, vals):
        for ticket in self:
            now = fields.Datetime.now()
            if vals.get('stage_id'):
                stage_obj = self.env['helpdesk.ticket.stage'].browse(
                    [vals['stage_id']])
                vals['last_stage_update'] = now
                if stage_obj.closed:
                    vals['closed_date'] = now
            if vals.get('user_id'):
                vals['assigned_date'] = now
            if 'kanban_state' not in vals:
                vals['kanban_state'] = 'normal'

        res = super(HelpdeskTicket, self).write(vals)

        # Check if mail to the user has to be sent
        for ticket in self:
            if vals.get('user_id'):
                ticket.send_user_mail()
        return res

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    @api.multi
    def _track_template(self, tracking):
        res = super(HelpdeskTicket, self)._track_template(tracking)
        test_task = self[0]
        changes, tracking_value = tracking[test_task.id]
        if "stage_id" in changes and test_task.stage_id.mail_template_id:
            res['stage_id'] = (test_task.stage_id.mail_template_id,
                               {"composition_mode": "mass_mail"})

        return res
