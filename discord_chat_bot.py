import os
import random
import time
from typing import Dict, List, Optional, Any

import requests
from dotenv import load_dotenv
from loguru import logger


class DiscordChatBot:
    """Discord聊天机器人，使用GPT API自动回复消息"""

    def __init__(self):
        """初始化机器人配置"""
        self._load_config()
        self._setup_headers()

    def _load_config(self) -> None:
        """从环境变量加载配置"""
        load_dotenv()
        try:
            self.token = os.getenv('DcToken')
            self.channel_id = os.getenv('ChannelId')
            self.language = os.getenv('Language', '').lower()
            self.gpt_key = os.getenv('GptKey')
            self.max_sleep = int(os.getenv('MaxSleep', '60'))
            self.min_sleep = int(os.getenv('MinSleep', '30'))
            self.dc_id = os.getenv('YourID')
            self.is_wait = os.getenv('IsWait', '').lower()
            self.my_demand = os.getenv('MyDemand', '').lower()
            self.max_loop = int(os.getenv('MaxLoop', '5'))
            self.is_wait_time = int(os.getenv('IsWaitTime', '300'))

            # 验证配置
            self._validate_config()
        except (ValueError, TypeError) as e:
            logger.error(f"配置加载错误: {str(e)}")
            raise

    def _validate_config(self) -> None:
        """验证配置的有效性"""
        if not all([self.token, self.channel_id, self.gpt_key, self.dc_id]):
            raise ValueError("缺少必要的配置参数")

        if self.max_sleep < self.min_sleep:
            raise ValueError('间隔时间设置错误: 最大时间小于最小时间')

        if self.is_wait not in ['yes', 'no']:
            raise ValueError('IsWait设置错误,只有 yes / no 两个选项!')

        if self.language not in ['english', 'chinese']:
            raise ValueError('AI回复语言设置错误,请设置为english或chinese')

    def _setup_headers(self) -> None:
        """设置请求头"""
        self.headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "authorization": self.token,
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

        self.chat_language = '英文' if self.language == 'english' else '中文'

    def get_history(self) -> Optional[List[Dict[str, Any]]]:
        """获取频道历史消息"""
        url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages"
        querystring = {"limit": "50"}

        try:
            response = requests.get(url, headers=self.headers, params=querystring, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"获取历史消息失败: {str(e)}")
            return None

    def send_message(self, message: str) -> bool:
        """发送消息到Discord频道"""
        url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages"
        payload = {
            "mobile_network_type": "unknown",
            "content": message,
            "tts": False,
            "flags": 0
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            return '"type":0' in response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"发送消息失败: {str(e)}")
            return False

    def chat_with_gpt(self, user_message: str) -> Optional[str]:
        """使用GPT API生成回复"""
        url = "https://api.gpt.ge/v1/chat/completions"
        gpt_headers = {
            "Authorization": f"Bearer {self.gpt_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": user_message}],
            "max_tokens": 30,
            "temperature": 1.1,
        }

        try:
            response = requests.post(url, headers=gpt_headers, json=data, timeout=600)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"GPT API调用失败: {str(e)}")
            return None

    def prepare_prompt(self, messages: List[Dict[str, Any]]) -> tuple[str, bool]:
        """准备发送给GPT的提示词并检查是否可以回复"""
        prompt = (f'我这里有几十条聊天纪录依次给你列出来了，我想你帮我回复一句话，承接他们的内容，要求如下：{self.my_demand}，用{self.chat_language}回复\n')
        message_count = 0
        can_reply = True
        for i in range(min(50, len(messages))):
            message_data = messages[-1 * i - 1]
            chat_message = message_data.get('content', '')

            # 检查是否为普通消息且不包含特殊字符
            if message_data.get('type') == 0 and all(char not in chat_message for char in '<>@'):
                message_count += 1
                user_id = message_data.get('author', {}).get('id')

                # 检查是否需要等待（用户ID在最近消息中）
                if self.is_wait == 'yes' and user_id == self.dc_id:
                    can_reply = False

                prompt += f'{message_count}:{chat_message}\n'

            # 检查是否为回复消息
            elif message_data.get('type') == 19 and message_data.get('mentions'):
                other_user_id = message_data.get('mentions', [{}])[0].get('id')
                if self.is_wait == 'yes' and other_user_id == self.dc_id:
                    can_reply = False

        return prompt, can_reply

    @staticmethod
    def format_reply(reply: Optional[str]) -> Optional[str]:
        """格式化GPT的回复"""
        if not reply:
            return None

        if '-' in reply:
            reply.replace('-', ' ')

        # 处理回复末尾的句号并转为小写
        if reply.endswith('.'):
            return reply[:-1].lower()
        return reply.lower()

    def run(self) -> None:
        """运行聊天机器人"""
        chat_success = 0

        while chat_success < self.max_loop:
            # 获取历史消息
            messages = self.get_history()
            if not messages:
                logger.error('获取历史聊天失败...')
                return

            # 准备提示词并检查是否可以回复
            prompt, can_reply = self.prepare_prompt(messages)

            if not can_reply:
                logger.warning(f'设置中的ID还在前50条消息中,停止本次聊天,{self.is_wait_time}秒后再试...')
                time.sleep(self.is_wait_time)
                continue

            # 获取GPT回复
            gpt_response = self.chat_with_gpt(prompt)
            if not gpt_response:
                logger.error('AI聊天有误，即将重新拉取聊天...')
                continue

            # 格式化并发送回复
            formatted_reply = self.format_reply(gpt_response)
            if self.send_message(formatted_reply):
                logger.success(f'AI聊天完成! Text: [{formatted_reply}] already sent...')
                chat_success += 1
            else:
                logger.error(f'AI聊天失败! {formatted_reply}')

            # 如果还有更多循环，等待随机时间
            if chat_success < self.max_loop:
                sleep_time = random.randint(self.min_sleep, self.max_sleep)
                logger.info(f'Chat will after {sleep_time} sec to continue...')
                time.sleep(sleep_time)

        logger.success(f'Chat Target Already Done!!!')


def main():
    """主函数"""
    try:
        bot = DiscordChatBot()
        bot.run()
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")


if __name__ == '__main__':
    main()
