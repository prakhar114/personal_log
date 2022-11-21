import os
import Example_pb2
from base64 import standard_b64decode
from base64 import standard_b64encode

import asyncio
import json
import time
from foxglove_websocket import run_cancellable
from foxglove_websocket.server import FoxgloveServer, FoxgloveServerListener
from foxglove_websocket.types import ChannelId
with open(
    os.path.join(os.path.dirname(Example_pb2.__file__), "Example.bin"), "rb"
) as schema_bin:
    schema_base64 = standard_b64encode(schema_bin.read()).decode("ascii")

async def main():

    class Listener(FoxgloveServerListener):
        def on_subscribe(self, server: FoxgloveServer, channel_id: ChannelId):
            print("First client subscribed to", channel_id)

        def on_unsubscribe(self, server: FoxgloveServer, channel_id: ChannelId):
            print("Last client unsubscribed from", channel_id)

    # Specify the server's host, port, and a human-readable name
    async with FoxgloveServer("0.0.0.0", 8765, "example server") as server:
        server.set_listener(Listener())
        chan_id = await server.add_channel(
            {
                "topic": "example_msg",
                "encoding": "protobuf",
                "schemaName": "Examplemsg",
                "schema": schema_base64,
            }
        )

    i = 0
    while True:
        i += 1
        await asyncio.sleep(0.2)
        await server.send_message(
            chan_id,
            time.time_ns(),
            Example_pb2.Examplemsg(msg="Hello", count=i).SerializeToString(),
        )

if __name__ == "__main__":
    run_cancellable(main())