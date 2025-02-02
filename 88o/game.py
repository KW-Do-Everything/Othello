# ====================
# 오셀로
# ====================

# 패키지 임포트
import random
import math


# 게임 상태
class State:
    # 초기화
    def __init__(self, pieces=None, enemy_pieces=None, depth=0):
        # 방향 정수
        self.dxy = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))

        # 연속 패스에 따른 종료
        self.pass_end = False

        # 돌의 배치
        self.pieces = pieces
        self.enemy_pieces = enemy_pieces
        self.depth = depth

        # 돌의 초기 배치
        if pieces is None or enemy_pieces is None:
            self.pieces = [0] * 64  # 8x8 보드 크기
            self.pieces[27], self.pieces[36] = 1, 1  # 흑돌 중앙 배치
            self.enemy_pieces = [0] * 64  # 8x8 보드 크기
            self.enemy_pieces[28], self.enemy_pieces[35] = 1, 1  # 백돌 중앙 배치

    # 돌의 수 얻기
    def piece_count(self, pieces):
        return sum(pieces)  # 돌이 1인 것만 세기

    # 패배 여부 판정
    def is_lose(self):
        return self.is_done() and self.piece_count(self.pieces) < self.piece_count(self.enemy_pieces)

    # 무승부 여부 판정
    def is_draw(self):
        return self.is_done() and self.piece_count(self.pieces) == self.piece_count(self.enemy_pieces)

    # 게임 종료 여부 판정
    def is_done(self):
        return self.piece_count(self.pieces) + self.piece_count(self.enemy_pieces) == 64 or self.pass_end

    # 다음 상태 얻기
    def next(self, action):
        state = State(self.pieces.copy(), self.enemy_pieces.copy(), self.depth + 1)
        if action != 64:
            state.is_legal_action_xy(action % 8, action // 8, True)
        state.pieces, state.enemy_pieces = state.enemy_pieces, state.pieces

        # 2회 연속 패스 판정
        if action == 64 and state.legal_actions() == [64]:
            state.pass_end = True
        return state

    # 합법적인 수 리스트 얻기
    def legal_actions(self):
        actions = []
        for j in range(8):
            for i in range(8):
                if self.is_legal_action_xy(i, j):
                    actions.append(i + j * 8)
        if len(actions) == 0:
            actions.append(64)  # 패스
        return actions

    # 임의의 매스가 합법적인 수인지 판정
    def is_legal_action_xy(self, x, y, flip=False):
        # 임의의 매스에서 임의의 방향이 합법적인 수인지 판정
        def is_legal_action_xy_dxy(x, y, dx, dy):
            # 첫 번째 상대 돌 확인
            x, y = x + dx, y + dy
            if y < 0 or y >= 8 or x < 0 or x >= 8 or self.enemy_pieces[x + y * 8] != 1:
                return False

            # 2번째 이후
            for j in range(8):
                if y < 0 or y >= 8 or x < 0 or x >= 8 or (self.enemy_pieces[x + y * 8] == 0 and self.pieces[x + y * 8] == 0):
                    return False

                if self.pieces[x + y * 8] == 1:
                    if flip:
                        for i in range(8):
                            x, y = x - dx, y - dy
                            if self.pieces[x + y * 8] == 1:
                                return True
                            self.pieces[x + y * 8] = 1
                            self.enemy_pieces[x + y * 8] = 0
                    return True
                x, y = x + dx, y + dy
            return False

        # 빈칸 여부 확인
        if self.enemy_pieces[x + y * 8] == 1 or self.pieces[x + y * 8] == 1:
            return False

        if flip:
            self.pieces[x + y * 8] = 1

        flag = False
        for dx, dy in self.dxy:
            if is_legal_action_xy_dxy(x, y, dx, dy):
                flag = True
        return flag

    # 선 수 여부 확인
    def is_first_player(self):
        return self.depth % 2 == 0

    # 문자열 표시
    def __str__(self):
        ox = ('o', 'x') if self.is_first_player() else ('x', 'o')
        str_board = ''
        for i in range(64):
            if self.pieces[i] == 1:
                str_board += ox[0]
            elif self.enemy_pieces[i] == 1:
                str_board += ox[1]
            else:
                str_board += '-'
            if i % 8 == 7:
                str_board += '\n'
        return str_board


# 랜덤으로 행동 선택
def random_action(state):
    legal_actions = state.legal_actions()
    return legal_actions[random.randint(0, len(legal_actions) - 1)]


# 동작 확인
if __name__ == '__main__':
    # 상태 생성
    state = State()

    # 게임 종료 시까지 반복
    while True:
        # 게임 종료 시
        if state.is_done():
            break

        # 다음 상태 얻기
        state = state.next(random_action(state))

        # 문자열 출력
        print(state)
        print()
