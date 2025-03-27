import time
import pandas as pd
import re
import requests
import datetime
import matplotlib.pyplot as plt
from DrissionPage import ChromiumPage


class DouyinScraper:
    def __init__(self, input_file):
        self.input_file = input_file

    def read_user_list(self):
        """读取 Excel 或 txt 获取抖音用户名列表"""
        if self.input_file.endswith('.txt'):
            with open(self.input_file, 'r', encoding='utf-8') as f:
                users = [line.strip() for line in f if line.strip()]
        elif self.input_file.endswith('.xlsx'):
            df = pd.read_excel(self.input_file)
            users = df.iloc[:, 0].dropna().tolist()
        else:
            raise ValueError("仅支持 txt 或 Excel 文件！")
        return users

    def get_user_sec_id(self, username, page):
        """搜索用户并获取 sec_user_id"""
        page.ele('x://input[@data-e2e="searchbar-input"]').clear()
        page.ele('x://input[@data-e2e="searchbar-input"]').input(f'{username}\n')
        tab = page.latest_tab
        tab.ele('x://*[@data-key="user"]', timeout=50).click()
        tab2 = page.latest_tab
        href = tab2.ele('x://*[@class="search-result-card"]/a', timeout=50).attr('href')
        match = re.search(r'user/([a-zA-Z0-9_-]+)', href)
        return match.group(1) if match else None

    def fetch_videos(self, sec_user_id, username, cookies):
        """获取指定用户的所有视频数据"""
        data = []
        result = {'has_more': 1, 'max_cursor': 0}
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"}

        while result['has_more']:
            response = requests.get(
                "https://www.douyin.com/aweme/v1/web/aweme/post/",
                headers=headers,
                cookies=cookies,
                params={"max_cursor": result['max_cursor'], "aid": "6383", "sec_user_id": sec_user_id, "count": 50}
            )
            result = response.json()

            for video in result.get('aweme_list', []):
                video_data = {
                    'URL': video['share_url'],
                    'Title': video['desc'],
                    'Comment Count': video['statistics']['comment_count'],
                    'Share Count': video['statistics']['share_count'],
                    'Digg Count': video['statistics']['digg_count'],
                    'Collect Count': video['statistics']['collect_count'],
                    'Timestamp': datetime.datetime.fromtimestamp(video['create_time'])
                }
                data.append(video_data)
                print(f"标题: {video_data['Title']}, 评论数: {video_data['Comment Count']}, 分享数: {video_data['Share Count']}, 点赞数: {video_data['Digg Count']}, 收藏数: {video_data['Collect Count']}, 时间: {video_data['Timestamp']}")

        df = pd.DataFrame(data)
        df.to_csv(f'{username}.csv', index=False, encoding='utf-8-sig')
        return df

    def plot_trends(self, df, username):
        """生成并保存点赞数、评论数、分享数、收藏数趋势图"""
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df = df.sort_values('Timestamp')

        plt.figure(figsize=(10, 5))
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文乱码
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

        plt.plot(df['Timestamp'], df['Digg Count'], label='Likes')
        plt.plot(df['Timestamp'], df['Comment Count'], label='Comments')
        plt.plot(df['Timestamp'], df['Share Count'], label='Shares')
        plt.plot(df['Timestamp'], df['Collect Count'], label='Favorites')
        plt.xlabel('日期')
        plt.ylabel('数量')
        plt.title(f'{username} 视频趋势')
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid()
        plt.tight_layout()

        plt.savefig(f'{username}_趋势图.png')
        plt.close()

    def run(self):
        """主流程：批量获取用户数据并生成图表"""
        page = ChromiumPage()
        page.get('http://www.douyin.com/?recommend=1', retry=3, interval=2, timeout=5)
        cookies = {cookie['name']: cookie['value'] for cookie in page.cookies()}
        users = self.read_user_list()

        for username in users:
            print(f'正在处理用户：{username}...')
            sec_user_id = self.get_user_sec_id(username, page)
            if not sec_user_id:
                print(f'无法获取 {username} 的 sec_user_id，跳过...')
                continue
            df = self.fetch_videos(sec_user_id, username, cookies)
            self.plot_trends(df, username)
            print(f'{username} 处理完成，数据已保存！')

        print("所有用户处理完毕！")


# 运行爬虫
scraper = DouyinScraper('用户.txt')  # 可换成 txt 文件
scraper.run()
