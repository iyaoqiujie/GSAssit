# -*- coding:utf-8 -*-
import json
import requests
from datetime import datetime, timedelta
from django.core.cache import cache
#from workwechat_assist.corporation.models import Corporation, CorpApp, Department, Member, \
#    DepartmentMemberRelationShip, ExternalAttr
import logging

myLogger = logging.getLogger('WWAssist.wechat_sdk')


class ErrorCode(object):
    SUCCESS = 0


class WorkWechat(object):

    def __init__(self, corpapp):
        """
            document address: http://qydev.weixin.qq.com/wiki/index.php?title=%E9%A6%96%E9%A1%B5
        """
        self.corpid = corpapp.corp.corp_id
        self.corpsecret = corpapp.secret
        self.agentid = corpapp.agent_id
        self.url_prefix = "https://qyapi.weixin.qq.com/cgi-bin"
        #self.token_valid_time = None
        #self._access_token = self.__get_access_token()

    @property
    def access_token(self):
        access_token = cache.get('{0}:{1}'.format(self.corpid, self.agentid))
        if access_token:
            return access_token
        else:
            return self.__get_access_token()
        #if self.token_valid_time and datetime.now() < self.token_valid_time:
        #    return self._access_token
        #self.__get_access_token()
        #return self._access_token

    @access_token.setter
    def access_token(self, value):
        cache.set('{0}:{1}'.format(self.corpid, self.agentid), value, timeout=6000)
        #self._access_token = value

    def __get_access_token(self, force=False):
        # access_token 有效期为 7200秒
        cache_key = '{0}:{1}'.format(self.corpid, self.agentid)
        access_token = cache.get(cache_key)
        ttl = cache.ttl(cache_key)

        # If access token is not expired, just return
        if not force and access_token and ttl > 60:
            return access_token

        url = "%s/gettoken?corpid=%s&corpsecret=%s" % (self.url_prefix, self.corpid, self.corpsecret)
        res = requests.get(url)
        res = res.json()
        if res.get('errcode') != 0:
            myLogger.error('Failed to fetch the access token:[{0}], corpId: {1}, agentId: {2}'.format(
                res.get('errmsg'), self.corpid, self.agentid
            ))
            return ''

        access_token = res.get("access_token")
        cache.set(cache_key, access_token, timeout=6000)
        return access_token


