# APC PDU Manager
This script allows interacting with an old APC PDU.

The following models are tested on:
- AP7932
- AP7902

Features:
- List outlets
- Set outlet status (one or multiple at a time)
- Login / logout

The idea is that this can be used inside Home-assistant to setup entities to control the outlets individually.

## Setup
Install the python dependencies

```bash
    pip install -r requirements.txt
```

You can play around with the `test.py` script.

A pdu_session_manager is initialized with a url, username and password.
A pdu_outlet_manager is initialized with a pdu_session_manager

Methods:

```python
    pdu_session_manager.login() # uses the creds to log in
    pdu_session_manager.logout()
    pdu_outlet_manager.fetch_outlets() # logs in if not logged in and populates pdu_outlet_manager.outlets
    pdu_outlet_manager.set_outlet_power_status() # logs in if not logged in and switches a list of 1 or more outlets on or off.
```