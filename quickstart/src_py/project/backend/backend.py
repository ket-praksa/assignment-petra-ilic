from hat import aio
from hat import json
from hat.event.server import common
import typing
import sqlite3
import math
import hat
import time
import datetime

json_schema_id = None
json_schema_repo = None


async def create(conf: json.Data) -> 'Backend':
    """Creates a new backend instance which communicates with the database.

    Args:
        conf: backend configuration

    Returns:
        new Backend instance
    """
    backend = Backend()
    backend._async_group = aio.Group()
    backend._db_con = init_db(conf)
    return backend


def init_db(conf):
    con = sqlite3.connect(conf["path"])
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS ELEMENT(asdu integer, io integer, val float,
                'time' DATETIME NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')))""")
    con.commit()
    return con


class Backend(common.Backend):
    last_entry = {}

    @property
    def async_group(self) -> aio.Group:
        """Creates a group controlling resource's lifetime.

        Returns:
            controlling resource's lifetime
        """
        return self._async_group

    async def get_last_event_id(self, server_id: int) -> common.EventId:
        """Returns the last registered event id associated with server id.

        Args:
            server_id: server's id

        Returns:
            the last registered event id associated with server id
        """
        result = common.EventId(server_id, 0)
        return await self._async_group.spawn(aio.call, lambda: result)

    async def register(
        self, events: typing.List[common.Event]
    ) -> typing.List[typing.Optional[common.Event]]:
        """Stores data into database.

        Args:
            events: received events

        Returns:
            list of events
        """
        cur = self._db_con.cursor()
        for e in events:

            e_type = e.event_type
            asdu = e_type[-2]
            io = e_type[-1]

            if asdu.isnumeric() and io.isnumeric() and e_type[0] == "gui":

                current = datetime.datetime.fromtimestamp(time.time())
                last = Backend.last_entry.get(asdu, None)
                if last is None:
                    Backend.last_entry[asdu] = current
                elif current - datetime.timedelta(minutes=2) < last:
                    pass

                Backend.last_entry[asdu] = current
                val = e.payload.data
                if math.isnan(val):
                    val = "0"
                asdu = int(asdu)
                io = int(io)

                entries = cur.execute("SELECT Count(*) FROM ELEMENT")
                entries = entries.fetchone()[0]
                if entries > 50000:
                    cur.execute("DELETE FROM ELEMENT ORDER BY time LIMIT 1000")

                cur.execute("INSERT INTO ELEMENT (asdu, io, val) VALUES (?, ?, ?);", (asdu, io, val))

            self._db_con.commit()
        return await self._async_group.spawn(aio.call, lambda: events)

    async def query(self, data: common.QueryData) -> typing.List[common.Event]:
        """Loads data from database based on query data.

        Args:
            data: query data

        Returns:
            list of events containing selected records
        """
        result = []
        cur = self._db_con.cursor()

        event_type = data.event_types[0]

        if event_type[0] == "db":
            asdu = int(event_type[1])
            io = int(event_type[2])
            time_val = []

            for val, time in cur.execute("SELECT val, time FROM ELEMENT WHERE asdu=? AND io=? AND time >= datetime('now','-1 day');", (asdu, io)):
                time_val.append(f"{time};{val}")

            event = hat.event.common.Event(
                event_id=hat.event.common.EventId(server=1, instance=1),
                timestamp=common.Timestamp(1, 2),
                event_type=("db",),
                source_timestamp=None,
                payload=hat.event.common.EventPayload(
                    type=hat.event.common.EventPayloadType.JSON, data=time_val
                ),
            )
            result.append(event)
        return await self._async_group.spawn(aio.call, lambda: result)
