import sys

from vkbottle.rule import FromMe
from vkbottle.user import Blueprint, Message

from objects import Database
from utils import edit_message
from vkbottle.utils import logger

user = Blueprint(
    name='prefixes_blueprint'
)


def show_self_prefixes(database: Database) -> str:
    index = 1
    message = '📃 Ваши префиксы для собственных сигналов\n'
    for prefix in database.self_prefixes:
        message += f'{index}. {prefix}\n'
        index += 1
    return message


def show_duty_prefixes(database: Database) -> str:
    index = 1
    message = '📃 Ваши префиксы для сигналов дежурному\n'
    for prefix in database.duty_prefixes:
        message += f'{index}. {prefix}\n'
        index += 1
    return message


def add_self_prefix(database: Database, prefix: str) -> None:
    database.self_prefixes.append(prefix)
    database.save()


def add_duty_prefix(database: Database, prefix: str) -> None:
    database.duty_prefixes.append(prefix)
    database.save()


def remove_self_prefix(database: Database, prefix: str) -> None:
    database.self_prefixes.remove(prefix)
    database.save()


def remove_duty_prefix(database: Database, prefix: str) -> None:
    database.duty_prefixes.remove(prefix)
    database.save()


@user.on.message(FromMe(), text="<prefix:service_prefix> префиксы свои")
@user.on.chat_message(FromMe(), text="<prefix:service_prefix> префиксы свои")
async def show_self_prefixes_wrapper(message: Message, **kwargs):
    db = Database.get_current()
    logger.info(f'Просмотр своих префиксов\n')
    await edit_message(
        message,
        show_self_prefixes(db)
    )


@user.on.message(FromMe(), text="<prefix:service_prefix> префиксы дежурный")
@user.on.chat_message(FromMe(), text="<prefix:service_prefix> префиксы дежурный")
async def show_duty_prefixes_wrapper(message: Message, **kwargs):
    logger.info(f'Просмотр префиксов дежурного\n')
    db = Database.get_current()
    await edit_message(
        message,
        show_duty_prefixes(db)
    )


@user.on.message(FromMe(), text="<prefix:service_prefix> +префикс свой <new_prefix>")
@user.on.chat_message(FromMe(), text="<prefix:service_prefix> +префикс свой <new_prefix>")
async def add_self_prefix_wrapper(message: Message, new_prefix: str, **kwargs):
    db = Database.get_current()
    logger.info(f'Создание своего префикса\n')
    new_prefix = new_prefix.replace(' ', '')
    if new_prefix in db.self_prefixes:
        await edit_message(
            message,
            f'⚠ Префикс <<{new_prefix}>> уже существует'
        )
        return
    add_self_prefix(db, new_prefix)
    await edit_message(
        message,
        f'✅ Новый префикс <<{new_prefix}>> создан'
    )


@user.on.message(FromMe(), text="<prefix:service_prefix> +префикс дежурный <new_prefix>")
@user.on.chat_message(FromMe(), text="<prefix:service_prefix> +префикс дежурный <new_prefix>")
async def add_duty_prefix_wrapper(message: Message, new_prefix: str, **kwargs):
    db = Database.get_current()
    logger.info(f'Создание префикса дежурного\n')
    new_prefix = new_prefix.replace(' ', '')
    if new_prefix in db.duty_prefixes:
        await edit_message(
            message,
            f'⚠ Префикс <<{new_prefix}>> уже существует'
        )
        return
    add_duty_prefix(db, new_prefix)
    await edit_message(
        message,
        f'✅ Новый префикс <<{new_prefix}>> создан'
    )


@user.on.message(FromMe(), text="<prefix:service_prefix> -префикс свой <old_prefix>")
@user.on.chat_message(FromMe(), text="<prefix:service_prefix> -префикс свой <old_prefix>")
async def remove_self_prefix_wrapper(message: Message, old_prefix: str, **kwargs):
    db = Database.get_current()
    logger.info(f'Удаление своего префикса\n')
    old_prefix = old_prefix.replace(' ', '')
    if old_prefix not in db.self_prefixes:
        await edit_message(
            message,
            f'⚠ Префикса <<{old_prefix}>> не существует'
        )
        return
    remove_self_prefix(db, old_prefix)
    await edit_message(
        message,
        f'✅ Префикс <<{old_prefix}>> удален'
    )


@user.on.message(FromMe(), text="<prefix:service_prefix> -префикс дежурный <old_prefix>")
@user.on.chat_message(FromMe(), text="<prefix:service_prefix> -префикс дежурный <old_prefix>")
async def remove_duty_prefix_wrapper(message: Message, old_prefix: str, **kwargs):
    db = Database.get_current()
    logger.info(f'Удаление префикса дежурного\n')
    old_prefix = old_prefix.replace(' ', '')
    if old_prefix not in db.duty_prefixes:
        await edit_message(
            message,
            f'⚠ Префикса <<{old_prefix}>> не существует'
        )
        return
    remove_duty_prefix(db, old_prefix)
    await edit_message(
        message,
        f'✅ Префикс <<{old_prefix}>> удален'
    )
