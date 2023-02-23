from typing import Any, Union, Dict

from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery

from utils.models import User


class IsAdminFilter(Filter):
    async def __call__(self, update: Message | CallbackQuery) -> Union[bool, Dict[str, Any]]:
        user = await User.get(pk=update.from_user.id)
        if user:
            return user.role_id == 1
        else:
            return False

