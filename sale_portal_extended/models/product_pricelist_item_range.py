from odoo import fields, models, api
from odoo.exceptions import UserError


class ProductPricelistItemRange(models.Model):
    _name = 'product.pricelist.item.range'
    _description = 'Product Price List Range'

    pricelist_item_id = fields.Many2one('product.pricelist.item')
    min_amount = fields.Float(string="Minimum Amount")
    max_amount = fields.Float(string="Maximum Amount")
    discount_perecent = fields.Float(string="Percent")

    @api.onchange('min_amount', 'max_amount')
    def onchnage_amount(self):
        for rec in self:
            if rec.min_amount and rec.max_amount and rec.max_amount < rec.min_amount:
                raise UserError("Maximum amount should be greater then Minimum amount")