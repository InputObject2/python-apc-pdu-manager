from pdu_session_manager import PDUSessionManager
from pdu_outlet import PDUOutlet
from typing import List, Union
from bs4 import BeautifulSoup


class PDUOutletManager:
    def __init__(self, session_manager: PDUSessionManager):
        self.session_manager = session_manager
        self.outlets = []  # List of PDUOutlet instances

    async def set_outlet_power_state(self, outlets: Union[PDUOutlet, List[PDUOutlet]], state):
        actions = {'on': '2', 'off': '4'}  # 'on immediate' and 'off immediate'
        action_value = actions[state.lower()]

        # If a single outlet is passed, wrap it in a list
        if isinstance(outlets, PDUOutlet):
            outlets = [outlets]

        # First, perform a GET request to check if the session is still active
        outlet_control_url = f"{self.session_manager.session_url}/outlctrl.htm"

        async with self.session_manager.session.get(outlet_control_url) as response:
            response_text = await response.text()  # Correctly get the response text
            if response.status != 200 or "login" in response_text.lower():
                await self.session_manager.login()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            'Referer': outlet_control_url,
        }

        post_data = [
            ('rPDUOutletCtrl', action_value),
            ('submit', 'Next>>')
        ]

        for outlet in outlets:
            post_data.append((outlet.checkbox_name, outlet.checkbox_value))

        print(f"Setting outlets {outlets} to {state.lower()}")
        # URL for the outlet control action
        outlet_control_form = f"{self.session_manager.session_url}/Forms/outlctrl1"
        async with self.session_manager.session.post(outlet_control_form, data=post_data, headers=headers, allow_redirects=True) as response:
            if response.status != 200:
                raise Exception(f"Outlet configuration POST request failed. Status code: {response.status}")

        print("Configuration sent")
        confirmation_form_url = f"{self.session_manager.session_url}/Forms/rpduconf1"
        referer = f"{self.session_manager.session_url}/rpduconf.htm"

        confirmation_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            'Referer': referer,
            'Origin': self.session_manager.base_url
            }

        # POST data for the confirmation form
        confirm_post_data = [
            ('submit', 'Apply'),
            ('Control', '')
        ]

        # Second POST request for confirmation
        async with self.session_manager.session.post(confirmation_form_url, data=confirm_post_data, headers=confirmation_headers, allow_redirects=True) as confirm_response:
            if confirm_response.status != 200:
                raise Exception(f"Confirmation POST request failed. Status code: {confirm_response.status}")

        print("Configuration confirmed")

    async def fetch_outlets(self):
        # remove the previously known outlets
        self.outlets = []
        outlet_control_url = f"{self.session_manager.session_url}/outlctrl.htm"
        print(f"Fetching outlets on endpoint {outlet_control_url}")

        async with self.session_manager.session.get(outlet_control_url) as response:
            if response.status != 200:
                raise Exception("Failed to fetch outlet control page.")

            soup = BeautifulSoup(await response.text(), 'html.parser')

            # Extract the necessary form data
            form = soup.find('form', {'name': 'HashForm1'})
            table_rows = form.find_all('tr')

            # Find the first row that contains 'th' elements and count outlets per row
            outlets_per_row = 0
            for row in table_rows:
                if row.find('th'):
                    outlets_per_row = sum('Outlet' in th.get_text() for th in row.find_all('th'))
                    break  # Exit loop after finding the header row

            if outlets_per_row == 0:
                raise Exception("Unable to determine the number of outlets per row.")

            #print(f"We have {outlets_per_row} outlets per row")

            # Iterate over rows to find the one with the nested tbody containing the outlets
            for row in table_rows:
                nested_td = row.find('td')
                if nested_td:
                    nested_tbody = nested_td.find('table')
                    if nested_tbody:
                        #print("Found outlet table")
                        outlet_rows = nested_tbody.find_all('tr')
                        for outlet_row in outlet_rows[1:]:  # Skip header row
                            cells = outlet_row.find_all('td')
                            outlet_td_count = 4  # Number of 'td' elements per outlet
                            separator_td_count = 1  # Number of 'td' elements used as separators between outlets

                            # Calculate the total number of outlets in the row
                            total_outlets = (len(cells) + separator_td_count) // (outlet_td_count + separator_td_count)

                            # Iterate over each outlet in the row
                            for i in range(total_outlets):
                                cell_base = i * (outlet_td_count + separator_td_count)
                                checkbox = cells[cell_base].find('input', type='checkbox')
                                if checkbox:
                                    status = cells[cell_base + 1].get_text(strip=True)
                                    outlet_name = cells[cell_base + 3].get_text(strip=True)
                                    outlet = PDUOutlet(
                                        name=outlet_name,
                                        status=status,
                                        checkbox_name=checkbox.get('name'),
                                        checkbox_value=checkbox.get('value')
                                    )
                                    print(f"Found {outlet.name}: {outlet.status} ({outlet.checkbox_name}/{outlet.checkbox_value})")
                                    self.outlets.append(outlet)
                        break  # Exit loop after processing the nested tbody
