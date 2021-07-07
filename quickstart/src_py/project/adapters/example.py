import hat.aio
import hat.event.common
import hat.gui.common
import hat.util


json_schema_id = None
json_schema_repo = None


async def create_subscription(conf):
    return hat.event.common.Subscription([("*",)])


async def create_adapter(conf, event_client):
    adapter = Adapter()

    adapter._async_group = hat.aio.Group()
    adapter._event_client = event_client
    adapter._state = {}
    adapter._state_change_cb_registry = hat.util.CallbackRegistry()

    adapter._async_group.spawn(adapter._main_loop)

    return adapter


class Adapter(hat.gui.common.Adapter):
    @property
    def async_group(self):
        return self._async_group

    @property
    def state(self):
        return self._state

    def subscribe_to_state_change(self, callback):
        return self._state_change_cb_registry.register(callback)

    async def create_session(self, juggler_client):
        return Session(self, juggler_client, self._async_group.create_subgroup())

    async def _main_loop(self):
        while True:
            events = await self._event_client.receive()
            for e in events:
                ev_type = e.event_type[-2:]
                if e.event_type == (ev_type[0], ev_type[1]):
                    self._state = dict(self._state)
                    self._state["el" + "-".join(ev_type)] = e.payload.data
                    self._state_change_cb_registry.notify()


class Session(hat.gui.common.AdapterSession):
    def __init__(self, adapter, juggler_client, group):
        self._adapter = adapter
        self._juggler_client = juggler_client
        self._async_group = group
        self._async_group.spawn(self._run)

    @property
    def async_group(self):
        return self._async_group

    async def _run(self):
        self._on_state_change()
        with self._adapter.subscribe_to_state_change(self._on_state_change):
            await self.wait_closing()

    def _on_state_change(self):
        self._juggler_client.set_local_data(self._adapter.state)
