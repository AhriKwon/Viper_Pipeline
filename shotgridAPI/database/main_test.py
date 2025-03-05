from shotgrid_manager import ShotGridManager

if __name__ == "__main__":
    manager = ShotGridManager()

    # 유저 ID로 Task 조회
    user_id = 132
    tasks = manager.get_user_tasks(user_id)
    print(f"🔍 유저 {user_id}의 테스크 목록: {tasks}")

    # 특정 프로젝트의 에셋 조회
    project_name = "Viper"
    assets = manager.get_project_assets(project_name)
    print(f"📂 프로젝트 {project_name}의 에셋 목록: {assets}")

    # 특정 Task의 퍼블리시 파일 가져오기
    task_id = 1234
    published_files = manager.get_task_published_files(task_id)
    print(f"🗂 Task {task_id}의 퍼블리시 파일: {published_files}")

    # 로컬 Work 파일 검색
    work_files = manager.find_work_files(project_name)
    print(f"💾 로컬 Work 파일 목록: {work_files}")

    # 특정 Task 설명 업데이트
    manager.update_task_description(task_id, "이 테스크는 중요함!")

    manager.close()
