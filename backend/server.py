import asyncio
import collections
import enum
import logging
import math
import random
import socket
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
from dataclasses_json import dataclass_json, LetterCase
from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.responses import PlainTextResponse
from starlette.routing import Route, WebSocketRoute
from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.websockets import WebSocket

logger = logging.getLogger(__name__)


class ObjectType(enum.IntEnum):
    PERSON = 0
    BICYCLE = 1
    CAR = 2
    MOTORCYCLE = 3
    BUS = 5
    TRUCK = 7
    TRAFFIC_LIGHT = 9
    FIRE_HYDRANT = 10
    STOP_SIGN = 11
    PARKING_METER = 12


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TrackedObject:
    location: Tuple[int, int]
    rotation: int
    vel: Tuple[float, float]
    obj_type: ObjectType

    @classmethod
    def from_np(cls, np_array: np.array):
        [obj_id, x, y, rot, speed, typ, t_stamp] = np_array
        vel = (speed * math.cos(rot), -speed * math.sin(rot))
        return obj_id, cls(obj_type=ObjectType(int(typ)), location=(int(x), int(y)), vel=vel,
                           rotation=math.pi / 2 - rot)


class Room:
    """
    Room state, comprising connected users.
    """

    def __init__(self):
        logger.info("Creating new empty room")
        self._users: Dict[str, WebSocket] = {}

    def __len__(self) -> int:
        """Get the number of users in the room.
        """
        return len(self._users)

    @property
    def empty(self) -> bool:
        """Check if the room is empty.
        """
        return len(self._users) == 0

    @property
    def user_list(self) -> List[str]:
        """Return a list of IDs for connected users.
        """
        return list(self._users)

    def add_user(self, user_id: str, websocket: WebSocket):
        """Add a user websocket, keyed by corresponding user ID.
        Raises:
            ValueError: If the `user_id` already exists within the room.
        """
        if user_id in self._users:
            raise ValueError(f"User {user_id} is already in the room")
        logger.info("Adding user %s to room", user_id)
        self._users[user_id] = websocket

    async def kick_user(self, user_id: str):
        """Forcibly disconnect a user from the room.
        We do not need to call `remove_user`, as this will be invoked automatically
        when the websocket connection is closed by the `RoomLive.on_disconnect` method.
        Raises:
            ValueError: If the `user_id` is not held within the room.
        """
        if user_id not in self._users:
            raise ValueError(f"User {user_id} is not in the room")
        await self._users[user_id].send_json(
            {
                "type": "ROOM_KICK",
                "data": {"msg": "You have been kicked from the chatroom!"},
            }
        )
        logger.info("Kicking user %s from room", user_id)
        await self._users[user_id].close()

    def remove_user(self, user_id: str):
        """Remove a user from the room.
        Raises:
            ValueError: If the `user_id` is not held within the room.
        """
        if user_id not in self._users:
            raise ValueError(f"User {user_id} is not in the room")
        logger.info("Removing user %s from room", user_id)
        del self._users[user_id]

    async def broadcast_message(self, user_id: str, msg: str):
        """Broadcast message to all connected users.
        """
        for websocket in self._users.values():
            await websocket.send_json(
                {"type": "MESSAGE", "data": {"user_id": user_id, "msg": msg}}
            )

    async def broadcast_tracking(self, objects: Dict[int, TrackedObject], tick_time: float):
        for websocket in self._users.values():
            await websocket.send_json(
                {"type": "TRACKING", "data": {k: o.to_dict() for k, o in objects.items()},
                 "tickTime": tick_time}
            )

    async def broadcast_user_joined(self, user_id: str):
        """Broadcast message to all connected users.
        """
        for websocket in self._users.values():
            await websocket.send_json({"type": "USER_JOIN", "data": user_id})

    async def broadcast_user_left(self, user_id: str):
        """Broadcast message to all connected users.
        """
        for websocket in self._users.values():
            await websocket.send_json({"type": "USER_LEAVE", "data": user_id})


class RoomEventMiddleware:  # pylint: disable=too-few-public-methods
    """Middleware for providing a global :class:`~.Room` instance to both HTTP
    and WebSocket scopes.
    Although it might seem odd to load the broadcast interface like this (as
    opposed to, e.g. providing a global) this both mimics the pattern
    established by starlette's existing DatabaseMiddlware, and describes a
    pattern for installing an arbitrary broadcast backend (Redis PUB-SUB,
    Postgres LISTEN/NOTIFY, etc) and providing it at the level of an individual
    request.
    """

    def __init__(self, app: ASGIApp):
        self._app = app
        self._room = global_room

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] in ("lifespan", "http", "websocket"):
            scope["room"] = self._room
        await self._app(scope, receive, send)


