from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class StockMoveConteo(models.Model):
    _inherit = 'stock.move'
    _description = 'Anexo para trazabilidad'

    conteo_stock = fields.Float(string="Conteo actual", compute='_compute_conteo',digits=dp.get_precision('Product Unit of Measure'))

    @api.one
    @api.depends('product_id', 'date', 'conteo_stock')
    def _compute_conteo(self):
    	current_user_id = self.env.uid
    	current_user = self.env['res.users'].search([('id', '=', current_user_id)], limit=1)
    	lista_com = []
    	for co in current_user.company_ids:
    		lista_com.append(co.id)
    	cr = self.env.cr
    	lista = []
    	def_pro = self.env.context.get('default_product_id', False)
    	search_pro = self.env.context.get('search_default_product_id', False)
        for p in self.product_id.product_variant_ids:
        	lista.append(str(p.id))
    	
    	total_stock = 0.0
    	if(def_pro==search_pro):
    		sql = "select sm.product_uom_qty, sp.name, sl.name, sm.company_id from stock_move sm full outer join stock_picking sp on sp.id=sm.picking_id full outer join stock_location sl on sl.id = sm.location_id WHERE sm.product_id='"+str(def_pro)+"' and sm.id<='"+str(self.id)+"' and sm.state='done';"
	        cr.execute(str(sql))
	        filas = cr.fetchall()
	        if(filas!=[]):
	            for c in filas:
	            	qty = float(c[0])
	            	tt = str(c[1])
	            	if(c[3] in lista_com):
		            	if(tt.find("/IN/")>=0):
		            		total_stock = total_stock + float(qty)
		            	if(tt == 'None'):
		            		ttt = str(c[2])
		            		if(ttt.find("adjustment")>=0):
		            			total_stock = total_stock + float(qty)
		            		else:
		            			total_stock = total_stock - float(qty)
		            	if(tt.find("/OUT/")>=0):
		            		total_stock = total_stock - float(qty)
    	else:
	    	for l in lista:
		        sql = "select sm.product_uom_qty, sp.name, sl.name from stock_move sm full outer join stock_picking sp on sp.id=sm.picking_id full outer join stock_location sl on sl.id = sm.location_id WHERE sm.product_id='"+str(l)+"' and sm.id<='"+str(self.id)+"' and sm.state='done';"
		        cr.execute(str(sql))
		        filas = cr.fetchall()
		        if(filas!=[]):
		            for c in filas:
		            	qty = float(c[0])
		            	tt = str(c[1])
		            	if(c[3] in lista_com):
			            	if(tt.find("/IN/")>=0):
			            		total_stock = total_stock + float(qty)
			            	if(tt == 'None'):
			            		ttt = str(c[2])
			            		if(ttt.find("adjustment")>=0):
			            			total_stock = total_stock + float(qty)
			            		else:
			            			total_stock = total_stock - float(qty)
			            	if(tt.find("/OUT/")>=0):
			            		total_stock = total_stock - float(qty)

        self.conteo_stock = total_stock