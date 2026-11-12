# Bổ sung AI cấp 1 và cấp 2 cho Caro 9x9

## Cấu trúc

```text
Co-Caro/
├── main.py                  # giao diện Pygame
├── core/
│   ├── board.py              # ma trận và thao tác bàn cờ
│   └── game.py               # lượt chơi, luật thắng, kết quả
├── agents/                   # Random, Heuristic, Minimax, MCTS, Supervised
├── training/                 # dataset, policy model, lệnh train
├── evaluation/               # tournament, thống kê, kết quả JSON
├── tests/                    # kiểm thử game và agent
├── data/                     # dữ liệu đầu vào/xử lý
└── models/checkpoints/        # model đã huấn luyện
```

`game.py` và `board.py` ở thư mục gốc chỉ giữ vai trò tương thích với các import cũ; code mới nên dùng `core.game` và `core.board`.

## API mà main.py mong đợi từ game.py

`game.py` cần có lớp `CaroGame` và các thành phần:

- `CaroGame(size=9)`
- `reset()`
- `board`: ma trận, 0 là ô trống, 1 là X, 2 là O
- `current_player`: 1 hoặc 2
- `game_over`: trạng thái kết thúc
- `winning_cells`: danh sách tọa độ thắng (có thể để trống nếu engine chưa lưu)
- `legal_actions()`: danh sách `(row, col)` còn trống
- `make_move(row, col)`: trả về True nếu đi hợp lệ
- `result()`: None, `"DRAW"`, `"X"` hoặc `"O"`

Hai agent chỉ cần `board`, `current_player` và `legal_actions()`; không sửa bàn cờ khi tính nước đi.

## Cài đặt và chạy

Mở terminal tại thư mục dự án, kích hoạt môi trường ảo rồi cài Pygame nếu chưa có:

```powershell
.venv\Scripts\activate
python -m pip install pygame
```

Chạy giao diện:

```powershell
python main.py
```

- Nhấn `1`: hai người chơi.
- Nhấn `2`: người chơi X đấu AI Random cấp 1 (O).
- Nhấn `3`: người chơi X đấu AI Heuristic cấp 2 (O).
- Nhấn `4`: Minimax với Alpha-Beta Pruning.
- Nhấn `5`: Monte Carlo Tree Search (MCTS).
- Nhấn `6`: AI Supervised; nếu chưa có checkpoint, tạm dùng Heuristic.
- Nhấn `T`: chạy giải round-robin giữa các AI trong nền.
- Nhấn `S`: xem bảng xếp hạng và thống kê giải gần nhất.
- Nhấn `R`: chơi lại.
- Nhấn `ESC`: thoát.

## Huấn luyện AI Supervised

Policy network học chọn nước đi từ các ván tự sinh do Heuristic làm giáo viên. Chạy lệnh sau tại thư mục dự án để tạo checkpoint mặc định tại `models/checkpoints/caro_policy.pt`:

```powershell
python -m training.train --games 50 --epochs 12
```

Sau khi huấn luyện, khởi động lại game và chọn chế độ 6. Có thể đổi số ván, số epoch hoặc đường dẫn checkpoint bằng các tham số `--games`, `--epochs` và `--output`.

## Đấu giải và kiểm thử

Kết quả giải được lưu tại `evaluation/results/latest_tournament.json`. Có thể chạy giải độc lập từ terminal:

```powershell
python -m evaluation.tournament --games-per-pair 2
```

Chạy toàn bộ kiểm thử:

```powershell
python -m unittest discover -s tests -v
```

## Luật exact-five

`would_win()` đếm chuỗi qua nước đi giả định. Một hướng chỉ thắng khi tổng số quân liên tiếp bằng đúng 5. Không yêu cầu đầu chuỗi mở, do đó chuỗi 5 bị chặn vẫn thắng. Chuỗi 6 trở lên không thắng theo hướng đó. Engine trong `game.py` vẫn là nơi quyết định kết quả ván đấu; logic trong agent chỉ giúp chọn nước đi.
