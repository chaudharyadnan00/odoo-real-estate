from odoo import models, fields, api
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _order = "id desc"

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Post Code")
    date_availability = fields.Date(
        string="Date of Availability",
        default=(date.today() + timedelta(days=90)).strftime("%Y-%m-%d"),
        copy=False,
    )
    last_seen = fields.Datetime("Last Seen", default=fields.Datetime.now)
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area (square meters)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (square meters)")
    garden_orientation = fields.Selection(
        [("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")],
        string="Garden Orientation",
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="new",
        copy=False,
        required=True,
    )

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    salesperson_id = fields.Many2one(
        "res.users", string="Salesperson", default=lambda self: self.env.user
    )
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)

    tag_ids = fields.Many2many("estate.property.tag", string="Property Tags")

    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    total_area = fields.Float(string="Total Area", compute="_compute_total_area")
    best_price = fields.Float(string="Best Price", compute="_compute_best_price")

    image=fields.Binary()

    _sql_constraints = [
        (
            "estate_property_positive_expected_price",
            "CHECK(expected_price > 0)",
            "Expected price must be strictly positive",
        ),
        (
            "estate_property_positive_selling_price",
            "CHECK(selling_price >= 0)",
            "Selling price must be Positive",
        ),
    ]
    def unlink(self):
        for record in self:
            if record.state not in ['new', 'cancelled']:
                raise ValidationError("You cannot delete a property that is not in 'New' or 'Cancelled' state.")
        return super().unlink()


    @api.constrains("selling_price")
    def _check_selling_price(self):
        for record in self:
            if not float_is_zero(record.selling_price, 2) and float_compare(record.selling_price, 0.9 * record.expected_price, 2) == -1:
                raise ValidationError("The selling price must be atleast 90% of the expected price.")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            offer_prices = record.offer_ids.mapped("price")
            if offer_prices:
                record.best_price = max(offer_prices, default=0)
            else:
                record.best_price = 0.0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10.0
            self.garden_orientation = "north"
        else:
            self.garden_area = 0.0
            self.garden_orientation = ""

    def estate_property_action_sold(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError("Cancelled property cannot be sold.")
            else:
                if float_is_zero(record.selling_price, 2):
                    raise ValidationError("The selling price must be atleast 90% of the expected price.")
                else:    
                    record.state = "sold"
            return True

    def estate_property_action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise UserError("Sold property cannot be cancelled")
            else:
                record.state = "cancelled"
            return True
