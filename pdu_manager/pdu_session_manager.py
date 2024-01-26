import requests
import asyncio
import aiohttp
from bs4 import BeautifulSoup

class PDUSessionManager:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.session_url = None  # For storing session-specific URL
        self.session = None
        self.username = username
        self.password = password
        self.login_path = "/Forms/login1"
        self.login_referer_path = "/logon.htm"
        self.logout_path = '/logout.htm'  # Simplified logout path
        self.outlet_path = "/outlctrl.htm"  # Path appended to session URL
        self.session_lock = asyncio.Lock()

    async def login(self):
        """
        Attempts to log into the PDU. If login fails due to an existing session, tries to logout and retry once.
        """
        self.session = aiohttp.ClientSession()

        login_url = f"{self.base_url}{self.login_path}"
        referer = f"{self.base_url}{self.login_referer_path}"
        data = {
            "login_username": self.username,
            "login_password": self.password,
        #    "submit": "Log On"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": referer
        }

        print(f"Logging into {login_url} as user {self.username}")

        async with self.session.post(login_url, data=data, headers=headers) as response:
            if response.status == 200:
                print("Login successful (200)")
                # Check response content for the specific error message
                soup = BeautifulSoup(await response.text(), 'html.parser')
                if 'Someone is currently logged' in soup.get_text():
                    print("Another user is logged in. Attempting to log out and retry...")
                    await self.logout()
                    async with self.session.post(login_url, data=data, headers=headers) as response:  # Retry login
                        if response.status != 200 or 'Someone is currently logged' in await response.text():
                            raise Exception("Login failed due to an active session by another user.")
                elif str(response.url).startswith(f"{self.base_url}/NMC/"):
                    self.session_url = str(response.url).rsplit('/', 1)[0]
                    print(f"Session url is {self.session_url}")
                else:
                    raise Exception("Failed to capture session-specific URL")
            else:
                raise Exception(f"Login failed with status code: {response.status} and response text {await response.text()}")


    async def logout(self):
        """
        Logs out of the PDU to free up the session.
        """
        if self.session:
            logout_url = f"{self.base_url}{self.logout_path}"
            try:
                print("Logging out")
                await self.session.get(logout_url)
            except requests.RequestException as e:
                print(f"Error during logout: {e}")
            finally:
                await self.session.close()
                self.session = None
                print("Session terminated")