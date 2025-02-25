import shotgun_api3
from shotgrid_connector import ShotGridConnector

class UserAuthenticator:
    """ShotGrid 사용자 로그인 및 권한 확인"""

    def login(username):
        """사용자 로그인 인증"""
        user = ShotGridConnector.sg.find_one(
            "HumanUser",
            [["login", "is", username]],
            ["id", "name", "permission_rule_set"]
        )
        if user:
            return user
        else:
            None

    def get_user_role(user_id):
        """현재 로그인한 사용자의 역할(Role) 확인"""
        user = ShotGridConnector.sg.find_one(
            "HumanUser",
            [["id", "is", user_id]],
            ["permission_rule_set"]
        )
        if user:
            return user["permission_rule_set"]
        else:
            None