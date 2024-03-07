from odoo import http
from odoo.http import request

class EstateProperties(http.Controller):

    @http.route('/properties', type="http", auth="public", website=True)
    def all_properties(self):
        limit=6