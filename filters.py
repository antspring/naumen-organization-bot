from aiogram.filters import BaseFilter


class RoleFilter(BaseFilter):
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    async def __call__(self, message, **kwargs):
        state = kwargs.get("state")
        data = await state.get_data()
        role = data.get("user").role.name

        return role in self.allowed_roles