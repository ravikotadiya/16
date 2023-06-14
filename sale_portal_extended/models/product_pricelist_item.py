from odoo import fields, models, api
from odoo.exceptions import UserError


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    item_range_ids = fields.One2many('product.pricelist.item.range', 'pricelist_item_id')
    calculate_based_on_order_amount = fields.Boolean(string="Based On Order Amount")

    @api.constrains('calculate_based_on_order_amount')
    def valid_calculate_based_on_order_amount(self):
        for rec in self:
            if rec.calculate_based_on_order_amount:
                if rec.min_quantity:
                    raise UserError('Min. Quantity must be 0')
                if rec.pricelist_id.discount_policy == 'with_discount':
                    raise UserError(
                        "Discount policy should be 'Show public price & discount to the customer' in pricelist")
