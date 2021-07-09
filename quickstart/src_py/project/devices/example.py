import asyncio
import hat.aio
import hat.event.common
import hat.gateway.common
from hat.drivers import iec104
from hat.aio import run_asyncio


json_schema_id = None
json_schema_repo = None
device_type = "example"
addr = iec104.Address("127.0.0.1", 19999)


async def create(conf, event_client, event_type_prefix):
    device = Device()

    device._async_group = hat.aio.Group()
    device._event_client = event_client
    device._event_type_prefix = event_type_prefix
    device._async_group.spawn(device._main_loop)

    return device


class Device(hat.gateway.common.Device):
    @property
    def async_group(self):
        return self._async_group

    async def _main_loop(self):
        conn = await iec104.connect(addr)

        while True:
            result = await conn.receive()
            val = round(result[0].value.value, 2)
            # print(val)
            asdu = str(result[0].asdu_address)
            io = str(result[0].io_address)

            self._event_client.register(
                [
                    hat.event.common.RegisterEvent(
                        event_type=(
                            *self._event_type_prefix,
                            "gateway",
                            asdu,
                            io,
                        ),
                        source_timestamp=None,
                        payload=hat.event.common.EventPayload(
                            type=hat.event.common.EventPayloadType.JSON, data=val
                        ),
                    )
                ]
            )
