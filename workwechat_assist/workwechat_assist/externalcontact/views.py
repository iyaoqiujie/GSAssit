from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.decorators import method_decorator
from .WXBizMsgCrypt3 import WXBizMsgCrypt
import xml.etree.cElementTree as ET
import logging

# Create your views here.
myLogger = logging.getLogger('WWAssist.externalcontact')


class GSAssitCallBack(View):

    def get(self, request):
        sToken = "mLOLPDZdSVqAMCxFEFu7DRBeU7HK"
        sEncodingAESKey = "GrVwDhSRfY4k2tjfVwcmjd3aqcAawbNsHqVYk3MQeNM"
        sCorpID = "wwcfaf880742304045"
        wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)

        params = request.GET

        #Verify request
        sVerifyMsgSig = params.get('msg_signature', '')
        sVerifyTimeStamp = params.get('timestamp', '')
        sVerifyNonce = params.get('nonce', '')
        sVerifyEchoStr = params.get('echostr', '')
        myLogger.debug('[{0}], [{1}], [{2}], [{3}]'.format(sVerifyMsgSig, sVerifyTimeStamp,
                                                           sVerifyNonce, sVerifyEchoStr))
        ret, sEchoStr = wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce, sVerifyEchoStr)
        if ret:
            myLogger.error(('ERR: VerifyURL ret: {0}'.format(ret)))
            return HttpResponse('ERR: VerifyURL ret: {0}'.format(ret))

        myLogger.debug('EchoStr: {0}'.format(sEchoStr))
        return HttpResponse(sEchoStr)

    @method_decorator(csrf_exempt)
    def post(self, request):
        sToken = "mLOLPDZdSVqAMCxFEFu7DRBeU7HK"
        sEncodingAESKey = "GrVwDhSRfY4k2tjfVwcmjd3aqcAawbNsHqVYk3MQeNM"
        sCorpID = "wwcfaf880742304045"
        wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)

        params = request.GET
        sReqMsgSig = params.get('msg_signature')
        sReqTimeStamp = params.get('timestamp')
        sReqNonce = params.get('nonce')
        myLogger.debug('{0}, {1}, {2}'.format(sReqMsgSig, sReqTimeStamp, sReqNonce))
        myLogger.debug('body:{0}'.format(request.body))
        sReqData = request.body
        ret, sMsg = wxcpt.DecryptMsg(sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
        if ret:
            myLogger.error("ERR: DecryptMsg ret: {0}".format(ret))
            return HttpResponse('ERR: VerifyURL ret: {0}'.format(ret))

        myLogger.debug(sMsg)
        # 解密成功，sMsg即为xml格式的明文
        # TODO: 对明文的处理
        # For example:
        xml_tree = ET.fromstring(sMsg)
        event = xml_tree.find('Event').text
        changeType = xml_tree.find('ChangeType').text
        myLogger.debug('Event: [{0}], type:[{1}]'.format(event, changeType))
        
        if event == 'change_external_contact' and xml_tree.find('ChangeType').text == 'add_external_contact':
            userid = xml_tree.find('UserID').text
            externaluserid = xml_tree.find('ExternalUserID').text

            state = xml_tree.find('State').text
            welcomecode = xml_tree.find('WelcomeCode').text
            myLogger.debug('{0}, {1}, {2}, {3}'.format(userid, externaluserid, state, welcomecode))
        return HttpResponse('OK')

        # state = xml_tree.find('State').text
        # fromUser = xml_tree.find('FromUserName').text
        # content = xml_tree.find("Content").text
        # print('from:[{0}], context:[{1}]'.format(fromUser, content))




gsassist_callback_view = GSAssitCallBack.as_view()
