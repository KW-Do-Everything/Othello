# ====================
# 사람과 AI의 대전 (8x8 보드)
# ====================

# 패키지 임포트
from game import State
from pv_mcts import pv_mcts_action
from tensorflow.keras.models import load_model
import tkinter as tk

# 베스트 플레이어 모델 로드
model = load_model('yungoon/Othello/8_2_reversi/model/best.h5')


# 게임 UI 정의
class GameUI(tk.Frame):
    # 초기화
    def __init__(self, master=None, model=None):
        tk.Frame.__init__(self, master)
        self.master.title('오셀로')

        # 게임 상태 생성
        self.state = State()

        # PV MCTS를 활용한 행동을 선택하는 함수 생성
        self.next_action = pv_mcts_action(model, 0.0)

        # 캔버스 생성 (8x8에 맞춘 크기)
        self.c = tk.Canvas(self, width=320, height=320, highlightthickness=0)
        self.c.bind('<Button-1>', self.turn_of_human)
        self.c.pack()

        # 화면 갱신
        self.on_draw()

    # 사람의 턴
    def turn_of_human(self, event):
        # 게임 종료 시
        if self.state.is_done():
            self.state = State()
            self.on_draw()
            return

        # 선 수가 아닌 경우
        if not self.state.is_first_player():
            return

        # 클릭 위치를 행동으로 변환
        x = int(event.x / 40)
        y = int(event.y / 40)
        if x < 0 or 7 < x or y < 0 or 7 < y:  # 8x8 범위 외
            return
        action = x + y * 8  # 8x8 인덱스 변환

        # 합법적인 수가 아닌 경우
        legal_actions = self.state.legal_actions()
        if legal_actions == [64]:
            action = 64  # 패스
        if action != 64 and not (action in legal_actions):
            return

        # 다음 상태 얻기
        self.state = self.state.next(action)
        self.on_draw()

        # AI의 턴
        self.master.after(1, self.turn_of_ai)

    # AI의 턴
    def turn_of_ai(self):
        # 게임 종료 시
        if self.state.is_done():
            return

        # 행동 얻기
        action = self.next_action(self.state)

        # 다음 상태 얻기
        self.state = self.state.next(action)
        self.on_draw()

    # 돌 그리기
    def draw_piece(self, index, first_player):
        x = (index % 8) * 40 + 5
        y = int(index / 8) * 40 + 5
        if first_player:
            self.c.create_oval(x, y, x + 30, y + 30, width=1.0, outline='#000000', fill='#C2272D')
        else:
            self.c.create_oval(x, y, x + 30, y + 30, width=1.0, outline='#000000', fill='#FFFFFF')

    # 화면 갱신
    def on_draw(self):
        self.c.delete('all')
        self.c.create_rectangle(0, 0, 320, 320, width=0.0, fill='#C69C6C')
        for i in range(1, 8):
            self.c.create_line(0, i * 40, 320, i * 40, width=1.0, fill='#000000')
            self.c.create_line(i * 40, 0, i * 40, 320, width=1.0, fill='#000000')
        for i in range(64):
            if self.state.pieces[i] == 1:
                self.draw_piece(i, self.state.is_first_player())
            if self.state.enemy_pieces[i] == 1:
                self.draw_piece(i, not self.state.is_first_player())


# 게임 UI 실행
f = GameUI(model=model)
f.pack()
f.mainloop()
