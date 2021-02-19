# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, g
from common.lib.Helper import ops_render

route_index = Blueprint( 'index_page',__name__ )

@route_index.route("/")
def index():
    current_user = g.current_user
    return ops_render( "index/index.html")