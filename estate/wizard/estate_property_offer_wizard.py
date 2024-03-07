from odoo import models, fields, api


class EstatePropertyOfferWizard(models.TransientModel):
    _name = "estate.property.offer.wizard"
    _description = "We can add offers to multiple properties."

    price = fields.Float(string="Price")
    partner_id = fields.Many2one("res.partner", required=True, string="Partner")
    validity = fields.Integer(string="Validity (days)", default=7)

    def create_offers(self):
        active_property_ids = self.env["estate.property"].search(
            [("id", "in", self._context.get("active_ids"))]
        )
        for record in active_property_ids:
            offer_vals = {
                "property_id": record.id,
                "partner_id": self.partner_id.id,
                "price": self.price,
                "validity": self.validity,
            }
            self.env["estate.property.offer"].create(offer_vals)
        return True
