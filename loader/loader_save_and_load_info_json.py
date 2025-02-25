
import json
import os
from shotgun_api3 import Shotgun

# ShotGrid 서버 정보
SHOTGRID_URL = "https://minseo.shotgrid.autodesk.com"
SCRIPT_NAME = "Viper"
API_KEY = "jvceqpsfqvbl1azzcns?haksI"

USER_DATA_FILE = "user_info.json"

class ShotGridAuthManager:
    """ShotGrid API를 사용하여 로그인한 사용자의 정보를 관리하는 클래스"""

    def __init__(self, sg_url, script_name, api_key):
        """
        :param sg_url: ShotGrid 서버 URL
        :param script_name: ShotGrid API 스크립트 이름
        :param api_key: ShotGrid API 키
        """
        self.sg = Shotgun(sg_url, script_name, api_key)

    def login_user(self, username, password):
        """
        ShotGrid에 로그인하고 사용자 정보를 저장.
        (ShotGrid에서는 직접 비밀번호 인증이 안되므로, ID로 사용자 조회)
        
        :param username: 로그인할 사용자의 ID(이메일 또는 ShotGrid 로그인명)
        :param password: 비밀번호 (ShotGrid API에서는 사용하지 않지만 UI에서 필요할 수 있음)
        :return: 사용자 정보 딕셔너리 (또는 오류 메시지)
        """
        try:
            # ShotGrid에서 사용자 정보 조회
            filters = [["login", "is", username]]
            fields = ["id", "name", "email"]
            user = self.sg.find_one("HumanUser", filters, fields)

            if user:
                user_info = {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "login": username
                }
                self.save_user_info(user_info)
                return user_info
            else:
                return {"error": "User not found"}
        except Exception as e:
            return {"error": str(e)}

    def save_user_info(self, user_info):
        """사용자 정보를 JSON 파일에 저장"""
        with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(user_info, f, indent=4)

    def load_user_info(self):
        """저장된 사용자 정보를 JSON 파일에서 불러오기"""
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return None


# 사용 예시
if __name__ == "__main__":
    auth_manager = ShotGridAuthManager(SHOTGRID_URL, SCRIPT_NAME, API_KEY)

    username = input("Enter your username: ")
    password = input("Enter your password: ")  # ShotGrid에서는 사용되지 않음

    user_info = auth_manager.login_user(username, password)
    print("Login Info:", user_info)

    # 저장된 사용자 정보 불러오기
    print("Stored User Info:", auth_manager.load_user_info())







##########################################################################################################
########################################## 오류 발생 시 수정코드 ###########################################
##########################################################################################################




import json
import os
from shotgun_api3 import Shotgun

# ShotGrid 서버 정보
SHOTGRID_URL = "https://minseo.shotgrid.autodesk.com"
SCRIPT_NAME = "Viper"
API_KEY = "jvceqpsfqvbl1azzcns?haksI"

USER_DATA_FILE = os.path.expanduser("~/user_info.json")  # 홈 디렉토리에 저장

class ShotGridAuthManager:
    """ShotGrid API를 사용하여 로그인한 사용자의 정보를 관리하는 클래스"""

    def __init__(self, sg_url, script_name, api_key):
        try:
            self.sg = Shotgun(sg_url, script_name, api_key)
        except Exception as e:
            raise Exception(f"Shotgun API 연결 실패: {e}")

    def login_user(self, username, password=None):
        """
        ShotGrid에 로그인하고 사용자 정보를 저장.
        """
        try:
            filters = [["login", "is", username]]
            fields = ["id", "name", "email"]
            user = self.sg.find_one("HumanUser", filters, fields)

            if user:
                user_info = {
                    "id": user.get("id", "Unknown"),
                    "name": user.get("name", "Unknown"),
                    "email": user.get("email", "Unknown"),
                    "login": username
                }
                self.save_user_info(user_info)
                return user_info
            else:
                return {"error": "User not found"}
        except Exception as e:
            return {"error": str(e)}

    def save_user_info(self, user_info):
        """사용자 정보를 JSON 파일에 저장"""
        try:
            with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(user_info, f, indent=4)
        except Exception as e:
            print(f"파일 저장 오류: {e}")

    def load_user_info(self):
        """저장된 사용자 정보를 JSON 파일에서 불러오기"""
        if os.path.exists(USER_DATA_FILE):
            try:
                with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

# 실행 예제
if __name__ == "__main__":
    auth_manager = ShotGridAuthManager(SHOTGRID_URL, SCRIPT_NAME, API_KEY)
    username = input("Enter your username: ")
    password = input("Enter your password: ")  # UI 용도로만 사용

    user_info = auth_manager.login_user(username, password)
    print("Login Info:", user_info)
    print("Stored User Info:", auth_manager.load_user_info())
