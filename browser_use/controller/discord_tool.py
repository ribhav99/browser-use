import time
import random
import os
import requests
from datetime import datetime, timedelta, timezone


class DiscordAPI:
    def __init__(self, token=None):
        self.token = token if token else os.getenv("DISCORD_TOKEN")
        self.base_url = "https://discord.com/api/v10"
        self.headers = {
            "Authorization": f"{self.token}",
            "Content-Type": "application/json",
        }

    def get_user_info(self):
        response = requests.get(f"{self.base_url}/users/@me", headers=self.headers)
        return response.json()

    def get_guilds(self):
        response = requests.get(
            f"{self.base_url}/users/@me/guilds", headers=self.headers
        )
        return response.json()

    def get_channels(self, guild_id):
        response = requests.get(
            f"{self.base_url}/guilds/{guild_id}/channels", headers=self.headers
        )
        return response.json()

    def get_messages(self, channel_id, before=None, limit=100):
        time.sleep(random.randint(1, 7) / 20)
        params = {"limit": limit}
        if before:
            params["before"] = before
        response = requests.get(
            f"{self.base_url}/channels/{channel_id}/messages",
            headers=self.headers,
            params=params,
        )
        return response.json()

    def get_messages_until(self, channel_id, timespan: timedelta):
        until = datetime.now(timezone.utc) - timespan
        all_messages = []
        before = None
        idx = 0
        while True:
            messages = self.get_messages(channel_id, before=before, limit=100)
            if not messages or type(messages) != list:
                print(f"No more messages found for channel {channel_id}")
                break
            idx += 1
            print(f"Got {len(messages)} messages (round {idx})")
            all_messages.extend(messages)
            timestamp = datetime.fromisoformat(messages[-1]["timestamp"])
            before = messages[-1]["id"]
            if timestamp < until:
                print(f"Got till {timestamp} which is before {until}")
                break
        return all_messages

    def get_messages_since(self, channel_id, start_date: datetime):
        """Get all messages in a channel since the given date"""
        timespan = datetime.now(start_date.tzinfo) - start_date
        return self.get_messages_until(channel_id, timespan)

    def get_timestamp_from_message_id(self, message_id: str, timezone: timezone = timezone.utc) -> datetime:
        """
        Convert a Discord message ID (snowflake) to a datetime object.
        
        Args:
            message_id (str): The Discord message ID/snowflake
            
        Returns:
            datetime: The timestamp when the message was created
        """
        DISCORD_EPOCH = 1420070400000
        timestamp = ((int(message_id) >> 22) + DISCORD_EPOCH) / 1000
        return datetime.fromtimestamp(timestamp, tz=timezone)

    def get_last_24_hours_messages(self, guild_id):
        channels = self.get_channels(guild_id)
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        all_messages = []

        for channel in channels:
            if channel["type"] == 0:  # Text channel
                try:
                    messages = self.get_messages(channel["id"])
                    if not isinstance(messages, list):
                        print(
                            f"Unexpected response for channel {channel['id']}: {messages}"
                        )
                        continue

                    for message in messages:
                        if not isinstance(message, dict):
                            print(
                                f"Unexpected message format in channel {channel['id']}: {message}"
                            )
                            continue

                        try:
                            message_time = datetime.fromisoformat(
                                message["timestamp"].rstrip("Z")
                            ).replace(tzinfo=timezone.utc)
                            if message_time > yesterday:
                                all_messages.append(
                                    {
                                        "id": message["id"],
                                        "content": message["content"],
                                        "author": {
                                            "id": message["author"]["id"],
                                            "username": message["author"]["username"],
                                            "global_name": message["author"].get(
                                                "global_name"
                                            ),
                                        },
                                        "timestamp": message["timestamp"],
                                        "channel_name": channel["name"],
                                    }
                                )
                        except KeyError as e:
                            print(f"Missing key in message data: {e}")
                        except ValueError as e:
                            print(f"Error parsing timestamp: {e}")

                except Exception as e:
                    print(f"Error processing channel {channel['id']}: {e}")

        return all_messages

    def get_dm_channels(self):
        response = requests.get(
            f"{self.base_url}/users/@me/channels", headers=self.headers
        )
        dm_channels = response.json()
        return dm_channels

    def get_private_dms(self):
        dm_channels = self.get_dm_channels()

        all_dms = []
        for channel in dm_channels:
            if channel["type"] == 1:  # DM channel
                messages = self.get_messages(channel["id"])
                all_dms.extend(messages)

        return all_dms

    def clean_message(self, message, include_attachments=True, include_reactions=True, include_embeds=True, include_deleted=False):
        """Clean and format a Discord message with configurable options"""
        if not include_deleted and message.get("flags", 0) & (1 << 2):  # Message was deleted
            return None
            
        cleaned = {
            "id": message["id"],
            "content": message["content"],
            "author": {
                "id": message["author"]["id"],
                "username": message["author"]["username"],
                "global_name": message["author"].get("global_name"),
            },
            "timestamp": message["timestamp"],
        }
        
        if include_attachments and message.get("attachments"):
            cleaned["attachments"] = [{
                "id": att["id"],
                "filename": att["filename"],
                "url": att["url"],
                "content_type": att.get("content_type"),
                "size": att.get("size")
            } for att in message["attachments"]]
            
        if include_reactions and message.get("reactions"):
            cleaned["reactions"] = [{
                "emoji": reaction["emoji"],
                "count": reaction["count"],
                "me": reaction.get("me", False)
            } for reaction in message["reactions"]]
            
        if include_embeds and message.get("embeds"):
            cleaned["embeds"] = message["embeds"]
            
        return cleaned