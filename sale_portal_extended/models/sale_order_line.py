from odoo import fields, models, api


class SaleorderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_discount(self):
        for line in self:
            if line.pricelist_item_id and line.pricelist_item_id.calculate_based_on_order_amount:
                base_price = line._get_pricelist_price_before_discount()
                if base_price:
                    amount = line.order_id.amount_undiscounted
                    range_id = line.pricelist_item_id.item_range_ids.filtered(lambda range:range.min_amount <= amount and range.max_amount >= amount)
                    line.discount = range_id and range_id[0].discount_perecent or 0
            else:
                return super(SaleorderLine, line)._compute_discount()
