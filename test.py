from pdu_manager.pdu_session_manager import PDUSessionManager
from pdu_manager.pdu_outlet_manager import PDUOutletManager
import asyncio

async def setup_outlets(url, username, password, expected_outlets):
    pdu_session_manager = PDUSessionManager(url, username, password)
    pdu_outlet_manager = PDUOutletManager(pdu_session_manager)

    try:
        await pdu_session_manager.login()
        await pdu_outlet_manager.fetch_outlets()
        print(f"Outlet count for {url}: {len(pdu_outlet_manager.outlets)} (Expected: {expected_outlets})")
        await pdu_outlet_manager.set_outlet_power_state([pdu_outlet_manager.outlets[2], pdu_outlet_manager.outlets[5]], "off")
        await pdu_outlet_manager.fetch_outlets()
    finally:
        await pdu_session_manager.logout()

async def main():
    # List of tasks to run
    tasks = [
        setup_outlets("http://pdu", "apc", "apc", 24)
    ]
    # Run tasks concurrently
    await asyncio.gather(*tasks)

# Run the main coroutine
asyncio.run(main())
