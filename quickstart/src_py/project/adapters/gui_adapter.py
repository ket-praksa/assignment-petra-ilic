import hat.aio
import hat.event.common
import hat.gui.common
import hat.util
import hat.juggler
from hat import json
from hat.event.common import Subscription
from hat.gui.common import Adapter
from hat.gui.common import AdapterEventClient
from hat.aio import Group
from hat.util import CallbackRegistry
from hat.util import RegisterCallbackHandle
from hat.gui.common import AdapterSessionClient
import math
import typing


json_schema_id = None
json_schema_repo = None


async def create_subscription(conf: json.Data) -> Subscription:
    """Creates a subscribed event types filter.

    Args:
        conf: adapter configuration

    Returns:
        subscribed event types filter
    """
    return hat.event.common.Subscription([("gateway", "gateway", "device", "device", "device", "gui", "*",)])


async def create_adapter(conf: json.Data, event_client: AdapterEventClient) -> 'Adapter':
    """Creates a new adapter instance which provides server-side functionality and data
    exposed to GUI relying on its interal state.

    Args:
        conf: adapter configuration
        event_client: adapter's event client

    Returns:
        new Adapter instance
    """
    adapter = Adapter()

    adapter._async_group = hat.aio.Group()
    adapter._event_client = event_client
    adapter._state = {}
    adapter._state_change_cb_registry = hat.util.CallbackRegistry()

    adapter._async_group.spawn(adapter._main_loop)

    return adapter


class Adapter(hat.gui.common.Adapter):
    @property
    def async_group(self) -> Group:
        """
        Creates a group controlling resource's lifetime.

        Returns:
            controlling resource's lifetime
        """
        return self._async_group

    @property
    def state(self) -> typing.Dict[str, float]:
        """Returns adapter state.

        Returns:
            adapter state
        """
        return self._state

    def subscribe_to_state_change(self, callback: typing.Callable) -> RegisterCallbackHandle:
        """Registers a callback.

        Args:
            callback: notified on state change

        Returns:
            register callback handle
        """
        return self._state_change_cb_registry.register(callback)

    async def create_session(self, juggler_client: AdapterSessionClient) -> 'Session':
        """Creates adapter's single client session.

        Args:
            juggler_client: single juggler connection

        Returns:
            client session
        """
        return Session(self, juggler_client, self._async_group.create_subgroup())

    async def _main_loop(self):
        while True:
            events = await self._event_client.receive()
            for e in events:
                data = e.payload.data

                if math.isnan(data):data = 0

                self._state = dict(self._state)
                key = "el" + "-".join(e.event_type[-2:])

                self._state["el" + "-".join(e.event_type[-2:])] = data
                self._state_change_cb_registry.notify()


class Session(hat.gui.common.AdapterSession):
    def __init__(self, adapter, juggler_client, group):
        self._adapter = adapter
        self._juggler_client = juggler_client
        self._async_group = group
        self._async_group.spawn(self._run)

    @property
    def async_group(self) -> Group:
        """
        Creates a group controlling resource's lifetime.

        Returns:
            controlling resource's lifetime
        """
        return self._async_group

    async def _run(self):
        try:
            self._on_state_change()
            with self._adapter.subscribe_to_state_change(self._on_state_change):
                while True:
                    received = await self._juggler_client.receive()

                    self._adapter._event_client.register((
                        [
                            hat.event.common.RegisterEvent(
                                event_type=("device", "system"),
                                source_timestamp=None,
                                payload=hat.event.common.EventPayload(
                                    type=hat.event.common.EventPayloadType.JSON,
                                    data=received,
                                ),
                            )
                        ]
                    )
                    )
        except:
            await self.wait_closing()

    def _on_state_change(self):
        self._juggler_client.set_local_data(self._adapter.state)
