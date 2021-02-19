# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import redirect

from common.UrlManager import UrlManager
from common.lib.user.UserService import UserService
from common.models.User import User
from web.application import app,db
from common.lib.Helper import iPagination,getCurrentDate
route_account = Blueprint( 'account_page',__name__ )
from common.lib.Helper import ops_render
from sqlalchemy import or_

@route_account.route( "/index" )
def index():

    resp_data = {}
    req = request.values

    page = int( req['p']) if ('p' in req and req['p']) else 1

    if "mix_kw" in req:
        rule = or_(User.nickname.ilike("%{0}%".format( req['mix_kw']) ),User.mobile.ilike("%{0}%".format( req['mix_kw']) ))
        User.query = User.query.filter(rule)

    if "status"in req and int( req['status'] )>-1:
        User.query = User.query.filter( User.status == int( req['status'] ))

    page_params = {
        'total':User.query.count(), #总共多少数据
        'page_size':app.config['PAGE_SIZE'],    #每一页多少
        'page':page,  #第几页
        'display':app.config['PAGE_DISPLAY'],  #显示多少页
        'url':request.full_path.replace("&p={}".format(page),"")
    }
    pages = iPagination( page_params )
    offset = ( page-1) * app.config['PAGE_SIZE']
    limit = app.config['PAGE_SIZE'] * page

    #[offset:limit]切片操作，取从offset到limit的数据。
    list = User.query.order_by( User.uid.desc()).all()[offset:limit]
    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['search_con'] = req
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    for tmp in resp_data['status_mapping']:
        app.logger.info(tmp)
    return ops_render( "account/index.html",resp_data )

@route_account.route( "/info" )
def info():
    resp_data = {}
    req = request.args
    uid = int( req.get('id',0))
    if uid < 1:
        return redirect( UrlManager.buildUrl("/account/index"))
    info = User.query.filter_by(uid = uid).first()
    if not info:
        return redirect(UrlManager.buildUrl("/account/index"))

    resp_data['info'] = info
    return ops_render( "account/info.html" ,resp_data)

@route_account.route( "/set",methods=['GET','POST'] )
def set():
    default_pwd = "******"
    if request.method == "GET":
        resp_data = {}
        req = request.args
        uid = int( req.get("id",0))
        info = None
        if uid:
            info = User.query.filter_by(uid = uid).first()
        resp_data['info'] = info
        return ops_render("account/set.html",resp_data)
    resp = {'code': 200, 'msg': '编辑成功', 'data': {}}
    req = request.values
    nickname = req['nickname'] if 'nickname' in req else ''
    email = req['email'] if 'email' in req else ''
    mobile = req['mobile'] if 'mobile' in req else ''
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''
    id = req['id'] if 'id' in req else '0'


    if nickname is None or len(nickname) < 1:
        resp['code'] = -1
        resp['msg'] = "nickname failed"
        return jsonify(resp)

    if email is None or len(email) < 1:
        resp['code'] = -1
        resp['msg'] = "email failed"
        return jsonify(resp)

    has_in = User.query.filter( User.login_name == login_name,User.uid != id).first()
    if has_in:
        resp['code'] = -1
        resp['msg'] = "email failed"
        return jsonify(resp)

    user_info = User.query.filter(User.uid == id).first()
    if user_info:
        model_user = user_info
    else:
        model_user = User()
        model_user.updated_time = getCurrentDate()
        model_user.created_time = getCurrentDate()

    if login_pwd != default_pwd:
        model_user.login_salt = UserService.genSalt()
        model_user.login_pwd = UserService.genePwd(login_pwd, model_user.login_salt)

    model_user.nickname = nickname
    model_user.email = email
    model_user.mobile = mobile
    model_user.login_name = login_name


    db.session.add(model_user)
    db.session.commit()
    return jsonify(resp)

@route_account.route( "/ops",methods=['POST'] )
def ops():
    resp = {'code': 200, 'msg': '编辑成功', 'data': {}}
    req = request.values

    id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ""
    if not id:
        resp['code'] = -1
        resp['msg'] = "login_name is already exist"
        return jsonify(resp)

    if not act in ['remove','recover']:
        resp['code'] = -1
        resp['msg'] = "login_name is already exist"
        return jsonify(resp)
    user_info = User.query.filter(User.uid == id ).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "login_name don't  exist"
        return jsonify(resp)

    if act == "remove":
        user_info.status = 0
    elif act == "recover":
        user_info.status = 1
    user_info.update_time = getCurrentDate()
    db.session.add(user_info)
    db.session.commit()

    return jsonify(resp)

