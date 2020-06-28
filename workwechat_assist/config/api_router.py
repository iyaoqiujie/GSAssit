from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from workwechat_assist.users.api.views import UserViewSet
from workwechat_assist.corporation.api.views import CorporationViewSet, CorpAppViewSet, DepartmentViewSet, \
    MemberViewSet, TagViewSet
from workwechat_assist.externalcontact.api.views import ContactMeViewSet, CustomerViewSet, \
    CustomerFollowUserRelationshipViewSet, TagGroupViewSet, TagViewSet, GroupChatViewSet, GroupMessageViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register('users', UserViewSet)
router.register('corp', CorporationViewSet)
router.register('corpapp', CorpAppViewSet)
router.register('department', DepartmentViewSet)
router.register('member', MemberViewSet)
router.register('mtag', TagViewSet)
router.register('contactme', ContactMeViewSet)
router.register('customer', CustomerViewSet)
router.register('cfurel', CustomerFollowUserRelationshipViewSet)
router.register('taggroup', TagGroupViewSet)
router.register('tag', TagViewSet)
router.register('groupchat', GroupChatViewSet)
router.register('groupmsg', GroupMessageViewSet)


app_name = 'api'
urlpatterns = router.urls
