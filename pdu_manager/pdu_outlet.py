class PDUOutlet:
    def __init__(self, name: str, status: str, checkbox_name: str, checkbox_value: str):
        self.name = name
        self.status = status
        self.checkbox_name = checkbox_name
        self.checkbox_value = checkbox_value

    def __repr__(self):
        return f"Outlet(name='{self.name}', status='{self.status}')"

    def get_control_data(self, action_value):
        return {self.checkbox_name: self.checkbox_value, 'rPDUOutletCtrl': action_value}
