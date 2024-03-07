from odoo import models, fields, api
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    price = fields.Float(string="Price")
    status = fields.Selection(
        [("accepted", "Accepted"), ("refused", "Refused")], string="Status", copy=False
    )
    partner_id = fields.Many2one("res.partner", required=True, string="Partner")
    property_id = fields.Many2one(
        "estate.property", required=True, string="Property Id"
    )

    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
    )
    validity = fields.Integer(string="Validity", default=7)
    property_type_id=fields.Many2one('estate.property.type', related="property_id.property_type_id", string="Property Type Id", store=True)

    _sql_constraints = [
        (
            "estate_property_offer_positive_price",
            "CHECK(price > 0)",
            "An offer price must be strictly positive",
        ),
    ]

    @api.model
    def create(self, vals):
        offer = super().create(vals)
        offer.property_id.state="offer_received"
        existing_offers = self.env['estate.property.offer'].search(
            [("property_id", "=", offer.property_id.id), ("id", "!=", offer.id)]
        )
        for record in existing_offers:
            if offer.price < record.price:
                raise ValidationError("Offer Price should be greater than existing offers")
        return offer

    def unlink(self):
        property_ids = self.mapped("property_id")
        print(property_ids)
        super().unlink()
        for record in property_ids:
            remaining_offers = self.search(
                [("property_id", "=", record.id)]
            )
            if not remaining_offers:
                record.state = "new"

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + timedelta(days = record.validity)
            else:
                record.date_deadline = date.today() + timedelta(days = record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date and record.date_deadline:
                record.validity = (fields.Date.from_string(record.date_deadline) - fields.Date.from_string(record.create_date)).days

    def estate_property_offer_action_accept(self):
        for record in self:
            if record.property_id.selling_price != 0.0:
                raise UserError("Can not accept more than one offer")

            else:
                property_id = record.property_id
                property_offers = self.env["estate.property.offer"].search(
                    [
                        ("id", "!=", record.id),
                        ("property_id", "=", property_id.id),
                    ]
                )
                property_offers.write({"status": "refused"})
                record.status = "accepted"
                property_id.state = "offer_accepted"
                property_id.selling_price = record.price
                property_id.buyer_id = record.partner_id
        return True

    def estate_property_offer_action_refuse(self):
        for record in self:
            record.status = "refused"
            record.property_id.selling_price = 0.0
            record.property_id.buyer_id = False
        return True
