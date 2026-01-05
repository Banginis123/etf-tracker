import asyncio
from email_service import send_alert_email

async def main():
    await send_alert_email("TEST", 100, 99)

asyncio.run(main())

