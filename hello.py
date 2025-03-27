import time
from DrissionPage import ChromiumPage,ChromiumOptions
import pandas as pd
from queue import Queue
import re
import requests
import datetime

class Douyin():
    def __init__(self):
        self.comment_queue=Queue()
    def login(self):
        # 创建多个页面对象
        # 创建浏览器配置对象，指定浏览器路径
        # co=ChromiumOptions().set_paths(local_port=9121,user_data_path=r'D:\data2')
        # co.set_proxy('140.250.146.122:54442')
        # 用该配置创建页面对象
        page=ChromiumPage()
        page.get('http://www.douyin.com/?recommend=1',retry=3,interval=2,timeout=5)
        # page.clear_cache()
        print('请于30秒内扫码登录')
        time.sleep(30)
        self.check(page)
    def check(self,page):
        choose=['王东来']
        for m in choose:
            # //*[@id="douyin-header"]/div[1]/header/div/div/div[1]/div/div[2]/div/div[1]/input
            #page.ele('x://*[@id="douyin-header"]/div[1]/header/div/div/div[1]/div/div[2]/div/div[1]/value()').clear()
            page.ele('x://input[@data-e2e="searchbar-input"]').clear()
            page.ele('x://*[@id="douyin-header"]/div[1]/header/div/div/div[1]/div/div[2]/div/div[1]/input').input('{}\n'.format(m))
            tab=page.latest_tab
            # print(tab.title)
            tab.ele('x:(//*[@class="search-result-card"])[1]').click()
            #tab2=page.latest_tab
            tab3=page.ele('x:// *[ @ id = "waterfall_item_2651651389003966"] / div / div / div / div[1] / div / a').attr('href')
            pattern=r'user/([a-zA-Z0-9_-]+)'
            print(tab3)
            # 使用re.search查找匹配项
            match=re.search(pattern,tab3)
            # 如果找到匹配项，打印结果
            if match:
                print("匹配到的用户ID：",match.group(1)) # 使用group（1）来获取第一个括号内匹配的内容
            else:
                print("没有找到匹配项")
            sec_user_id=match.group(1)
            self.parse(page,sec_user_id,m)
    def parse(self,page,sec_user_id,m):
        result={}
        data=[]
        result['has_more']=1
        result['max_cursor']=0
        while result['has_more']==1:
            max_cursor=result['max_cursor']
            headers={"user-agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36"}
            #cookies=page.cookies()
            # 获取cookies
            cookies_list = page.cookies()

            # 转换为requests需要的字典格式
            cookies = {cookie['name']: cookie['value'] for cookie in cookies_list}


            url="https://www.douyin.com/aweme/v1/web/aweme/post/"
            params={"max_cursor":max_cursor,
                    "aid":"6383",
                    "sec_user_id":sec_user_id,
                    "count":10000,
                    "publish_video_strategy_type":"2",}
            response=requests.get(url,headers=headers,cookies=cookies,params=params)
            # print(response.text)
            # print(response)

            result=response.json()
            # 视频链接
            length=len(result['aweme_list'])
            for i in range(length):
                # 完整url
                url=result['aweme_list'][i]['share_url']
                awesome_id=result['aweme_list'][i]['aweme_id']
                # 标题
                title=result['aweme_list'][i]['desc']
                # 评论数
                comment=result['aweme_list'][i]['statistics']['comment_count']
                # 分享数
                share=result['aweme_list'][i]['statistics']['share_count']
                # 喜欢
                digg= result['aweme_list'][i]['statistics']['digg_count']
                # 收藏
                collect=result['aweme_list'][i]['statistics']['collect_count']
                timestamp=result['aweme_list'][i]['create_time']
                dt_object=datetime.datetime.fromtimestamp(timestamp)
                print(title,awesome_id,share,digg,collect,comment,dt_object)
                # 将每条记录作为一个字典添加到列表中
                data.append({'博主':m,
                             'URL':url,
                             'Awesome ID':awesome_id,
                             'Title':title,
                             'Comment Count':comment,
                             'Share Count':share,
                             'Digg Counet':digg,
                             'Collect Count':collect,
                             'timestamp':dt_object})
                df=pd.DataFrame(data)
                df.to_csv('Douyin{}.csv'.format((m)),index=False,encoding='utf-8-sig')
    def inits(self):
        m=input("是否登录，0or1\n")
        if m=='0':
            self.login()
        else:
            # 创建浏览器配置对象，指定浏览器路径
            # co=ChromiumOptions().set_paths(local_port=9111,user_data_path=r'D:\data1')
            # 用该配置创建页面对象
            page=ChromiumPage()
            page.get('https://www.douyin.com/?recommend=1',retry=3,interval=2,timeout=5)
            self.check(page)



douyin=Douyin()
douyin.inits()