class Stream(WebSocketEndpoint):
    encoding: str = "text"
    session_name: str = ""
    count: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room: Optional[Room] = None
        self.user_id: Optional[str] = None

    @classmethod
    def get_next_user_id(cls):
        """Returns monotonically increasing numbered usernames in the form
            'user_[number]'
        """
        user_id: str = f"user_{cls.count}"
        cls.count += 1
        return user_id

    async def on_connect(self, websocket):
        """Handle a new connection.
        New users are assigned a user ID and notified of the room's connected
        users. The other connected users are notified of the new user's arrival,
        and finally the new user is added to the global :class:`~.Room` instance.
        """
        logger.info("Connecting new user...")
        room: Optional[Room] = self.scope.get("room")
        if room is None:
            raise RuntimeError(f"Global `Room` instance unavailable!")
        self.room = room
        self.user_id = self.get_next_user_id()
        await websocket.accept()
        await websocket.send_json(
            {"type": "ROOM_JOIN", "data": {"user_id": self.user_id}}
        )
        await self.room.broadcast_user_joined(self.user_id)
        self.room.add_user(self.user_id, websocket)

    async def on_disconnect(self, _websocket: WebSocket, _close_code: int):
        """Disconnect the user, removing them from the :class:`~.Room`, and
        notifying the other users of their departure.
        """
        if self.user_id is None:
            raise RuntimeError(
                "RoomLive.on_disconnect() called without a valid user_id"
            )
        self.room.remove_user(self.user_id)
        await self.room.broadcast_user_left(self.user_id)

    async def on_receive(self, websocket, data):
        await websocket.send_text(f"Message text was: {data}")


class VehicleTracker:
    MAX_HISTORY_POINTS = 10

    _vehicle_history: Dict[int, List[TrackedObject]]
    fake_mode: bool
    socket_reader: Optional[asyncio.StreamReader]
    socket_writer: Optional[asyncio.StreamWriter]
    room: Optional[Room]
    host: Optional[str]
    port: Optional[int]

    def __init__(self, room: Room):
        self._vehicle_history = collections.defaultdict(list)
        self.fake_mode = False
        self.socket_reader = None
        self.socket_writer = None
        self._room = room
        self.host = None
        self.port = None

    def update_history(self, vehicle_id: int, obj: TrackedObject):
        self._vehicle_history[vehicle_id].append(obj)
        if len(self._vehicle_history[vehicle_id]) > self.MAX_HISTORY_POINTS:
            # remove old point
            self._vehicle_history[vehicle_id].pop(0)

    @property
    def current_vehicles(self) -> Dict[int, TrackedObject]:
        return {key: objs[-1] for key, objs in self._vehicle_history.items()}

    async def connect(self, host: str, port: int):
        if self.fake_mode:
            return

        self.host = host
        self.port = port

        try:
            self.socket_reader, self.socket_writer = await asyncio.open_connection(host, port)
            self.socket_writer.write(bytes("", "utf-8"))
            await self.socket_writer.drain()
        except socket.error:
            logger.warning("Not able to connect. Using fake data")
            self.fake_mode = True

    async def close(self):
        if self.fake_mode:
            return

        self.socket_writer.close()
        await self.socket_writer.wait_closed()
        self.socket_writer = None
        self.socket_reader = None

    async def listen(self):
        new_time = datetime.now()
        next_loc = None
        while True:
            try:
                prev_time = new_time
                new_time = datetime.now()
                elapsed = (new_time - prev_time).total_seconds()
                if self.fake_mode is False:
                    data = await self.socket_reader.read(2048)
                    received = np.frombuffer(data)
                    received = received.reshape((len(received) // 7, 7))
                    received_pairs = [TrackedObject.from_np(row) for row in received]
                    object_data = {obj_id: obj for (obj_id, obj) in received_pairs}
                else:
                    new_loc = next_loc or (200 + random.randint(-100, 100), 300 + random.randint(-100, 100))
                    next_loc = (200 + random.randint(-100, 100), 300 + random.randint(-100, 100))
                    diff = ((next_loc[0] - new_loc[0]) / elapsed, (next_loc[1] - new_loc[1]) / elapsed)
                    object_data = {
                        1: TrackedObject(location=(450, 300), rotation=0, vel=(0, 0), obj_type=ObjectType.CAR),
                        2: TrackedObject(location=new_loc, rotation=0, vel=diff, obj_type=ObjectType.PERSON)
                    }

                for k, obj in object_data.items():
                    self.update_history(k, obj)

                await self._room.broadcast_tracking(self.current_vehicles, elapsed)
                await asyncio.sleep(0.2)
            except Exception as e:
                logger.error("Socket read failed:", e)
                # Attempt to reconnect
                await self.close()
                await self.connect(self.host, self.port)


async def init_tracker():
    loop = asyncio.get_event_loop()
    tracker = VehicleTracker(global_room)
    await tracker.connect('14.137.209.102', 7777)
    loop.create_task(tracker.listen())


async def homepage(request):
    return PlainTextResponse("Homepage")


global_room = Room()
routes = [
    Route('/', endpoint=homepage),
    WebSocketRoute('/stream', endpoint=Stream)
]
app = Starlette(
    routes=routes,
    on_startup=[init_tracker]
)
app.add_middleware(RoomEventMiddleware)
