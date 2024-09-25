# ====================
# 사람과 AI의 대전 (커맨드 창 입력 방식, 돌의 수 차이 출력 및 입력 검증)
# ====================

# 패키지 임포트
from game import State
from pv_mcts import pv_mcts_action
from tensorflow.keras.models import load_model

# 베스트 플레이어 모델 로드
model = load_model('/data/yungoon/Othello/88o/model/best.h5')

# 좌표 변환 (A1~H8 -> 인덱스)
def position_to_index(pos):
    columns = 'ABCDEFGH'
    rows = '12345678'

    # 입력 길이 검증
    if len(pos) != 2:
        raise ValueError("잘못된 입력입니다. 좌표는 두 글자여야 합니다 (예: A1).")

    # 입력 열과 행이 유효한지 검증
    if pos[0].upper() not in columns or pos[1] not in rows:
        raise ValueError("잘못된 입력입니다. 좌표는 A1~H8 범위 내에 있어야 합니다.")
    
    x = columns.index(pos[0].upper())
    y = rows.index(pos[1])
    return x + y * 8

# 인덱스를 좌표로 변환
def index_to_position(index):
    columns = 'ABCDEFGH'
    rows = '12345678'
    x = index % 8
    y = index // 8
    return f"{columns[x]}{rows[y]}"

# 사람의 턴 입력 처리
def turn_of_human(state):
    legal_actions = state.legal_actions()

    # 패스해야 하는 경우
    if legal_actions == [64]:
        print("패스합니다.")
        return 64

    while True:
        # 좌표 입력
        pos = input("당신의 수를 입력하세요 (예: A1): ")
        
        # 입력 검증
        try:
            action = position_to_index(pos)
            if action in legal_actions:
                return action
            else:
                print("해당 수는 둘 수 없습니다. 다시 입력하세요.")
        except (ValueError, IndexError) as e:
            print(f"잘못된 입력: {e}. 다시 입력하세요.")

# AI의 턴 처리
def turn_of_ai(state, next_action):
    action = next_action(state)
    pos = index_to_position(action)
    print(f"AI가 선택한 수: {pos}")
    return action

# 보드 출력 (좌표 테두리 포함)
def print_board(state):
    ox = ('o', 'x') if state.is_first_player() else ('x', 'o')
    columns = 'ABCDEFGH'
    rows = '12345678'
    
    # 상단 좌표 출력
    print('  ' + ' '.join(columns))

    for y in range(8):
        row_str = rows[y] + ' '  # 좌측 좌표 출력
        for x in range(8):
            piece = '-'
            index = x + y * 8
            if state.pieces[index] == 1:
                piece = ox[0]
            elif state.enemy_pieces[index] == 1:
                piece = ox[1]
            row_str += piece + ' '
        row_str += rows[y]  # 우측 좌표 출력
        print(row_str)

    # 하단 좌표 출력
    print('  ' + ' '.join(columns))

# 돌의 수 차이 출력
def print_score_diff(state):
    player_count = state.piece_count(state.pieces)
    enemy_count = state.piece_count(state.enemy_pieces)
    diff = player_count - enemy_count
    print(f"현재 돌 수 차이: 플레이어 {player_count} vs 상대 {enemy_count} (차이: {diff})")

# 게임 실행
def play_game():
    # 상태 생성
    state = State()

    # PV MCTS를 활용한 행동을 선택하는 함수 생성
    next_action = pv_mcts_action(model, 0.0)

    # 게임 종료 시까지 반복
    while True:
        # 현재 보드 출력
        print_board(state)

        # 돌 수 차이 출력
        print_score_diff(state)

        # 게임 종료 시
        if state.is_done():
            break

        # 사람의 턴
        if state.is_first_player():
            action = turn_of_human(state)
        else:
            # AI의 턴
            action = turn_of_ai(state, next_action)

        # 다음 상태로 전환
        state = state.next(action)

    # 게임 결과 출력
    if state.is_lose():
        print("AI가 승리했습니다!")
    elif state.is_draw():
        print("무승부입니다!")
    else:
        print("당신이 승리했습니다!")

# 게임 시작
if __name__ == '__main__':
    play_game()
