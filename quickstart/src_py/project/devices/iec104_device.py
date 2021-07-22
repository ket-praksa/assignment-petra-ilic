import hat.aio
import hat.event.common
import hat.gateway.common
from hat import json
from hat.drivers import iec104
from hat.gateway.common import DeviceEventClient
from hat.aio import Group
import time
import typing

json_schema_id = None
json_schema_repo = None
device_type = "device"
addr = iec104.Address("127.0.0.1", 19999)


async def create(conf: json.Data, event_client: DeviceEventClient,
                 event_type_prefix: typing.List[str]) -> 'Device':
    """
    Creates a new device instance and connects it to the server. Receives and registers
    events from the server and sends commands back to the server.

    Args:
        conf: device configuration
        event_client: device's event client interface
        event_type_prefix: event type prefix

    Returns:
        new Device instance
    """
    device = Device()

    device._async_group = hat.aio.Group()
    device._event_client = event_client
    device._event_type_prefix = event_type_prefix
    device._conn = await iec104.connect(addr)
    device._async_group.spawn(device._main_loop)
    device._async_group.spawn(device._event_loop)

    return device


class Device(hat.gateway.common.Device):
    @property
    def async_group(self) -> Group:
        """
        Creates a group controlling resource's lifetime.

        Returns:
            controlling resource's lifetime
        """
        return self._async_group

    async def _main_loop(self):

        self._conn = await iec104.connect(addr)
        data = await self._conn.interrogate(65535)
        time.sleep(3)
        for event in data:
            self._register_event([event])

        while True:
            result = await self._conn.receive()
            self._register_event(result)

    def _register_event(self, result):
        val = round(result[0].value.value, 2)
        asdu = str(result[0].asdu_address)
        io = str(result[0].io_address)

        self._event_client.register(
            [
                hat.event.common.RegisterEvent(
                    event_type=(*self._event_type_prefix,
                                "device", "gui", asdu, io),
                    source_timestamp=None,
                    payload=hat.event.common.EventPayload(
                        type=hat.event.common.EventPayloadType.JSON, data=val
                    ),
                )
            ]
        )

    async def _event_loop(self):

        while True:
            data = await self._event_client.receive()

            if data[0].payload.data.get("value") == 0:
                val = iec104.common.SingleValue.OFF
            else:
                val = iec104.common.SingleValue.ON

            command = iec104.Command(
                action=iec104.Action.EXECUTE,
                value=val,
                asdu_address=data[0].payload.data.get("asdu"),
                io_address=data[0].payload.data.get("io"),
                time=None,
                qualifier=1,
            )

            res = await self._conn.send_command(command)
