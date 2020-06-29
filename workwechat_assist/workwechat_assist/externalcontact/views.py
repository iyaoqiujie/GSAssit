from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .WXBizMsgCrypt3 import WXBizMsgCrypt
import xml.etree.cElementTree as ET
import logging

# Create your views here.
myLogger = logging.getLogger('WWAssist.externalcontact')


class GSAssitCallBack(View):

    def get(self, request):
        sToken = "VXQPBVhnzWHbsneAlRPPgN3efdRW"
        sEncodingAESKey = "y45sA6Ag3W07DK2iELzuqEF2k5aRtCXjC7EDKdm1xS6"
        sCorpID = "wwcfaf880742304045"
        wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)

        params = request.GET

        #Verify request
#        sVerifyMsgSig = params.get('msg_signature', '')
#        sVerifyTimeStamp = params.get('timestamp', '')
#        sVerifyNonce = params.get('nonce', '')
#        sVerifyEchoStr = params.get('echostr', '')
#        myLogger.debug('[{0}], [{1}], [{2}], [{3}]'.format(sVerifyMsgSig, sVerifyTimeStamp,
#                                                           sVerifyNonce, sVerifyEchoStr))
#        ret, sEchoStr = wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce, sVerifyEchoStr)
#        if ret:
#            myLogger.error(('ERR: VerifyURL ret: {0}'.format(ret)))
#            return HttpResponse('ERR: VerifyURL ret: {0}'.format(ret))
#
#        myLogger.debug('EchoStr: {0}'.format(sEchoStr))
#        return HttpResponse(sEchoStr)

        sReqMsgSig = params.get('msg_signature')
        sReqTimeStamp = params.get('timestamp')
        sReqNonce = params.get('nonce')
        myLogger.debug('{0}, {1}, {2}'.format(sReqMsgSig, sReqTimeStamp, sReqNonce))
        sReqData = request.get_data(as_text=True)
        ret, sMsg = wxcpt.DecryptMsg(sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
        if ret:
            print("ERR: DecryptMsg ret: {0}".format(ret))
            return HttpResponse('ERR: VerifyURL ret: {0}'.format(ret))

        myLogger.debug(sMsg)
        # 解密成功，sMsg即为xml格式的明文
        # TODO: 对明文的处理
        # For example:
        xml_tree = ET.fromstring(sMsg)
        event = xml_tree.find('Event').text
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

    @csrf_exempt
    def post(self, request):
        myLogger.debug('Received post request')
        return HttpResponseBadRequest('仅支持GET请求')




gsassist_callback_view = GSAssitCallBack.as_view()
