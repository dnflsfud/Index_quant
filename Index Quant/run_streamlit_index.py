# main.py

import subprocess
import threading
import os
import sys

class StreamlitApp:
    def __init__(self, app_path, work_dir):
        self.app_path = app_path
        self.work_dir = work_dir
        self.process = None
        self.thread = None

    def start(self):
        if not os.path.exists(self.app_path):
            print(f"'app.py' not found at {self.app_path}")
            return

        def run_app():
            try:
                # 환경 변수에 PYTHONIOENCODING 설정
                env = os.environ.copy()
                env["PYTHONIOENCODING"] = "utf-8"

                self.process = subprocess.Popen(
                    ["streamlit", "run", self.app_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    bufsize=1,  # 실시간 출력을 위해 버퍼 사이즈를 1로 설정
                    universal_newlines=True,  # 텍스트 모드
                    encoding='utf-8',  # utf-8로 디코딩
                    cwd=self.work_dir,  # 작업 디렉토리 변경
                    env=env
                )

                # 실시간 로그 출력
                for line in self.process.stdout:
                    print(f"[Streamlit] {line}", end='')
            except Exception as e:
                print(f"Error running Streamlit app: {e}")

        self.thread = threading.Thread(target=run_app, daemon=True)
        self.thread.start()
        print("Streamlit app started.")

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None
            print("Streamlit app terminated.")
        else:
            print("Streamlit app is not running.")

def main():
    # Streamlit 애플리케이션의 절대 경로와 작업 디렉토리 설정
    app_path = r"C:\Users\westl\PycharmProjects\pythonProject\venv\Index Quant\app_index.py"
    work_dir = r"C:\Users\westl\PycharmProjects\pythonProject\venv\Index Quant"

    # StreamlitApp 인스턴스 생성
    app = StreamlitApp(app_path, work_dir)

    # Streamlit 애플리케이션 시작
    app.start()

    # 메인 애플리케이션의 다른 작업 수행
    try:
        while True:
            cmd = input("Enter command ('stop' to terminate Streamlit, 'exit' to quit): ").strip().lower()
            if cmd == 'stop':
                app.stop()
            elif cmd == 'exit':
                app.stop()
                print("Exiting main application...")
                break
            else:
                print(f"Unknown command: {cmd}")
    except KeyboardInterrupt:
        app.stop()
        print("Main application terminated via KeyboardInterrupt.")

if __name__ == "__main__":
    main()
