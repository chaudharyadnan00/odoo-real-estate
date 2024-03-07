from odoo import models, fields, api


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _order = "name"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(string="Sequence")
    property_ids = fields.One2many(
        "estate.property", "property_type_id", string="Properties"
    )
    offer_ids = fields.One2many(
        "estate.property.offer", "property_type_id", string="OFFERS"
    )
    offer_count = fields.Integer(string="Offer Count", compute="_compute_offer_count")


    _sql_constraints = [
        (
            "estate_property_type_unique_name",
            "UNIQUE(name)",
            "Property type name must be unique",
        ),
    ]

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
    