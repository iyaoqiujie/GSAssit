from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework import permissions, authentication
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.decorators import action, api_view, permission_classes
import logging

from .serializers import UserSerializer

User = get_user_model()
myLogger = logging.getLogger('WWAssist.user')


#class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    #lookup_field = "username"

    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_staff:
            return User.objects.all()

        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False, methods=["GET"])
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def work_wx_login(request):
    result = {'result': 'OK', 'msg': ''}
    params = request.GET

    code = params.get('code', 'CODE')
    state = params.get('state', 'STATE')

    myLogger.info('code:{0}, state:{1}'.format(code, state))
    return Response(result, status=status.HTTP_200_OK)




