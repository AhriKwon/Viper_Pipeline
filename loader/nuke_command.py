# import socket
# from PySide6.QtWidgets import QFileDialog, QApplication

# class NukeCommandSender:
#     """Nuke와 TCP 통신을 위한 정적 메서드 클래스"""

#     @staticmethod
#     def import_nuke(command, host="127.0.0.1", port=7007):
#         """Nuke에 Python 명령을 보내고 실행 결과를 받는 정적 메서드"""
#         try:
#             client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             client.connect((host, port))
#             client.send(command.encode("utf-8"))

#             response = client.recv(4096)
#             print(response.decode("utf-8"))
        
#         except ConnectionRefusedError:
#             print("오류: Nuke 서버가 실행되지 않았습니다. 먼저 Nuke를 실행하세요.")
        
#         except Exception as e:
#             print(f"오류 발생: {e}")
        
#         finally:
#             client.close()

#     @staticmethod
#     def select_and_import_nuke():
#         """사용자가 직접 Nuke 파일(.nk)을 선택하여 Import하는 기능"""
#         # 기존 QApplication 인스턴스 확인 (이미 실행 중이면 새로 만들지 않음)
#         app = QApplication.instance()
#         if app is None:
#             app = QApplication([])
            
#         file_dialog = QFileDialog()
#         file_path, _ = file_dialog.getOpenFileName(None, "Nuke 파일 선택", "", "Nuke Files (*.nk);;All Files (*.*)")

#         if not file_path:
#             print("파일 선택이 취소되었습니다.")
#             return
        
#         # Nuke에 Import 명령 실행
#         command = f"nuke.nodePaste(r'{file_path}')"
#         NukeCommandSender.import_nuke(command)


import socket


class NukeCommandSender:
    """Nuke와의 TCP 통신을 위한 정적 메서드를 제공하는 클래스"""

    

    @staticmethod
    def import_nuke(command, host="127.0.0.1", port=7007):
        """Nuke에 Python 명령을 보내고 실행 결과를 받는 정적 메서드"""
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, port))
            client.send(command.encode("utf-8"))

            response = client.recv(4096)
            print(response.decode("utf-8"))
        
        except ConnectionRefusedError:
            print("오류: Nuke 서버가 실행되지 않았습니다. 먼저 Nuke를 실행하세요.")
        
        except Exception as e:
            print(f"오류 발생: {e}")
        
        finally:
            client.close()

# 예제 실행 (다른 GUI에서도 사용 가능)
nk_file_path = "/home/rapa/test_nuke/nuke_api.nk"
NukeCommandSender.import_nuke(f"nuke.nodePaste(r'{nk_file_path}')")

# import socket

# def send_command(command, host="127.0.0.1", port=7007):
#     client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client.connect((host, port))
#     client.send(command.encode("utf-8"))

#     response = client.recv(4096)
#     print (response.decode("utf-8"))

# nk_file_path = "/home/rapa/test_nuke/nuke_api.nk"
# send_command(f"nuke.nodePaste(r'{nk_file_path}')")



"""환경변수 코드"""
# import socket
# import threading
# import nuke

# def handle_client(client_socket):
#     """클라이언트에서 받은 Python 명령 실행"""
#     with client_socket:
#         data = client_socket.recv(1024).decode("utf-8")
#         print(f"Received command: {data}")

#         try:
#             exec(data)  # 받은 Python 명령 실행
#             response = "Command executed successfully"
#         except Exception as e:
#             response = f"Error: {e}"

#         client_socket.send(response.encode("utf-8"))

# def start_nuke_server():
#     """Nuke에서 외부 명령을 받을 TCP 서버 실행"""
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.bind(("127.0.0.1", 7007))  # 🔹 포트 7007에서 수신
#     server.listen(5)

#     print("✅ Nuke command server started on port 7007...")

#     while True:
#         client_socket, addr = server.accept()
#         client_handler = threading.Thread(target=handle_client, args=(client_socket,))
#         client_handler.start()

# # 🔹 Nuke 실행이 멈추지 않도록 백그라운드 스레드에서 실행
# server_thread = threading.Thread(target=start_nuke_server, daemon=True)
# server_thread.start()

