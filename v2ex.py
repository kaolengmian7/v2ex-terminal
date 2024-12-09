import requests
from bs4 import BeautifulSoup
import sys
import os
import json
from datetime import datetime

class V2exCLI:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.topics = []  # 存储主题列表
        self.cache_file = 'v2ex_cache.json'  # 缓存文件路径
        self.load_cache()  # 初始化时加载缓存
        
    def save_cache(self):
        """保存主题列表到缓存文件"""
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'topics': self.topics
        }
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f'保存缓存失败: {e}', file=sys.stderr)

    def load_cache(self):
        """从缓存文件加载主题列表"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    self.topics = cache_data['topics']
                    print('已从缓存加载主题列表')
                    return True
        except Exception as e:
            print(f'读取缓存失败: {e}', file=sys.stderr)
        return False

    def clear_screen(self):
        """清空屏幕"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_topics(self):
        """显示主题列表"""
        self.clear_screen()
        print('\n主题列表:\n')
        for index, topic in enumerate(self.topics, 1):
            print(f'[{index}] 标题: {topic["title"]} {topic["reply"]}')
            print(f'    链接: {topic["url"]}')
            print('-' * 80)
    
    def get_topics(self):
        try:
            # 获取网页内容
            response = requests.get('https://www.v2ex.com/?tab=all', headers=self.headers)
            response.raise_for_status()
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有class为"cell item"的div
            items = soup.find_all('div', class_='cell item')
            
            # 清空之前的主题列表
            self.topics = []
            
            # 遍历并提取信息
            for index, item in enumerate(items, 1):
                topic_link = item.find('a', class_='topic-link')
                reply_count = item.find('a', class_=['count_livid', 'count_orange'])
                reply_text = f'[{reply_count.text} 回复]' if reply_count else '[0 回复]'
                
                if topic_link:
                    title = topic_link.text.strip()
                    url = 'https://www.v2ex.com' + topic_link['href']
                    # 存储主题信息
                    self.topics.append({'title': title, 'url': url, 'reply': reply_text})
            
            # 保存到缓存
            self.save_cache()
            
            # 显示主题列表
            self.display_topics()
                    
        except requests.RequestException as e:
            print(f'获取数据失败: {e}', file=sys.stderr)
            return False
        except Exception as e:
            print(f'解析数据失败: {e}', file=sys.stderr)
            return False
        return True

    def get_topic_detail(self, topic_index):
        try:
            # 检查索引是否有效
            if not (1 <= topic_index <= len(self.topics)):
                print('无效的主题编号!')
                return
            
            topic = self.topics[topic_index - 1]
            response = requests.get(topic['url'], headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取主题内容
            topic_content = soup.find('div', class_='topic_content')
            if topic_content:
                self.clear_screen()  # 清屏后显示详情
                print('\n' + '=' * 80)
                print(f"标题: {topic['title']}")
                print('-' * 80)
                print(topic_content.text.strip())
                print('=' * 80)
                
                # 等待用户输入 b 返回
                while True:
                    user_input = input('\n输入 b 返回主题列表: ').strip().lower()
                    if user_input == 'b':
                        # 返回主题列表时重新显示
                        self.display_topics()
                        return
            else:
                print('未找到主题内容')
                
        except requests.RequestException as e:
            print(f'获取主题详情失败: {e}')
        except Exception as e:
            print(f'解析主题详情失败: {e}')

    def handle_user_input(self, user_input):
        """处理用户输入的命令或主题编号"""
        command = user_input.lower().strip()
        
        # 命令处理
        if command == 'help':
            self.clear_screen()
            print('\n可用命令:')
            print('数字    - 输入主题编号查看详情')
            print('help    - 显示帮助信息')
            print('b       - 返回主题列表')
            print('>       - 查看下一页')
            print('<       - 查看上一页')
            print('r       - 刷新页面')
            print('q       - 退出程序\n')
        elif command == 'b':
            self.display_topics()
        elif command == '>':
            print('下一页功能待实现')  # TODO: 实现翻页功能
        elif command == '<':
            print('上一页功能待实现')  # TODO: 实现翻页功能
        elif command == 'r':
            self.clear_screen()
            print('\n刷新主题列表...\n')
            # 删除缓存文件
            if os.path.exists(self.cache_file):
                try:
                    os.remove(self.cache_file)
                    print('已删除缓存文件')
                except Exception as e:
                    print(f'删除缓存文件失败: {e}', file=sys.stderr)
            # 清空当前主题列表
            self.topics.clear()
            # 重新获取主题列表
            self.get_topics()
        elif command == 'q':
            self.clear_screen()
            return False
        else:
            try:
                topic_index = int(user_input)
                self.get_topic_detail(topic_index)
            except ValueError:
                print('请输入有效的主题编号或命令！输入 help 查看可用命令')
        
        return True

    def run(self):
        self.clear_screen()
        print('正在加载 V2EX 主题列表...\n')
        
        # 如果没有缓存或缓存加载失败，则获取新数据
        if not self.topics:
            if not self.get_topics():
                return
        else:
            self.display_topics()
        
        while True:
            try:
                user_input = input('\n输入主题编号查看详情，输入 help 查看所有命令，输入 q 退出: ').strip()
                if not self.handle_user_input(user_input):
                    break
            except KeyboardInterrupt:
                self.clear_screen()
                break
            except Exception as e:
                print(f'发生错误: {e}')

if __name__ == '__main__':
    cli = V2exCLI()
    cli.run() 