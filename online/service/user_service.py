import json
from data_manager.data_manager import DataManager


class UserService:
    @classmethod
    def do_get(self, id: int):
        user = DataManager.get_instance().get_user_by_id(id)
        return json.dumps(user)