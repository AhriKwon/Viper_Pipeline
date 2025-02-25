"""
로그인한 유저의 정보를 딕셔너리로 저장 및 불러오기

"""

import pickle
import os
from shotgun_api3 import Shotgun

# ShotGrid 서버 정보
SHOTGRID_URL = "https://minseo.shotgrid.autodesk.com"
SCRIPT_NAME = "Viper"
API_KEY = "jvceqpsfqvbl1azzcns?haksI"

USER_DATA_FILE = "user_data.pkl"

def save_user_info(user_info):
    """사용자 정보를 파일에 저장합니다."""
    with open(USER_DATA_FILE, "wb") as f:
        pickle.dump(user_info, f)

def load_user_info():
    """저장된 사용자 정보를 불러옵니다."""
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "rb") as f:
            return pickle.load(f)
    return None

def login_user(username, password):
    """ShotGrid에 로그인하고 사용자 정보를 저장합니다."""
    try:
        sg = Shotgun(SHOTGRID_URL, SCRIPT_NAME, API_KEY)
        
        # ShotGrid에서 사용자 정보 가져오기
        filters = [["login", "is", username]]
        fields = ["id", "name", "email"]
        user = sg.find_one("HumanUser", filters, fields)
        
        if user:
            user_info = {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "login": username
            }
            save_user_info(user_info)
            return user_info
        else:
            return {"error": "User not found"}
    except Exception as e:
        return {"error": str(e)}

# 사용 예시
if __name__ == "__main__":
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    user_info = login_user(username, password)
    print("Login Info:", user_info)
    
    # 저장된 사용자 정보 불러오기
    print("Stored User Info:", load_user_info())





######################################################################################################
########################################### 오류 시 수정 코드 #########################################
######################################################################################################



import pickle
import os
from shotgun_api3 import Shotgun

# ShotGrid 서버 정보
SHOTGRID_URL = "https://minseo.shotgrid.autodesk.com"
SCRIPT_NAME = "Viper"
API_KEY = "jvceqpsfqvbl1azzcns?haksI"

USER_DATA_FILE = os.path.expanduser("~/user_data.pkl")  # 홈 디렉토리에 저장

def save_user_info(user_info):
    """사용자 정보를 파일에 저장합니다."""
    try:
        with open(USER_DATA_FILE, "wb") as f:
            pickle.dump(user_info, f)
    except Exception as e:
        print(f"파일 저장 오류: {e}")

def load_user_info():
    """저장된 사용자 정보를 불러옵니다."""
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "rb") as f:
                return pickle.load(f)
        except (EOFError, pickle.UnpicklingError):
            return {}  # 파일이 손상된 경우 기본값 반환
    return {}

def login_user(username, password=None):
    """ShotGrid에 로그인하고 사용자 정보를 저장합니다."""
    try:
        sg = Shotgun(SHOTGRID_URL, SCRIPT_NAME, API_KEY)
        
        # ShotGrid에서 사용자 정보 가져오기
        filters = [["login", "is", username]]
        fields = ["id", "name", "email"]
        user = sg.find_one("HumanUser", filters, fields)
        
        if user:
            user_info = {
                "id": user.get("id", "Unknown"),
                "name": user.get("name", "Unknown"),
                "email": user.get("email", "Unknown"),
                "login": username
            }
            save_user_info(user_info)
            return user_info
        else:
            return {"error": "User not found"}
    except Exception as e:
        return {"error": str(e)}

# 사용 예시
if __name__ == "__main__":
    username = input("Enter your username: ")
    password = input("Enter your password: ")  # ShotGrid에서는 사용되지 않음
    user_info = login_user(username, password)
    print("Login Info:", user_info)
    
    print("Stored User Info:", load_user_info())
