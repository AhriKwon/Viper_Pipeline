import os
import re

class DCCFileLoader:
    """DCC 소프트웨어에서 새로운 파일을 생성하는 기능을 추가"""

    def __init__(self, base_dir="/nas/show/Viper"):
        self.base_dir = base_dir  # 기본 프로젝트 경로

    def create_new_file(self, part, asset_type=None, asset_name=None, seq=None, shot=None, task=None):
        """
        사용자가 선택한 파트에 맞는 새 파일을 생성하는 함수

        :param part: 사용자가 선택한 파트 (MDL, RIG, LDV, LAY, ANM, LGT, FX, COM)
        :param asset_type: ASSETTYPE (MDL, RIG, LDV에서 필요)
        :param asset_name: ASSETNAME (MDL, RIG, LDV에서 필요)
        :param seq: SEQ (LAY, ANM, LGT, FX, COM에서 필요)
        :param shot: SHOT (LAY, ANM, LGT, FX, COM에서 필요)
        :param task: TASK (필수)
        :return: 생성된 파일의 전체 경로 (str)
        """

        # 경로 템플릿
        file_templates = {
            "MDL": f"{self.base_dir}/assets/{{asset_type}}/{{asset_name}}/{{task}}/work/maya/scenes/{{asset_name}}_{{task}}_v001.ma",
            "RIG": f"{self.base_dir}/assets/{{asset_type}}/{{asset_name}}/{{task}}/work/maya/scenes/{{asset_name}}_{{task}}_v001.ma",
            "LDV": f"{self.base_dir}/assets/{{asset_type}}/{{asset_name}}/{{task}}/work/maya/scenes/{{asset_name}}_{{task}}_v001.ma",
            "LAY": f"{self.base_dir}/seq/{{seq}}/{{shot}}/{{task}}/work/maya/scenes/{{shot}}_{{task}}_v001.ma",
            "ANM": f"{self.base_dir}/seq/{{seq}}/{{shot}}/{{task}}/work/maya/scenes/{{shot}}_{{task}}_v001.ma",
            "LGT": f"{self.base_dir}/seq/{{seq}}/{{shot}}/{{task}}/work/maya/scenes/{{shot}}_{{task}}_v001.ma",
            "FX": f"{self.base_dir}/seq/{{seq}}/{{shot}}/{{task}}/work/houdini/scenes/{{shot}}_{{task}}_v001.hip",
            "COM": f"{self.base_dir}/seq/{{seq}}/{{shot}}/{{task}}/work/nuke/scenes/{{shot}}_{{task}}_v001.nk",
        }

        # 예외 처리: 존재하지 않는 파트
        if part not in file_templates:
            raise ValueError(f"잘못된 파트명입니다: {part}")

        # 파일 경로 생성
        file_path = file_templates[part].format(
            asset_type=asset_type or "Unknown",
            asset_name=asset_name or "Unknown",
            seq=seq or "Unknown",
            shot=shot or "Unknown",
            task=task or "Unknown"
        )

        # 폴더 생성 (존재하지 않으면)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 파일 생성
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write(f"// New {part} file created: {file_path}\n")
            print(f"새 파일 생성 완료: {file_path}")
        else:
            print(f"이미 존재하는 파일입니다: {file_path}")

        return file_path  # 생성된 파일 경로 반환
    

    def version_up(self, file_path):
        """
        파일의 버전을 증가시키는 기능 (v001 → v002 → v003 ...)
        
        :param file_path: 버전 업할 대상 파일 경로 (예: "/path/to/file_v001.ma")
        :return: 새로운 버전 파일 경로 (str)
        """

        # 정규식을 사용하여 파일명에서 v### 찾기 (예: v001, v023)
        version_pattern = re.compile(r"(.*)_v(\d{3})(\..+)$")
        match = version_pattern.match(file_path)

        if match:
            base_name, version_num, extension = match.groups()
            new_version = int(version_num) + 1  # 기존 버전 +1
            new_file_path = f"{base_name}_v{new_version:03d}{extension}"
        else:
            # 기존 버전이 없을 경우 v001을 추가
            base_name, extension = os.path.splitext(file_path)
            new_file_path = f"{base_name}_v001{extension}"

        # 이미 존재하는 파일이 있으면 다시 버전 올리기
        while os.path.exists(new_file_path):
            version_match = version_pattern.match(new_file_path)
            if version_match:
                base_name, version_num, extension = version_match.groups()
                new_version = int(version_num) + 1
                new_file_path = f"{base_name}_v{new_version:03d}{extension}"
            else:
                break  # 더 이상 버전 업이 불가능한 경우

        # 파일 버전 업 실행
        os.rename(file_path, new_file_path)
        print(f"파일 버전 업 완료: {file_path} → {new_file_path}")

        return new_file_path  # 새 파일 경로 반환
    


#####################################################################################################################################################

"""파일생성 코드사용하기"""


loader = DCCFileLoader()

new_file = loader.create_new_file(
    part="MDL",
    asset_type="Character",
    asset_name="Hero",
    task="Modeling"
)
print(f"생성된 파일 경로: {new_file}")
# 결과 # 새 파일 생성 완료: /nas/show/Viper/assets/Character/Hero/Modeling/work/maya/scenes/Hero_Modeling_v001.ma



new_file = loader.create_new_file(
    part="LAY",
    seq="S01",
    shot="S01_001",
    task="Layout"
)
print(f"생성된 파일 경로: {new_file}")
# 결과 # 새 파일 생성 완료: /nas/show/Viper/seq/S01/S01_001/Layout/work/maya/scenes/S01_001_Layout_v001.ma


new_file = loader.create_new_file(
    part="FX",
    seq="S01",
    shot="S01_002",
    task="FX_Simulation"
)
print(f"생성된 파일 경로: {new_file}")
# 결과 # 새 파일 생성 완료: /nas/show/Viper/seq/S01/S01_002/FX_Simulation/work/maya/scenes/S01_002_FX_Simulation_v001.hip


new_file = loader.create_new_file(
    part="COM",
    seq="S02",
    shot="S02_005",
    task="Compositing"
)
print(f"생성된 파일 경로: {new_file}")
# 결과 # 새 파일 생성 완료: /nas/show/Viper/seq/S02/S02_005/Compositing/work/maya/scenes/S02_005_Compositing_v001.nk



"""version up 코드 사용하기"""
loader = DCCFileLoader()
new_file = loader.version_up("/nas/show/Viper/seq/S01/S01_001/Layout/work/maya/scenes/S01_001_Layout_v001.ma")
print(f"새로운 버전 파일: {new_file}")

# 결과 # 파일 버전 업 완료: S01_001_Layout_v001.ma → S01_001_Layout_v002.ma
# 결과 # 새로운 버전 파일: /nas/show/Viper/seq/S01/S01_001/Layout/work/maya/scenes/S01_001_Layout_v002.ma

