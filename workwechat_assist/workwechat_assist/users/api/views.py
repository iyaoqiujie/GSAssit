from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework import permissions, authentication
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from workwechat_assist.utils.workwechat_sdk import WorkWechat
from workwechat_assist.corporation.models import CorpApp, Corporation
from config.settings.base import AGENT_ID
import logging

from .serializers import UserSerializer, UserRegSerializer
from .permissions import IsOwnerOrReadOnly

User = get_user_model()
myLogger = logging.getLogger('WWAssist.user')


#class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'username', 'mobile', 'nickName', 'openid')
    ordering_fields = ('last_login', 'date_joined')

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegSerializer
        else:
            return UserRegSerializer

    def get_permissions(self):
        if self.action == "create" or self.action == 'wx_login':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsOwnerOrReadOnly | permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_staff:
            return User.objects.all()

        return self.queryset.filter(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["username"] = user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=["GET"])
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def work_wx_login(request):
    result = {'result': 'FAIL', 'msg': '', 'code': 20000}
    code = request.data.get('code', 'CODE')
    state = request.data.get('state', 'STATE')

    myLogger.info('code:{0}, state:{1}'.format(code, state))

    try:
        corp = Corporation.objects.get(id=1)
    except Corporation.DoesNotExist:
        myLogger.error('公司不存在')
        result['message'] = '公司不存在'
        return Response(result)

    try:
        myapp = CorpApp.objects.get(corp=corp, agent_id=AGENT_ID)
    except CorpApp.DoesNotExist:
        myLogger.error('应用获取失败')
        result['message'] = '应用获取失败'
        return Response(result)

    wechat = WorkWechat(myapp)

    sts, res = wechat.get_userid(code)
    if not sts:
        result['message'] = res.get('errmsg')
        return Response(result)
    myLogger.debug(res)
    userid = res.get('UserId')
    sts, res = wechat.get_user(userid)
    if not sts:
        result['message'] = res.get('errmsg')
        return Response(result)

    myLogger.debug(res)
    # The account is not in active state
    if res.get('status') != 1:
        result['message'] = 'account[{0}] is not in active state'.format(res.get('userid'))
        return Response(result)

    user, created = User.objects.get_or_create(username=res.get('userid'))
    if created:
        user.name = res.get('name')
        user.mobile = res.get('mobile')
        user.gender = res.get('gender')
        user.avatarUrl = res.get('avatar')
        user.email = res.get('email')
        user.is_staff = True
        user.save()

    payload = jwt_payload_handler(user)
    result['token'] = jwt_encode_handler(payload)
    result['id'] = user.id
    result['name'] = user.name
    result['username'] = user.username
    result['mobile'] = user.mobile
    result['email'] = user.email
    result['roles'] = 'admin' #TODO
    result['nickName'] = user.nickName
    result['avatar'] = res.get('thumb_avatar')
    result['avatarUrl'] = user.avatarUrl
    result['result'] = 'OK'

    return Response(result, status=status.HTTP_200_OK)


