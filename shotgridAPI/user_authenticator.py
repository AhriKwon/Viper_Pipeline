from shotgrid_db import ShotgridDB
from shotgrid_connector import ShotGridAPI
sg_db = ShotgridDB()
sg_api = ShotGridAPI()

class UserAuthenticator:
    """
    ShotGrid 사용자 로그인 및 권한 확인
    """

    @staticmethod
    def get_user(email):
        """
        사용자 로그인 인증
        """
        user = sg_api.sg.find_one(
            "HumanUser",
            [["login", "is", email]],
            ["id", "name", "login", "permission_rule_set"]
        )

        if user:
            return user
        else:
            None

    @staticmethod
    def get_user_role(user_id):
        """
        현재 로그인한 사용자의 역할(Role) 확인
        """
        user = sg_db.sg.find_one(
            "HumanUser",
            [["id", "is", user_id]],
            ["permission_rule_set"]
        )
        if user:
            return user["permission_rule_set"]
        else:
            None
    
    @staticmethod
    def login(email):
        """
        유저 로그인 시 데이터베이스에 유저 데이터가 있으면 API 호출 없이 로그인 처리
        """
        # 데이터베이스에서 유저 정보 조회
        user = sg_db.get_user_data(email)  # DB에서 유저 데이터 가져오기
        if user:
            print(f"{email} 데이터베이스에서 로그인 완료 (API 호출 스킵)")
            return user  # 기존 데이터 반환

        # 데이터베이스에 정보가 없으면 ShotGrid API 호출
        print(f"ShotGrid API 호출: {email} 로그인 중...")
        user = UserAuthenticator.get_user(email)  # ShotGrid API로 유저 정보 가져오기
        if not user:
            print("로그인 실패: 유저를 찾을 수 없습니다.")
            return None

        # ShotGrid에서 유저 프로젝트 정보 가져오기
        user_projects = sg_api.get_user_projects(user['id'])
        user["projects"] = []  # 프로젝트 데이터를 저장할 리스트

        for project in user_projects:
            project_data = sg_api.get_project_details(project["id"])
            sg_db.save_project_data(project_data)  # DB에 저장
            user["projects"].append(project_data)  # 유저 데이터에 프로젝트 추가

        # 유저 정보를 데이터베이스에 저장하여 다음 로그인 시 API 호출 없이 처리
        sg_db.save_user_data(user)
        print(f"{email} 데이터베이스에 저장 완료")

        return user