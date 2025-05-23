import hashlib
import json
import logging
from typing import Any, Dict, List, Tuple

import strawberry
import strawberry_django
from kante.types import Info
from kammer import enums, inputs, models, scalars, types
from vector import inputs as vector_inputs

logger = logging.getLogger(__name__)
from django.contrib.auth import get_user_model
from kammer import inputs


@strawberry.input
class CreateRoomInput:
    description: str | None = None
    title: str | None = None


def create_room(info: Info, input: CreateRoomInput) -> types.Room:
    creator = info.context.request.user

    exp = models.Room.objects.create(
        title=input.title or "Untitled",
        description=input.description or "No description",
    )

    return exp


@strawberry.input
class DeleteRoomInput:
    id: strawberry.ID


def delete_room(info: Info, input: DeleteRoomInput) -> strawberry.ID:
    room = models.Room.objects.get(id=input.id)

    room.delete()

    return input.id


@strawberry.input
class SendMessageInput:
    room: strawberry.ID
    agent_id: str
    text: str
    parent: strawberry.ID | None = None
    notify: bool | None = None
    attach_structures: List[vector_inputs.StructureInput] | None = None


def send(info: Info, input: SendMessageInput) -> types.Message:
    agent, _ = models.Agent.objects.get_or_create(
        user=info.context.request.user,
        client=info.context.request.client,
        room_id=input.room,
        name=input.agent_id,
    )

    message = models.Message.objects.create(agent=agent, text=input.text)
    if input.attach_structures:
        for structure in input.attach_structures:
            structure, _ = models.Structure.objects.get_or_create(object=structure.object, identifier=structure.identifier)
            message.attached_structures.add(structure)

    return message
