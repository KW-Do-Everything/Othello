# 패키지 임포트
from game import State
from pv_mcts import pv_mcts_action, pv_mcts_scores
from tensorflow.keras.models import load_model
import numpy as np

# 베스트 플레이어 모델 로드
model = load_model('/data/yungoon/Othello/Othello/88o/model/best.h5')

# 좌표 변환 (A1~H8 -> 인덱스)
def position_to_index(pos):
    columns = 'ABCDEFGH'
    rows = '12345678'

    if len(pos) != 2:
        raise ValueError("잘못된 입력입니다. 좌표는 두 글자여야 합니다 (예: A1).")

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

# 사람의 턴 추천 수 출력
def recommend_best_action(state, model):
    legal_actions = state.legal_actions()

    # MCTS를 통해 각 수에 대한 승률 계산
    scores = pv_mcts_scores(model, state, temperature=1.0)
    
    # 합법적인 수 중에서 가장 높은 승률을 가진 수 찾기
    best_action = legal_actions[np.argmax(scores)]
    best_action_pos = index_to_position(best_action)
    
    print(f"추천 수: {best_action_pos}, 예상 승률: {scores[np.argmax(scores)] * 100:.2f}%")

# 사람의 턴 입력 처리
def turn_of_human(state, last_human_move):
    legal_actions = state.legal_actions()

    if legal_actions == [64]:
        print("패스합니다.")
        return 64

    # 추천 수 출력
    recommend_best_action(state, model)

    while True:
        pos = input("당신의 수를 입력하세요 (예: A1): ")
        
        try:
            action = position_to_index(pos)
            if action in legal_actions:
                last_human_move[0] = pos  # 마지막 사람 수 저장
                return action
            else:
                print("해당 수는 둘 수 없습니다. 다시 입력하세요.")
        except (ValueError, IndexError) as e:
            print(f"잘못된 입력: {e}. 다시 입력하세요.")

# AI의 턴 처리 (승률 표시 X)
def turn_of_ai(state, next_action, last_ai_move):
    action = next_action(state)
    pos = index_to_position(action)
    last_ai_move[0] = pos  # 마지막 AI 수 저장
    print(f"AI가 선택한 수: {pos}")
    return action

# 보드 출력 (좌표 테두리 포함, o는 사람, x는 AI)
def print_board(state):
    ox = ('o', 'x') if state.is_first_player() else ('x', 'o')
    columns = 'ABCDEFGH'
    rows = '12345678'
    
    print('  ' + ' '.join(columns))
    for y in range(8):
        row_str = rows[y] + ' '
        for x in range(8):
            piece = '-'
            index = x + y * 8
            if state.pieces[index] == 1:
                piece = 'o'
            elif state.enemy_pieces[index] == 1:
                piece = 'x'
            row_str += piece + ' '
        row_str += rows[y]
        print(row_str)
    print('  ' + ' '.join(columns))

# 돌의 수 차이 출력
def print_score_diff(state):
    player_count = state.piece_count(state.pieces)
    enemy_count = state.piece_count(state.enemy_pieces)
    diff = player_count - enemy_count
    print(f"현재 돌 수 차이: 플레이어 {player_count} vs AI {enemy_count} (차이: {diff})")

# 마지막으로 둔 수 출력
def print_last_moves(last_human_move, last_ai_move):
    print(f"마지막 사람 수: {last_human_move[0]}, 마지막 AI 수: {last_ai_move[0]}")

# 게임 실행
def play_game():
    state = State()
    next_action = pv_mcts_action(model, 0.0)

    last_human_move = [None]  # 마지막 사람 수 저장 리스트
    last_ai_move = [None]     # 마지막 AI 수 저장 리스트

    while True:
        print_board(state)
        print_score_diff(state)
        # print_last_moves(last_human_move, last_ai_move)

        if state.is_done():
            break

        if state.is_first_player():
            action = turn_of_human(state, last_human_move)
        else:
            action = turn_of_ai(state, next_action, last_ai_move)

        state = state.next(action)

    if state.is_lose():
        print("AI가 승리했습니다!")
    elif state.is_draw():
        print("무승부입니다!")
    else:
        print("당신이 승리했습니다!")

if __name__ == '__main__':
    play_game()
