import requests
import time

class DiscordAPI(object):
    __api = "https://discord.com/api/v9"

    def __init__(self, token, verify_token=True):
        self.token = token

        if verify_token:
            self._verify_token()
    
    def _request(self, method, path, payload=None):
        http = requests.request(method, f"{self.__api}{path}", headers={"Authorization": self.token}, json=payload)

        try:
            return http.json()
        except Exception:
            return http.text

    def _verify_token(self):
        user = self._request("GET", "/users/@me")
        if not "id" in user:
            raise DiscordInvalidToken("Invalid user token")

    def get_guilds(self):
        return self._request("GET", "/users/@me/guilds")

    def leave_guild(self, guild_id):
        return self._request("DELETE", f"/users/@me/guilds/{guild_id}")
    
    def delete_guild(self, guild_id):
        return self._request("POST", f"/guilds/{guild_id}/delete", {})
    
    def get_channels(self):
        return self._request("GET", "/users/@me/channels")
    
    def delete_channel(self, channel_id):
        return self._request("DELETE", f"/channels/{channel_id}?silent=false")
    
    def get_relationships(self):
        return self._request("GET", "/users/@me/relationships")
    
    def delete_relationship(self, relationship_id):
        return self._request("DELETE", f"/users/@me/relationships/{relationship_id}")


class DiscordInvalidToken(Exception):
    """Raises when user passes invalid Discord token."""
    pass


class PoliceRaid(DiscordAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def leave_guilds(self):
        guilds = self._request_wait(super().get_guilds)
        for guild in guilds:
            guild_id = guild["id"]
            is_guild_owner = guild["owner"]

            if is_guild_owner:
                self._request_wait(super().delete_guild, guild_id)
                continue

            self._request_wait(super().leave_guild, guild_id)
            time.sleep(1)
    
    def delete_channels(self):
        channels = self._request_wait(super().get_channels)
        for channel in channels:
            channel_id = channel["id"]
            self._request_wait(super().delete_channel, channel_id)
            time.sleep(1)
        
    def delete_relationships(self):
        relationships = self._request_wait(super().get_relationships)
        for relationship in relationships:
            relationship_id = relationship["id"]
            self._request_wait(super().delete_relationship, relationship_id)
            time.sleep(1)
    
    def _request_wait(self, func, *args, **kwargs):
        while True:
            try:
                response = func(*args, **kwargs)
            except Exception:
                time.sleep(1)
                continue
            
            if not type(response) in [dict, list, str]:
                raise Exception(f"Discord API returned unexpected data type. Data type: {type(response)} Data: {response}")
            
            if "retry_after" in response:
                retry_after = response["retry_after"]
                print(f"Ignore: Rate limited. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                continue
            
            return response


def main():
    import getpass
    try:
        token = getpass.getpass("Token: ").strip()

        if not token:
            print("Token is not set. Edit the file first.")
            return
        
        police = PoliceRaid(token)

        print(
            "\nYou are about to delete everything in your Discord account.\n" \
            "This includes friends, channels or dms and guilds. For more\n" \
            "informations, please read the notes below.\n\n" \

            "Note 1: This will remove everything in your relationships, this\n" \
            "        includes friends, friend requests and blocklisted users.\n\n" \
            
            "Note 2: This does not clear messages you've sent in channels\n" \
            "        neither in Discord's database.\n\n" \
            
            "Note 3: This will delete including guilds you own.\n\n" \

            "Note 4: The author of this program will never be responsible for\n" \
            "        any consequences of your actions. Please proceed with risk.\n\n" \

            "Note 5: This will first delete all your friends to your channels\n" \
            "        and finally your guilds.\n\n" \

            "This action is irreversible, thus it requires your verification.\n"
        )

        try:
            verify_input = input("Please verify [Y/n]: ").lower()[0]
        except Exception:
            print("\nNo input has been declared. Assuming user is unsure. Quitting...")
            return
        
        if not verify_input == "y":
            return
        
        print("\nInitializing p0l1c3-r41d...")
        police.delete_relationships()
        police.delete_channels()
        police.leave_guilds()
        print("Successfully deleted everything.")
    except KeyboardInterrupt:
        return
    except DiscordInvalidToken as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()
