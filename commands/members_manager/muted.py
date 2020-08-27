import sys

from vkbottle.api import UserApi
from vkbottle.rule import FromMe
from vkbottle.user import Blueprint, Message
from vkbottle.utils import logger


from objects import Database, MutedMembers
from utils import edit_message, get_ids_by_message, get_full_name_by_member_id

user = Blueprint(
    name='muted_members_blueprint'
)


def add_muted_member(database: Database, member_id: int, peer_id: int) -> None:
    database.muted_members.append(
        MutedMembers(
            member_id=member_id,
            chat_id=peer_id
        )
    )
    database.save()


def remove_muted_member(database: Database, member_id: int, peer_id: int) -> None:
    ignored_member = None
    for ign in database.muted_members:
        if ign.member_id == member_id and ign.chat_id == peer_id:
            ignored_member = ign
    database.muted_members.remove(ignored_member)
    database.save()


async def show_muted_members(
        database: Database,
        api: UserApi,
        peer_id: int
) -> str:
    user_ids = [
        muted_member.member_id
        for muted_member in database.muted_members
        if muted_member.chat_id == peer_id and muted_member.member_id > 0
    ]
    group_ids = [
        abs(muted_member.member_id)
        for muted_member in database.muted_members
        if muted_member.chat_id == peer_id and muted_member.member_id < 0
    ]

    if not user_ids and not group_ids:
        return "📃 Ваш мут-лист пуст"

    index = 1
    message = "📃 Ваш мут-лист для этого чата\n"

    if user_ids:
        for vk_user in await api.users.get(user_ids=user_ids):
            message += f"{index}. [id{vk_user.id}|{vk_user.first_name} {vk_user.last_name}]\n"
            index += 1

    if group_ids:
        for vk_group in await api.groups.get_by_id(group_ids=group_ids):
            message += f'{index}. [club{vk_group.id}|{vk_group.name}]'
            index += 1
    return message


@user.on.message(
    FromMe(),
    text=[
        '<prefix:service_prefix> +мут [id<user_id:int>|<foo>',
        '<prefix:service_prefix> +мут [club<group_id:int>|<foo>',
        '<prefix:service_prefix> +мут https://vk.com/<domain>',
        '<prefix:service_prefix> +мут',
    ]
)
@user.on.chat_message(
    FromMe(),
    text=[
        '<prefix:service_prefix> +мут [id<user_id:int>|<foo>',
        '<prefix:service_prefix> +мут [club<group_id:int>|<foo>',
        '<prefix:service_prefix> +мут https://vk.com/<domain>',
        '<prefix:service_prefix> +мут',
    ]
)
async def add_muted_member_wrapper(
        message: Message,
        domain: str = None,
        user_id: int = None,
        group_id: int = None,
        **kwargs
):
    db = Database.get_current()
    logger.info(f'Добавление в мут\n')
    member_id = user_id if user_id else None
    if not user_id and group_id:
        member_id = -group_id

    member_ids = await get_ids_by_message(message, member_id, domain)
    if not member_ids:
        await edit_message(
            message,
            f'⚠ Необходимо указать пользователей'
        )
        return

    member_id = member_ids[0]

    if member_id > 0:
        name = f'Пользователь [id{member_id}|{await get_full_name_by_member_id(message.api, member_id)}]'
    else:
        name = f'Группа [club{abs(member_id)}|{await get_full_name_by_member_id(message.api, member_id)}]'

    if member_id in [
        muted_member.member_id
        for muted_member in db.muted_members
        if muted_member.chat_id == message.peer_id
    ]:
        await edit_message(
            message,
            f'⚠ {name} уже в мутлисте'
        )
        return
    add_muted_member(db, member_id, message.peer_id)
    await edit_message(
        message,
        f'✅ {name} добавлен в мутлист'
    )


@user.on.message(
    FromMe(),
    text=[
        '<prefix:service_prefix> -мут [id<user_id:int>|<foo>',
        '<prefix:service_prefix> -мут [club<group_id:int>|<foo>',
        '<prefix:service_prefix> -мут https://vk.com/<domain>',
        '<prefix:service_prefix> -мут',
    ]
)
@user.on.chat_message(
    FromMe(),
    text=[
        '<prefix:service_prefix> -мут [id<user_id:int>|<foo>',
        '<prefix:service_prefix> -мут [club<group_id:int>|<foo>',
        '<prefix:service_prefix> -мут https://vk.com/<domain>',
        '<prefix:service_prefix> -мут',
    ]
)
async def remove_ignored_member_wrapper(
        message: Message,
        domain: str = None,
        user_id: int = None,
        group_id: int = None,
        **kwargs
):
    db = Database.get_current()
    logger.info(f'Удаление из мута\n')
    member_id = user_id if user_id else None
    if not user_id and group_id:
        member_id = -group_id

    member_ids = await get_ids_by_message(message, member_id, domain)
    if not member_ids:
        await edit_message(
            message,
            f'⚠ Необходимо указать пользователей'
        )
        return

    member_id = member_ids[0]

    if member_id > 0:
        name = f'Пользователь  [id{member_id}|{await get_full_name_by_member_id(message.api, member_id)}]'
    else:
        name = f'Группа [club{abs(member_id)}|{await get_full_name_by_member_id(message.api, member_id)}]'

    if member_id not in [
        muted_member.member_id
        for muted_member in db.muted_members
        if muted_member.chat_id == message.peer_id
    ]:
        await edit_message(
            message,
            f'⚠ {name} не в мут-листе'
        )
        return
    remove_muted_member(db, member_id, message.peer_id)
    await edit_message(
        message,
        f'✅ {name} удален из мут-листа'
    )


@user.on.message(
    FromMe(),
    text=[
        '<prefix:service_prefix> мутлист',
        '<prefix:service_prefix> мут лист',
    ]
)
@user.on.chat_message(
    FromMe(),
    text=[
        '<prefix:service_prefix> мутлист',
        '<prefix:service_prefix> мут лист',
    ]
)
async def show_mute_members_wrapper(message: Message, **kwargs):
    db = Database.get_current()
    logger.info(f'Просмотр мута\n')
    await edit_message(
        message,
        await show_muted_members(
            db,
            message.api,
            message.peer_id
        )
    )
