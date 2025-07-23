# **의사양반** Discord Bot

**의사양반**은 <u>Discord 서버와 Minecraft 서버를 연동</u>해주는 봇입니다.

---

## 주요 기능

- **Minecraft RCON**: Discord 채팅창을 통해 Minecraft 서버에 명령어를 전송할 수 있습니다.
- **Minecraft: JE - Discord Link**: Minecraft 서버와 Discord 서버를 연동하여, 유기적인 이벤트를 구현합니다.
- **Accout Linking**: Discord 사용자와 Minecraft 계정을 연결합니다.
- **기타 기능**: Discord 서버 관리, Youtube 음원 재생 등 다양한 기능을 제공합니다.

---

## 설치 및 실행 방법

1.  **저장소 복제(Clone)**
    ```bash
    git clone https://github.com/your-username/UeSaYangban_py.git
    cd UeSaYangban_py
    ```

2.  **가상 환경 생성 및 활성화**
    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate

    # macOS / Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **필요한 라이브러리 설치**
    ```bash
    pip install -r requirements.txt
    ```
    *참고: `requirements.txt` 파일이 없다면, `pip install discord.py`를 실행하여 필요한 라이브러리를 직접 설치해주세요.*

4.  **설정 파일 준비**
    - `config.template.json` 파일을 복사하여 `config.json` 파일을 생성합니다.
    - `config.json` 파일을 열어 `YOUR_TOKEN_HERE` 부분을 실제 Discord 봇 토큰으로 교체합니다.
      ```json
      {
        "token": "여기에_실제_봇_토큰을_입력하세요"
      }
      ```
    *보안을 위해 `config.json` 파일은 Git 버전 관리에서 제외됩니다.*

5.  **봇 실행**
    ```bash
    python bot.py
    ```

---

## 명령어

- > 테스트
  > - `/hello`: 유저 확인 테스트
  > - `/say`: arguments 테스트
  > - `/dm`: DM 테스트

---
