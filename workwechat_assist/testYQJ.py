# -*- coding: utf-8 -*-
# Author：Qiujie Yao
# Email: yaoqiujie@gscopetech.com
# @Time: 2020/6/18 9:07 上午

#!/usr/bin/env python
import os
import sys
import mimetypes
from pathlib import Path
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
import django
django.setup()
from workwechat_assist.utils.workwechat_sdk import WorkWechat
from workwechat_assist.corporation.models import Corporation, CorpApp, Department, Member, \
    DepartmentMemberRelationShip, Tag

if __name__ == '__main__':
    corp = Corporation.objects.get(id=1)
    #app = CorpApp.objects.get(corp=corp, agent_id='crm')
    app = CorpApp.objects.get(id=1)
    w = WorkWechat(app)

    #status, res = w.get_follow_user_list()
    #status, res = w.get_customer_list('YaoQiuJie')
    #status, res = w.get_customer_detail('wmb82tCgAAgT9Vbtc3GSpJMrQ2r5Ga3Q')
    #status, res = w.get_corp_tag_list()
    #status, res = w.create_corp_tag('北京展会', ['周一', '周二'])
    #status, res = w.delete_corp_tag(['etb82tCgAiwfsRk1ro4cZMMKWkAA', ])
    #status, res = w.get_groupchat_detail('wrb82tCgAAG_wMhrloPU4wkfcq92X7UQ')

    #status, res = w.send_msg_to_groupchat('YaoQiuJie', msg_type='text', content='Greetings from Django')
    #status, res = w.send_msg_to_multiuser(external_userid_li=['wmb82tCgAAsSbiFIIYcO_T-_ZVi3T4vw',], msg_type='text', content='Greetings from Django')
    #status, res = w.get_group_msg_result('msgb82tCgAAgrXmwKrDqNIeY8QGlM5HNA')
    #status, res = w.get_contact_way("8ce274acc7e3592307bd6c9403a4b740")
    status, res = w.get_contact_way("8ce274acc7e3592307bd6c9403a4b740")
    #status, res = w.get_unassigned_list()
    #status, res = w.transfer_external_user('wmb82tCgAA6-zMo6u9fSkU6gN0IRWRWQ', 'LinDa-Shang', 'GuoDan')

    # Department
    #status, res = w.get_users_in_department_detail(2)
    print(status)
    print(res)

    # Material
#    filepath = '/Users/yqj/Downloads/IMG_8609.jpg'
#    filename = os.path.basename(filepath)
#    content_type = mimetypes.guess_type(filepath)[0]
#    filedata = open(filepath, 'rb')
#    media_file = (filename, filedata, content_type)
#    status, res = w.upload_media('image', media_file)
#    print(status)
#    print(res)
    #img_file = w.get_media('3U19BA1rF6OQ8mT5SVZMVQI66dOrZMS-dY3KubR_iPQw1G8o0_X8pLLLyye3JANxC')
    #print(img_file)



