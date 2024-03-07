from odoo import fields, models, api, Command


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def estate_property_action_sold(self):
        for record in self:
            new_move = self.env["account.move"].create(
                {
                    "partner_id": record.buyer_id.id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": record.name,
                                "quantity": 1.0,
                                "price_unit": record.selling_price * 0.06,
                            },
                        ),
                        Command.create(
                            {
                                "name": "Administrative Fees",
                                "quantity": 1.0,
                                "price_unit": 100.0,
                            },
                        ),
                    ],
                }
            )
        return super(EstateProperty,self).estate_property_action_sold()
