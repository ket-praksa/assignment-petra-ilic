from hat import aio
from hat import json
from hat.event.server import common
import typing
import sqlite3
import math

json_schema_id = None
json_schema_repo = None


async def create(conf: json.Data):
    backend = Backend()
    backend._async_group = aio.Group()
    backend._db_con = con=sqlite3.connect(conf["path"])
    return backend

class Backend(common.Backend):

    @property
    def async_group(self) -> aio.Group:
        return self._async_group
    
    async def get_last_event_id(self,
                                server_id: int
                                ) -> common.EventId:
        result = common.EventId(server_id, 0)
        return await self._async_group.spawn(aio.call, lambda: result)

    async def register(self,
                       events: typing.List[common.Event]
                       ) -> typing.List[typing.Optional[common.Event]]:
        cur = self._db_con.cursor()
        for e in events:
            e_type = e.event_type
            asdu = e_type[-2]
            io = e_type[-1]


            if asdu.isnumeric() and io.isnumeric() and e_type[0] == "gui":
                val = e.payload.data 
                if math.isnan(val): 
                    val = "0"
                asdu = int(asdu)            
                if asdu in range(0, 10): 
                    table = "BUS"
                elif asdu in range(10, 20):
                    table = "LINE"
                elif asdu in range(30, 40):
                    table = "SWITCH"
                else:
                    table = "TRANSFORMER"
                
                cur.execute(f"INSERT INTO {table} (asdu, io, val) VALUES ({asdu}, {io}, {val});")
                   

            self._db_con.commit()
        return await self._async_group.spawn(aio.call, lambda: events)

    async def query(self,
                    data: common.QueryData
                    ) -> typing.List[common.Event]:
        result = []
        return await self._async_group.spawn(aio.call, lambda: result)


