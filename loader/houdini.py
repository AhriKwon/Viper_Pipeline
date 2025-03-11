import sys
import os
import codecs

# UTF-8 인코딩 강제 설정
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# 환경 변수 설정
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LC_ALL"] = "en_US.UTF-8"
os.environ["LANG"] = "en_US.UTF-8"

# Houdini 실행 테스트
# import hou
# print("✅ Houdini Python 실행 가능")
