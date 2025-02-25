
# 마야의 컬렉션 방법들 

selections = cmds.ls(selections=True) [0]

items = cmds.ls(assembleies=True)
collect = [] 
for item in items:
    if item.startswith("teapot"):
        collect.append(item)



abc_file = f"/home/rapa/test_maya/cache/{selections}_code.abc"

start_frame = cmds.playbackOptions(q=True, min=True)
end_frame = int(cmds.playbackOptions(q=True, max = True)) 


# 알렘빅 캐쉬 옵션 설정
cmd = f"-frameRange {start_frame} {end_frame}"
cmd += "-uvWrite "
cmd += "-worldSpace "
cmd += "-renderrableonly "

# 추가한 커스텀 어트리뷰크 이름 추가 
cmd += "-attr assettype "

#오브젝트 추가 부분
cmd += f"-root {selections} "

# 파일 저장 경로
cmd += f"-file {abc_file}"
cmds.AbcExport(jobArg=cmd)