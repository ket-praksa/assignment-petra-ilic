from hat.drivers import iec104
from hat.aio import run_asyncio

addr = iec104.Address("127.0.0.1", 19999)


async def connect():

    conn = await iec104.connect(addr)

    command = iec104.Command(
        action=iec104.Action.EXECUTE,
        value=iec104.common.SingleValue.ON,
        asdu_address=30,
        io_address=0,
        time=None,
        qualifier=1,
    )

    await conn.send_command(command)

    while True:
        result = await conn.receive()
        if result[0].asdu_address == 30:
            print(result)

    await conn.async_close()


if __name__ == "__main__":
    run_asyncio(connect())
