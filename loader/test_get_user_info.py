# 사용 예시
# sg_connector = 앞에서 한 클래스(유저 로그인을 확인하고 할당된 task(이때 task는 항
# 목, 진행상태 등의 정보의 일치로 확인한다) 를 찾는다 

from loader_get_user_info import ShotGridConnector
sg_connector = ShotGridConnector()


username = "owlgrowl0v0@gmail.com"
user_data = sg_connector.login_user(username)

if "error" not in user_data:
    print(f"로그인 성공: {user_data}")

    # 1️ Task 목록을 Start Date, Due Date 기준으로 정렬
    sorted_tasks_by_dates = sg_connector.categorize_and_sort_tasks_by_dates()
    print("\n [Task 목록 - Start Date 기준 정렬]")
    for item in sorted_tasks_by_dates["by_start_date"]:
        print(item)

    print("\n [Task 목록 - Due Date 기준 정렬]")
    for item in sorted_tasks_by_dates["by_due_date"]:
        print(item)

    # 2️ Shot 목록을 Start Date, Due Date 기준으로 정렬
    sorted_shots_by_dates = sg_connector.categorize_and_sort_shots_by_dates()
    print("\n [Shot 목록 - Start Date 기준 정렬]")
    for item in sorted_shots_by_dates["by_start_date"]:
        print(item)

    print("\n [Shot 목록 - Due Date 기준 정렬]")
    for item in sorted_shots_by_dates["by_due_date"]:
        print(item)

    # 3️ Asset 목록을 Start Date, Due Date 기준으로 정렬
    sorted_assets_by_dates = sg_connector.categorize_and_sort_assets_by_dates()
    print("\n [Asset 목록 - Start Date 기준 정렬]")
    for item in sorted_assets_by_dates["by_start_date"]:
        print(item)

    print("\n [Asset 목록 - Due Date 기준 정렬]")
    for item in sorted_assets_by_dates["by_due_date"]:
        print(item)

else:
    print(user_data["error"])