#        if not force and self.token_valid_time and datetime.now() < self.token_valid_time:
#            return self.access_token
#
#        url = "%s/gettoken?corpid=%s&corpsecret=%s" % (self.url_prefix, self.corpid, self.corpsecret)
#        res = requests.get(url)
#        access_token = res.json().get("access_token")
#        self.token_valid_time = datetime.now() + timedelta(seconds=3600)
#        self.access_token = access_token
#        return access_token

    @staticmethod
    def __response(res):
        errcode = res.get("errcode")
        # errmsg = res.get("errmsg")
        if errcode is ErrorCode.SUCCESS:
            return True, res
        else:
            return False, res

    def __post(self, url, data):
        res = requests.post(url, data=json.dumps(data)).json()
        return self.__response(res)

    def __get(self, url):
        res = requests.get(url).json()
        return self.__response(res)

    def __post_file(self, url, media_file):
        #res = requests.post(url, file=media_file).json()
        res = requests.post(url, files=media_file).json()
        return self.__response(res)

    # 部门管理
    def create_department(self, name, parentid=1, order=None):
        """
            创建部门
            name    : 部门名称。长度限制为1~64个字符
            parentid: 父亲部门id。根部门id为1
            order   : 在父部门中的次序。从1开始，数字越大排序越靠后
        """
        url = "%s/department/create?access_token=%s" % (self.url_prefix, self.access_token)
        data = {
            "name": name,
            "parentid": parentid,
        }
        if order is not None:
            data["order"] = order
        status, res = self.__post(url, data)
        return status, res

    def update_department(self, department_id, **kwargs):
        """
            更新部门

            参数	必须	说明
            access_token	是	调用接口凭证
            id	是	部门id
            name	否	更新的部门名称。长度限制为1~64个字符。修改部门名称时指定该参数
            parentid	否	父亲部门id。根部门id为1
            order	否	在父部门中的次序。从1开始，数字越大排序越靠后
        """
        url = "%s/department/update?access_token=%s" % (self.url_prefix, self.access_token)
        data = {
            "id": department_id,
        }
        data.update(kwargs)
        myLogger.debug(data)
        status, res = self.__post(url, data)
        return status, res

    def delete_department(self, department_id):
        """
            删除部门
            参数	必须	说明
            access_token	是	调用接口凭证
            id	是	部门id。（注：不能删除根部门；不能删除含有子部门、成员的部门）
        """
        url = "%s/department/delete?access_token=%s&id=%s" % (self.url_prefix, self.access_token, department_id)
        status, res = self.__get(url)
        return status, res

    def get_department_list(self):
        """
            获取部门列表
            参数	必须	说明
            access_token	是	调用接口凭证
        """
        url = "%s/department/list?access_token=%s" % (self.url_prefix, self.access_token)
        status, res = self.__get(url)
        return status, res

    # 成员管理
    def create_user(self, data):
        """
            创建用户
            参数	必须	说明
            access_token	是	调用接口凭证
            userid	是	员工UserID。对应管理端的帐号，企业内必须唯一。长度为1~64个字符
            name	是	成员名称。长度为1~64个字符
            department	是	成员所属部门id列表。注意，每个部门的直属员工上限为1000个
            position	否	职位信息。长度为0~64个字符
            mobile	否	手机号码。企业内必须唯一，mobile/weixinid/email三者不能同时为空
            email	否	邮箱。长度为0~64个字符。企业内必须唯一
            weixinid	否	微信号。企业内必须唯一。（注意：是微信号，不是微信的名字）
            extattr	否	扩展属性。扩展属性需要在WEB管理端创建后才生效，否则忽略未知属性的赋值
        """
        url = "%s/user/create?access_token=%s" % (self.url_prefix, self.access_token)
        if data.get("userid") and data.get("name"):
            status, res = self.__post(url, data)
        else:
            status = False
            res = u"userid 或者 name 为空"
        return status, res

    def update_user(self, userid, **kwargs):
        """
            更新成员
            参数	必须	说明
            access_token	是	调用接口凭证
            userid	是	员工UserID。对应管理端的帐号，企业内必须唯一。长度为1~64个字符
            name	否	成员名称。长度为0~64个字符
            department	否	成员所属部门id列表。注意，每个部门的直属员工上限为1000个
            position	否	职位信息。长度为0~64个字符
            mobile	否	手机号码。企业内必须唯一，mobile/weixinid/email三者不能同时为空
            email	否	邮箱。长度为0~64个字符。企业内必须唯一
            weixinid	否	微信号。企业内必须唯一。（注意：是微信号，不是微信的名字）
            enable	否	启用/禁用成员。1表示启用成员，0表示禁用成员
            extattr	否	扩展属性。扩展属性需要在WEB管理端创建后才生效，否则忽略未知属性的赋值
        """
        url = "%s/user/update?access_token=%s" % (self.url_prefix, self.access_token)
        data = {"userid": userid}
        data.update(kwargs)
        status, res = self.__post(url, data=data)
        return status, res

    def delete_user(self, userid):
        """
            删除成员
            参数	必须	说明
            access_token	是	调用接口凭证
            userid	是	员工UserID。对应管理端的帐号
        """
        url = "%s/user/delete?access_token=%s&userid=%s" % (self.url_prefix, self.access_token, userid)
        status, res = self.__get(url)
        return status, res

    def multi_delete_user(self, useridlist):
        """
            批量删除成员
            参数	必须	说明
            access_token	是	调用接口凭证
            useridlist	是	员工UserID列表。对应管理端的帐号
        """
        url = "%s/user/batchdelete?access_token=%s" % (self.url_prefix, self.access_token)
        data = {"useridlist": useridlist}
        status, res = self.__post(url, data=data)
        return status, res

    def get_user(self, userid):
        """
            获取成员
            参数	必须	说明
            access_token	是	调用接口凭证
            userid	是	员工UserID。对应管理端的帐号

        """
        url = "%s/user/get?access_token=%s&userid=%s" % (self.url_prefix, self.access_token, userid)
        status, res = self.__get(url)
        return status, res

    def get_users_in_department(self, department_id, fetch_child=0, status=0):
        """
            获取部门成员
            参数	必须	说明
            access_token	是	调用接口凭证
            department_id	是	获取的部门id
            fetch_child	否	1/0：是否递归获取子部门下面的成员
            status	否	0获取全部员工，1获取已关注成员列表，2获取禁用成员列表，4获取未关注成员列表。status可叠加
        """
        url = "%s/user/simplelist?access_token=%s&department_id=%s&fetch_child=%s&status=%s" \
              % (self.url_prefix, self.access_token, department_id, fetch_child, status)
        status, res = self.__get(url)
        return status, res

    def get_users_in_department_detail(self, department_id, fetch_child=0, status=0):
        """
            获取部门成员(详情)
            参数	必须	说明
            access_token	是	调用接口凭证
            department_id	是	获取的部门id
            fetch_child	否	1/0：是否递归获取子部门下面的成员
            status	否	0获取全部员工，1获取已关注成员列表，2获取禁用成员列表，4获取未关注成员列表。status可叠加
        """
        url = "%s/user/list?access_token=%s&department_id=%s&fetch_child=%s&status=%s" \
              % (self.url_prefix, self.access_token, department_id, fetch_child, status)
        status, res = self.__get(url)
        return status, res

    def invite_attention_to_user(self, userid, invite_tips=None):
        """
            邀请用户关注
            参数	必须	说明
            access_token	是	调用接口凭证
            userid	是	用户的userid
            invite_tips	否	推送到微信上的提示语（只有认证号可以使用）。当使用微信推送时，该字段默认为“请关注XXX企业号”，邮件邀请时，该字段无效。
        """
        url = "%s/invite/send?access_token=%s" % (self.url_prefix, self.access_token)
        data = {
            "userid": userid
        }
        if invite_tips is not None:
            data["invite_tips"] = invite_tips
        status, res = self.__post(url, data)
        return status, res

    # 管理标签
    def create_tag(self, tagname):
        """
            创建标签
            参数	必须	说明
            access_token	是	调用接口凭证
            tagname	是	标签名称。长度为1~64个字符，标签不可与其他同组的标签重名，也不可与全局标签重名
        """
        url = "%s/tag/create?access_token=%s" % (self.url_prefix, self.access_token)
        data = {"tagname": tagname}
        status, res = self.__post(url, data)
        return status, res

    def update_tag(self, tagid, tagname):
        """
            更新标签名字
            参数	必须	说明
            access_token	是	调用接口凭证
            tagid	是	标签ID
            tagname	是	标签名称。长度为1~64个字符，标签不可与其他同组的标签重名，也不可与全局标签重名
        """
        url = "%s/tag/update?access_token=%s" % (self.url_prefix, self.access_token)
        data = {"tagid": tagid, "tagname": tagname}
        status, res = self.__post(url, data)
        return status, res

    def delete_tag(self, tagid):
        """
            删除标签
            参数	必须	说明
            access_token	是	调用接口凭证
            tagid	是	标签ID
        """
        url = "%s/tag/delete?access_token=%s&tagid=%s" % (self.url_prefix, self.access_token, tagid)
        status, res = self.__get(url)
        return status, res

    def get_user_from_tag(self, tagid):
        """
            获取标签成员
            参数	必须	说明
            access_token	是	调用接口凭证
            tagid	是	标签ID
        """
        url = "%s/tag/get?access_token=%s&tagid=%s" % (self.url_prefix, self.access_token, tagid)
        status, res = self.__get(url)
        return status, res

    def add_users_to_tag(self, tagid, userlist, partylist):
        """
            增加标签成员
            参数	必须	说明
            access_token	是	调用接口凭证
            tagid	是	标签ID
            userlist	否	企业员工ID列表，注意：userlist、partylist不能同时为空
            partylist	否	企业部门ID列表，注意：userlist、partylist不能同时为空
        """
        url = "%s/tag/addtagusers?access_token=%s" % (self.url_prefix, self.access_token)
        data = {"tagid": tagid, "userlist": userlist, "partylist": partylist}
        status, res = self.__post(url, data=data)
        return status, res

    def delete_user_in_tag(self, tagid, userlist, partylist):
        """
            删除标签成员
            参数	必须	说明
            access_token	是	调用接口凭证
            tagid	是	标签ID
            userlist	否	企业员工ID列表，注意：userlist、partylist不能同时为空
            partylist	否	企业部门ID列表，注意：userlist、partylist不能同时为空
        """
        url = "%s/tag/deltagusers?access_token=%s" % (self.url_prefix, self.access_token)
        data = {"tagid": tagid, "userlist": userlist, "partylist": partylist}
        status, res = self.__post(url, data=data)
        return status, res

    def get_tag_list(self):
        """
            获取标签列表
            参数	必须	说明
            access_token	是	调用接口凭证
        """
        url = "%s/tag/list?access_token=%s" % (self.url_prefix, self.access_token)
        status, res = self.__get(url)
        return status, res

    # 管理多媒体文件
    def upload_media(self, media_type, media_file):
        """
            上传媒体文件
            参数	必须	说明
            access_token	是	调用接口凭证
            type	是	媒体文件类型，分别有图片（image）、语音（voice）、视频（video），普通文件(file)
            media	是	form-data中媒体文件标识，有filename、filelength、content-type等信息
        """
        url = "%s/media/upload?access_token=%s&type=%s" % (self.url_prefix, self.access_token, media_type)
        data = {"media": media_file}
        status, res = self.__post_file(url, data)
        return status, res

    def get_media(self, media_id):
        """
            获取媒体文件
            参数	必须	说明
            access_token	是	调用接口凭证
            media_id	是	媒体文件id
        """
        url = "%s/media/get?access_token=%s&media_id=%s" % (self.url_prefix, self.access_token, media_id)
        media_file = requests.get(url)
        return media_file

    # 发送消息
    def send_msg_to_user(self, content, touser=None, toparty=None, totag=None, safe=0, msgtype="text", **kwargs):
        """
            发送消息到用户
            text消息
                参数	必须	说明
                touser	否	员工ID列表（消息接收者，多个接收者用‘|’分隔）。特殊情况：指定为@all，则向关注该企业应用的全部成员发送
                toparty	否	部门ID列表，多个接收者用‘|’分隔。当touser为@all时忽略本参数
                totag	否	标签ID列表，多个接收者用‘|’分隔。当touser为@all时忽略本参数
                msgtype	是	消息类型，此时固定为：text
                agentid	是	企业应用的id，整型。可在应用的设置页面查看
                content	是	消息内容
                safe	否	表示是否是保密消息，0表示否，1表示是，默认0
                其他消息参考： http://qydev.weixin.qq.com/wiki/index.php?
                    title=%E6%B6%88%E6%81%AF%E7%B1%BB%E5%9E%8B%E5%8F%8A%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F
        """
        url = "%s/message/send?access_token=%s" % (self.url_prefix, self.access_token)
        data = {
            "safe": safe,
            "msgtype": msgtype,
            "agentid": self.agentid
        }
        if msgtype == "text":
            data["text"] = {"content": content}
        if msgtype == "image":
            data["image"] = {"media_id": kwargs.get("media_id")}
        if msgtype == "voice":
            data["voice"] = {"media_id": kwargs.get("media_id")}
        if msgtype == "video":
            data["video"] = {
                "media_id": kwargs.get("media_id"),
                "title": kwargs.get("title"),
                "description": kwargs.get("description")
            }
        if msgtype == "file":
            data["file"] = {
                "media_id": kwargs.get("media_id")
            }
        if msgtype == "news":
            #   {
            #       "articles":[
            #           {
            #               "title": "Title",
            #               "description": "Description",
            #               "url": "URL",
            #               "picurl": "PIC_URL"
            #           },
            #           {
            #               "title": "Title",
            #               "description": "Description",
            #               "url": "URL",
            #               "picurl": "PIC_URL"
            #           }
            #       ]
            #   }
            data["news"] = kwargs
        if msgtype == "mpnews":
            #{
            #   "articles":[
            #       {
            #           "title": "Title",
            #           "thumb_media_id": "id",
            #           "author": "Author",
            #           "content_source_url": "URL",
            #           "content": "Content",
            #           "digest": "Digest description",
            #           "show_cover_pic": "0"
            #       },
            #       {
            #           "title": "Title",
            #           "thumb_media_id": "id",
            #           "author": "Author",
            #          "content_source_url": "URL",
            #           "content": "Content",
            #           "digest": "Digest description",
            #           "show_cover_pic": "0"
            #       }
            #   ]
            #}
            data["mpnews"] = kwargs

        if touser is None:
            to_user = "@all"
        else:
            to_user = '|'.join(touser)
        data["touser"] = to_user
        if toparty is not None:
            data["toparty"] = toparty

        if totag is not None:
            data["totag"] = totag
        status, res = self.__post(url, data)
        return status, res

    # 二次验证
    def second_validation(self, userid):
        """
            二次验证
            参数	必须	说明
            access_token	是	调用接口凭证
            userid	是	员工UserID
        """
        url = "https://qyapi.weixin.qq.com/cgi-bin/user/authsucc?access_token=%s&userid=%s" \
              % (self.access_token, userid)
        status, res = self.__get(url)
        return status, res

    # 客户管理
    def get_follow_user_list(self):
        """
        企业和第三方服务商可通过此接口获取配置了客户联系功能的成员列表。
        :return:
        """
        url = '{0}/externalcontact/get_follow_user_list?access_token={1}'.format(self.url_prefix, self.access_token)
        status, res = self.__get(url)
        return status, res

    def get_customer_list(self, userid):
        """
        企业可通过此接口获取指定成员添加的客户列表。客户是指配置了客户联系功能的成员所添加的外部联系人。
        没有配置客户联系功能的成员，所添加的外部联系人将不会作为客户返回。
        :param userid:
        :return:
        """
        url = '{0}/externalcontact/list?access_token={1}&userid={2}'.format(self.url_prefix,
                                                                            self.access_token,
                                                                            userid)
        status, res = self.__get(url)
        return status, res

    def get_customer_detail(self, customerid):
        """
        企业可通过此接口，根据外部联系人的userid，拉取客户详情。
        :param customerid:
        :return:
        """
        url = '{0}/externalcontact/get?access_token={1}&external_userid={2}'.format(
            self.url_prefix, self.access_token, customerid)
        status, res = self.__get(url)
        return status, res

    def update_customer_remark(self, userid, customerid, **kwargs):
        """
        企业可通过此接口修改指定用户添加的客户的备注信息。
        :param userid:
        :param customerid:
        :param kwargs:
        :return:
        """
        url = '{0}/externalcontact/remark?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            'userid': userid,
            'external_userid': customerid,
        }
        data.update(kwargs)
        status, res = self.__post(url, data=data)
        return status, res

    #企业客户标签管理
    def get_corp_tag_list(self, tagid_li=None):
        """
        企业可通过此接口获取企业客户标签详情。
        :param tagid_li: 要查询的标签id，如果不填则获取该企业的所有客户标签，目前暂不支持标签组id
        :return:
        """
        url = '{0}/externalcontact/get_corp_tag_list?access_token={1}'.format(
            self.url_prefix, self.access_token)
        data = {}
        if tagid_li:
            data = {
                'tag_id': tagid_li
            }
        status, res = self.__post(url, data=data)
        return status, res

    # 管理标签
    def create_corp_tag(self, group_name, tagname_li):
        """
如果要向指定的标签组下添加标签，需要填写group_id参数；如果要创建一个全新的标签组以及标签，则需要通过group_name参数指定新标签组名称，如果填写的groupname已经存在，则会在此标签组下新建标签。
如果填写了group_id参数，则group_name和标签组的order参数会被忽略。
不支持创建空标签组。
标签组内的标签不可同名，如果传入多个同名标签，则只会创建一个。
        """
        url = '{0}/externalcontact/add_corp_tag?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            'group_name': group_name,
            'tag': []
            }
        for t in tagname_li:
            data['tag'].append({'name': t})

        myLogger.debug('tags to be created: {0}'.format(data))
        status, res = self.__post(url, data)
        return status, res

    def update_corp_tag(self, tagid, tagname, order=None):
        """
            更新标签名字
            参数	必须	说明
            access_token	是	调用接口凭证
            tagid	是	标签ID
            tagname	是	标签名称。长度为1~64个字符，标签不可与其他同组的标签重名，也不可与全局标签重名
        """
        url = '{0}/externalcontact/edit_corp_tag?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {"id": tagid, "name": tagname}
        if order:
            data['order'] = order
        status, res = self.__post(url, data)
        return status, res

    def delete_corp_tag(self, tagid_li, groupid_li=None):
        """
            删除标签
            参数	必须	说明
            access_token	是	调用接口凭证
            tagid	是	标签ID
        """
        url = '{0}/externalcontact/del_corp_tag?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            'tag_id': tagid_li
        }
        if groupid_li:
            data['group_id'] = groupid_li

        myLogger.debug('tags to be deleted: {0}'.format(data))
        status, res = self.__post(url, data)
        return status, res

    def mark_tag(self, userid, customerid, **kwargs):
        """
        企业可通过此接口为指定成员的客户添加上由企业统一配置的标签。
        :param userid:
        :param customerid:
        :param kwargs:
        :return:
        """
        url = '{0}/externalcontact/mark_tag?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            'userid': userid,
            'external_userid': customerid,
        }
        data.update(kwargs)
        status, res = self.__post(url, data=data)
        return status, res

    # 客户群管理
    def get_groupchat_list(self, status=0, userid_li=None, offset=0, limit=100):
        """
        企业和第三方服务商可通过此接口获取配置了客户联系功能的成员列表。
        :return:
        """
        url = '{0}/externalcontact/groupchat/list?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            "status_filter": status,
            "owner_filter": {
                "userid_list": userid_li or [],
            },
            "offset": offset,
            "limit": limit

        }
        status, res = self.__post(url, data=data)
        return status, res

    def get_groupchat_detail(self, chat_id):
        """
        企业可通过此接口，根据外部联系人的userid，拉取客户详情。
        :param customerid:
        :return:
        """
        url = '{0}/externalcontact/groupchat/get?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            'chat_id': chat_id
        }
        status, res = self.__post(url, data=data)
        return status, res

    # 群发消息
    def send_msg_to_multiuser(self, external_userid_li, msg_type='text', **kwargs):
        url = '{0}/externalcontact/add_msg_template?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            'chat_type': 'single',
            'external_userid': external_userid_li
        }

        if msg_type == 'text':
            data['text'] = {
                'content': kwargs.get('content')
            }
        elif msg_type == 'image':
            data['image'] = {
                'media_id': kwargs.get('media_id')
            }
        elif msg_type == 'link':
            data['link'] = {
                'title': kwargs.get('title'),
                'url': kwargs.get('url'),
                'desc': kwargs.get('desc', ''),
                'picurl': kwargs.get('picurl', '')
            }
        elif msg_type == 'miniprogram':
            data['miniprogram'] = {
                'title': kwargs.get('title'),
                'pic_media_id': kwargs.get('pic_media_id'),
                'appid': kwargs.get('appid'),
                'page': kwargs.get('page')
            }

        status, res = self.__post(url, data=data)
        return status, res

    def send_msg_to_groupchat(self, sender, msg_type='text', **kwargs):
        url = '{0}/externalcontact/add_msg_template?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            'chat_type': 'group',
            'sender': sender
        }

        if msg_type == 'text':
            data['text'] = {
                'content': kwargs.get('content')
            }
        elif msg_type == 'image':
            data['image'] = {
                'media_id': kwargs.get('media_id')
            }
        elif msg_type == 'link':
            data['link'] = {
                'title': kwargs.get('title'),
                'url': kwargs.get('url'),
                'desc': kwargs.get('desc', ''),
                'picurl': kwargs.get('picurl', '')
            }
        elif msg_type == 'miniprogram':
            data['miniprogram'] = {
                'title': kwargs.get('title'),
                'pic_media_id': kwargs.get('pic_media_id'),
                'appid': kwargs.get('appid'),
                'page': kwargs.get('page')
            }

        myLogger.debug('data:{0}'.format(data))
        status, res = self.__post(url, data=data)
        return status, res

    def get_group_msg_result(self, msg_id):
        url = '{0}/externalcontact/get_group_msg_result?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            'msgid': msg_id
        }

        status, res = self.__post(url, data)
        return status, res

    # 联系我
    def add_contact_way(self, userid_li, party_li=None, type=2, scene=2, style=1, remark='', skip_verify=True, state=''):
        url = '{0}/externalcontact/add_contact_way?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            'type': type,
            'scene': scene,
            'style': style,
            'remark': remark,
            'skip_verify': skip_verify,
            'state': state,
            'user': userid_li,
        }
        if party_li:
            data['party'] = party_li

        status, res = self.__post(url, data)
        myLogger.debug(res)
        return status, res

    def get_contact_way(self, config_id):
        url = '{0}/externalcontact/get_contact_way?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            'config_id': config_id
        }

        status, res = self.__post(url, data)
        return status, res

    def update_contact_way(self, config_id, **kwargs):
        url = '{0}/externalcontact/update_contact_way?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            'config_id': config_id
        }
        data.update(kwargs)

        status, res = self.__post(url, data)
        return status, res

    def del_contact_way(self, config_id):
        url = '{0}/externalcontact/del_contact_way?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            'config_id': config_id
        }

        status, res = self.__post(url, data)
        return status, res

    # 离职管理
    def get_unassigned_list(self):
        url = '{0}/externalcontact/get_unassigned_list?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            'page_id': 0,
            'page_size': 100
        }

        status, res = self.__post(url, data)
        return status, res

    def transfer_external_user(self, external_userid, handover_userid, takeover_userid):
        url = '{0}/externalcontact/transfer?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            'external_userid': external_userid,
            'handover_userid': handover_userid,
            'takeover_userid': takeover_userid
        }

        status, res = self.__post(url, data)
        return status, res

    def transfer_groupchat(self, chat_id_li, new_owner):
        url = '{0}/externalcontact/groupchat/transfer?access_token={1}'.format(self.url_prefix, self.access_token)
        data = {
            'chat_id_list': chat_id_li,
            'new_owner': new_owner
        }

        status, res = self.__post(url, data)
        return status, res

    # 群欢迎素材
    def get_group_welcome(self):
        pass



