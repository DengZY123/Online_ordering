# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, make_response, Response, g
from werkzeug.utils import redirect
from common.lib.Helper import ops_render

from common.UrlManager import UrlManager
from common.models.User import User
import json
from web.application import app, db
from werkzeug.test import Client
from common.lib.user import UserService



route_user = Blueprint( 'user_page',__name__ )

@route_user.route( "/login" ,methods=['GET','POST'])
def login():
    if request.method == "GET":
        return ops_render( "user/login.html" )
    resp = {'code':200,'msg':'登录成功','data':{}}
    req = request.values
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

    if login_name is None or len(login_name)<1:
        resp ['code']=-1
        resp['msg']="loging_name failed"
        return jsonify(resp)

    if login_pwd is None or len(login_pwd)<1:
        resp ['code']=-1
        resp['msg']="login_pwd failed"
        return jsonify(resp)

    user_info = User.query.filter_by(login_name = login_name).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "there is not the person"
        return jsonify(resp)

    if user_info.login_pwd != UserService.UserService.genePwd(login_pwd,user_info.login_salt):
        app.logger.info(UserService.UserService.genePwd(login_pwd,user_info.login_salt))
        resp['code'] = -1
        resp['msg'] = "the pwd is wrong"
        return jsonify(resp)

    response = make_response(json.dumps(resp))
    response.set_cookie(app.config['AUTH_COOKIE_NAME'],
            "%s#%s"%(UserService.UserService.geneAuthCode(user_info),user_info.uid))
    return response



@route_user.route( "/edit",methods=['GET','POST'] )
def edit():
    if request.method == "GET":
        return ops_render( "user/edit.html", {'current':'edit'})
    resp = {'code':200,'msg':'编辑成功','data':{}}
    req = request.values
    nickname = req['nickname'] if 'nickname' in req else ''
    email = req['email'] if 'email' in req else ''

    if nickname is None or len(nickname)<1:
        resp ['code']=-1
        resp['msg']="nickname failed"
        return jsonify(resp)

    if email is None or len(email)<1:
        resp ['code']=-1
        resp['msg']="email failed"
        return jsonify(resp)

    user_info = g.current_user
    user_info.nickname = nickname
    user_info.email = email

    db.session.add(user_info)
    db.session.commit()


    return jsonify(resp)



@route_user.route( "/reset-pwd",methods=['POST','GET'] )
def resetPwd():
    if request.method == "GET":
        return ops_render("user/reset_pwd.html",{'current':'reset-pwd'})
    app.logger.info("lalalallaalallalall")
    resp = {'code': 200, 'msg': '编辑成功', 'data': {}}
    req = request.values
    new_password = req['new_password'] if 'new_password' in req else ''
    old_password = req['old_password'] if 'old_password' in req else ''

    if new_password is None or len(new_password) < 6:
        resp['code'] = -1
        resp['msg'] = "new_password failed"
        return jsonify(resp)

    if old_password is None or len(old_password) < 6:
        resp['code'] = -1
        resp['msg'] = "old_password failed"
        return jsonify(resp)

    if old_password == new_password:
        resp['code'] = -1
        resp['msg'] = "new password should not equals old password"
        return jsonify(resp)

    user_info = g.current_user
    user_info.login_pwd = UserService.UserService.genePwd(new_password,user_info.login_salt)

    db.session.add(user_info)
    db.session.commit()

    response = make_response(json.dumps(resp))
    response.set_cookie("mooc_food",
                        "%s#%s" % (UserService.UserService.geneAuthCode(user_info), user_info.uid))
    return response


@route_user.route("/logout")
def logout():
    app.logger.info("logout")
    response = make_response(redirect(UrlManager.buildUrl("/user/login")))
    response.delete_cookie("mooc_food")
    return response