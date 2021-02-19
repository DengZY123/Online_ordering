from web.controllers.api import *
from flask import request,jsonify,current_app
from web.application import app,db
import requests,json
from common.models.Member import Member
from common.models.OauthMember import OauthMemberBind
from common.lib.Helper import getCurrentDate
from common.lib.member.MemberService import MemberService


route_food = Blueprint( 'api_page',__name__ )
@route_api.route("/member/login",methods = ["GET","POST"])
def login():
    resp = {'code':200,'msg':"操作成功","data":{}}
    req = request.values

    code = req['code']
    app.logger.info(len(code))
    app.logger.info(code)
    if code == None or len(code)<10:
        resp['code'] = -1
        resp['msg'] = "需要code"
        app.logger.info("need code")
        return jsonify( resp )
    openid = MemberService.getWeChatOpenId( code )
    if openid == None:
        resp['code'] = -1
        resp['msg'] = "微信调用登录接口失败"
        app.logger.info("微信调用登录接口失败")
        return jsonify(resp)
    resp["openid"] = openid
    nickname = req['nickName']
    sex = req['gender']
    avatar = req['avatarUrl']

    bind_info = OauthMemberBind.query.filter_by(openid = openid, type = 1).first()
    app.logger.debug("bind_info")
    app.logger.debug(bind_info)
    if not bind_info:
        model_member = Member()
        model_member.nickname = nickname
        model_member.sex = sex
        model_member.avatar = avatar
        model_member.salt = MemberService.genSalt()
        model_member.created_time = model_member.updated_time = getCurrentDate()
        db.session.add(model_member)
        db.session.commit()

        model_bind = OauthMemberBind()
        model_bind.member_id = model_member.id
        model_bind.type = 1
        model_bind.extra = ''
        model_bind.openid = openid
        model_bind.updated_time = model_bind.created_time = getCurrentDate()
        db.session.add(model_bind)
        db.session.commit()

        db.session.flush()

        bind_info = model_bind


    member_info = Member.query.filter_by(id=bind_info.member_id).first()
    token = "%s#%s" % (MemberService.geneAuthCode(member_info), member_info.id)
    resp['data'] = {'token': token}
    return jsonify( resp )

@route_api.route("/member/check-reg",methods = ["GET","POST"])
def checkReg():
    resp = {'code': 200, 'msg': "操作成功", "data": {}}
    req = request.values
    code = req['code']
    app.logger.info(len(code))
    app.logger.info(code)
    if code == None or len(code) < 10:
        resp['code'] = -1
        resp['msg'] = "需要code"
        app.logger.info("need code")
        return jsonify(resp)

    openid = MemberService.getWeChatOpenId( code )
    if openid == None:
        resp['code'] = -1
        resp['msg'] = "微信调用登录接口失败"
        app.logger.info("微信调用登录接口失败")
        return jsonify(resp)

    bind_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first()
    if not bind_info:
        resp['code'] = -1
        resp['msg'] = "没有绑定微信"
        app.logger.info("微信调用登录接口失败")
        return jsonify(resp)

    member_info = Member.query.filter_by(id=bind_info.member_id).first()
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "未查到绑定信息"
        app.logger.info("微信调用登录接口失败")
        return jsonify(resp)

    token = "%s#%s"%( MemberService.geneAuthCode( member_info ),member_info.id)
    resp['data'] = {'token':token}
    return jsonify(resp)

@route_api.route("/member/test",methods = ["GET","POST"])
def test():
    resp = {'code':200,'msg':"操作成功","data":{}}
    return jsonify( resp )
