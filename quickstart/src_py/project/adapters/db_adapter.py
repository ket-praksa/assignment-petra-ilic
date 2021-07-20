import hat.aio
import hat.event.common
import hat.gui.common
import hat.util
import hat.juggler
import numbers
import math
import time

json_schema_id = None
json_schema_repo = None


async def create_subscription(conf):
    return hat.event.common.Subscription([("db","*")])


async def create_adapter(conf, event_client):
    adapter = DBAdapter()

    adapter._async_group = hat.aio.Group()
    adapter._event_client = event_client
    adapter._state_change_cb_registry = hat.util.CallbackRegistry()
    adapter._state = {}
    adapter._async_group.spawn(adapter._main_loop)

    return adapter


class DBAdapter(hat.gui.common.Adapter):
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
            


class Session(hat.gui.common.AdapterSession):
    def __init__(self, adapter, juggler_client, group):
        self._adapter = adapter
        self._juggler_client = juggler_client
        self._async_group = group
        self._async_group.spawn(self._run)
        self._state = {}

    @property
    def async_group(self):
        return self._async_group

    @property
    def state(self):
        return self._state
    
    def subscribe_to_state_change(self, callback):
        return self._state_change_cb_registry.register(callback)

    async def _run(self):
        try:    
            while True:
                received = await self._juggler_client.receive()
    
                asdu = received.get("asdu")
                io = received.get("io")
                
                events = await self._adapter._event_client.query(
                    hat.event.common.QueryData(event_types=[["db", asdu, io]], max_results=1)
                )
                self._state = dict(self._state)
                self._state["pairs"] = events[0].payload.data
                self._on_state_change() 
        except:
            await self.wait_closing()

    def _on_state_change(self):
        self._juggler_client.set_local_data(self._state)
