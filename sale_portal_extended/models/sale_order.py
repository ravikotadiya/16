from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def open_wizard_import_order(self):
        return {
            'name': _('Import Order'),
            'view_mode': 'form',
            'res_model': 'wizard.import.sale.order',
            'view_type': 'form',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'new'
        }

    def raise_error_if_team_or_pricelist_missing(self):
        partner_id = self.env.user.partner_id
        if not partner_id.team_id:
            raise UserError(_("Sales Team is not configure into Partner {}".format(partner_id.name)))
        if not partner_id.property_product_pricelist:
            raise UserError(_("Pricelist is not configure into Partner {}".format(partner_id.name)))

    def get_values(self, values, row_no, excel_value, empty_row, type):
        if type == 'xlsx':
            values.update({'product': excel_value[0],
                           'quantity': excel_value[1],
                           'uom': excel_value[2],
                           'description': excel_value[3],
                           'row_no': row_no,
                           })
        else:
            values.update({
                'product': excel_value[0],
                'quantity': excel_value[1],
            })
        if not values.get('product'):
            empty_row.get('product').append(str(values.get('row_no')))
        if not values.get('uom'):
            empty_row.get('uom').append(str(values.get('row_no')))
        if not values.get('quantity'):
            empty_row.get('quantity').append(str(values.get('row_no')))

        return values, empty_row

    def validate_data(self, values, not_found, duplicate_found, type):
        product = values.get('product')
        is_error = False
        # for Product
        if type == 'xlsx':
            if not product:
                not_found.get('product').append(str(values.get('row_no')) + ':' + product)
                is_error = True
            if product:
                product_id = self.search_product(product)
                if product_id:
                    if len(product_id) > 1:
                        duplicate_found.get('product').append(product)
                        is_error = True
                else:
                    not_found.get('product').append(str(values.get('row_no')) + ':' + product)
                    is_error = True
            # UOM
            uom = values.get('uom')
            if uom:
                uom_id = self.search_uom(uom)
                if not uom_id:
                    not_found.get('uom').append(str(values.get('row_no')) + ':' + uom)
                    is_error = True
                else:
                    if len(uom_id) > 1:
                        duplicate_found.get('uom').append(str(values.get('row_no')) + ':' + uom)
                        is_error = True
            else:
                not_found.get('uom').append(str(values.get('row_no')) + ':' + product)
                is_error = True

        return is_error, not_found, duplicate_found

    def search_product(self, product, limit=80):
        return self.env["product.product"].search([('default_code', '=ilike', product)], limit=limit)

    def search_uom(self, uom, limit=80):
        return self.env["uom.uom"].search([('name', '=ilike', uom)], limit=limit)
