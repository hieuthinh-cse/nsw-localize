# nsw-localize

CLI Python dùng [`nstool`](https://github.com/jakcron/nstool) để trích xuất nội dung NSP và NCA phục vụ quy trình Việt hoá game Nintendo Switch.

Chỉ sử dụng với game, firmware và keyset bạn tự dump từ thiết bị của mình và sở hữu hợp pháp. Công cụ này không kèm key, game, hay cơ chế vượt qua bảo vệ bản quyền.

## Yêu cầu

- [uv](https://docs.astral.sh/uv/) và Python 3.9 trở lên.
- File binary `nstool` tương thích với hệ điều hành. Mặc định CLI tự nhận diện `./nstool.exe` trên Windows hoặc `./nstool` trên macOS/Linux tại thư mục dự án; dùng `--nstool PATH` nếu muốn chỉ định đường dẫn binary khác.
- Với NCA được mã hoá: keyset hợp lệ (ví dụ `prod.keys`) bạn tự dump. Không commit keyset vào Git.

## Chạy CLI

Từ thư mục dự án, `uv` sẽ tạo môi trường cần thiết tự động:

```sh
uv run nsl --help
uv run nsl unpack --help
uv run nsl unpack nsp --help
uv run nsl unpack nca --help
uv run nsl merge-nca --help
```

## Trích xuất NSP

Lệnh này giải nén PFS0 trong package vào thư mục đích và in ra các file `.nca` đã tìm thấy.

```sh
uv run nsl unpack nsp "game.nsp" --output extracted/game
```

Ví dụ chọn binary `nstool` khác:

```sh
uv run nsl unpack nsp "game.nsp" --output extracted/game --nstool /path/to/nstool
```

## Trích xuất NCA

Lệnh sau trích xuất root của NCA. Cần cung cấp keyset bằng `--keyset`.

```sh
uv run nsl unpack nca extracted/game/program.nca \
  --keyset /path/to/prod.keys \
  --output extracted/romfs
```

Dùng `--virtual-path` để trích xuất một path/partition cụ thể theo cú pháp của `nstool`, ví dụ partition `/0`:

```sh
uv run nsl unpack nca extracted/game/program.nca \
  --keyset /path/to/prod.keys \
  --virtual-path /0 \
  --output extracted/partition-0
```

## Hợp nhất RomFS từ Base NCA và Update NCA (`merge-nca`)

Khi game có bản cập nhật (Update), các file mới được lưu dưới dạng BKTR diff trong file Update Program NCA. Lệnh `merge-nca` sẽ áp dụng bản vá lên Base Program NCA và trích xuất ra thư mục RomFS (`/1`) hoàn chỉnh:

```sh
uv run nsl merge-nca \
  --base extracted/base/program.nca \
  --patch extracted/update/program.nca \
  --output extracted/merged_romfs
```

Nếu không truyền `--keyset`, CLI sẽ tự động tìm `~/.switch/prod.keys`. Bạn cũng có thể truyền rõ:

```sh
uv run nsl merge-nca \
  --base extracted/base/program.nca \
  --patch extracted/update/program.nca \
  --keyset /path/to/prod.keys \
  --tik extracted/update/patch.tik \
  --output extracted/merged_romfs
```

## An toàn khi ghi file

CLI kiểm tra input, keyset và binary trước khi chạy `nstool`. Thư mục output đã có nội dung sẽ bị từ chối mặc định để tránh ghi đè nhầm. Chỉ dùng `--overwrite` khi bạn chấp nhận cho `nstool` ghi vào thư mục đó:

```sh
uv run nsl unpack nsp "game.nsp" --output extracted/game --overwrite
```

`--overwrite` không xoá các file cũ; nên dùng thư mục output trống cho mỗi lần trích xuất để tránh lẫn file cũ và mới.

## Kiểm thử

Không cần game hoặc key thật để chạy test vì process `nstool` được mock:

```sh
uv run python -m unittest discover -s tests -v
```

## Discord Bot (`nsl-bot`)

Bot Discord hỗ trợ slash command `/create` để tự động khởi tạo thư mục dự án Việt hoá bên dưới `projects/`.

### Thiết lập Discord Bot

1. Tạo một ứng dụng và Bot trên [Discord Developer Portal](https://discord.com/developers/applications).
2. Phân quyền và phạm vi bot:
   - Scopes: `bot`, `applications.commands`
   - Quyền tối thiểu: `View Channels`, `Send Messages`, `Create Public Threads`, `Send Messages in Threads`, `Use Application Commands`
3. Mời bot vào server (guild) của bạn.

### Biến môi trường

Bot hỗ trợ tự động nạp cấu hình từ file `.env` (thông qua `python-dotenv`). Nếu biến môi trường hệ thống đã được `export` sẵn, hệ thống sẽ ưu tiên giá trị từ môi trường thay vì file `.env`. Bạn có thể sao chép file `.env.example` thành `.env` để cấu hình:

```sh
cp .env.example .env
```

Các biến môi trường hỗ trợ:

- `DISCORD_TOKEN`: Token của Discord bot (bắt buộc).
- `DISCORD_CREATE_ROLE_IDS`: Danh sách ID vai trò (role) được phép tạo dự án và tương tác với bot, phân cách bởi dấu phẩy (bắt buộc, ví dụ `123456789012345678,987654321098765432`). Thành viên có quyền Administrator trên server sẽ luôn được cấp phép mà không cần role này.
- `DISCORD_LOCALIZE_NSW_CHANNEL_ID`: ID của kênh Forum trên server Discord dùng để tạo bài viết (post/thread) thảo luận cho dự án (bắt buộc, ví dụ `1568872535125393458`).
- `PROJECTS_ROOT`: Thư mục gốc chứa các dự án (không bắt buộc, mặc định là `./projects`).

### Tương tác trong Forum Post

- Khi Administrator hoặc thành viên có role được cấp quyền trong `DISCORD_CREATE_ROLE_IDS` tag/mention bot (@Bot) bên trong bất kỳ bài viết/thread nào thuộc kênh Forum đã cấu hình, bot sẽ phản hồi lại lời chào (`hi`) kèm trích dẫn tag người gửi.
- Các mention từ người không có quyền hoặc ngoài kênh Forum sẽ được giữ im lặng.

### Chạy Bot

Khởi động bot bằng lệnh:

```sh
uv run nsl-bot
```

Hoặc:

```sh
uv run python -m nsw_localize.bot
```

Khi chạy thiếu biến môi trường cần thiết, lệnh sẽ báo lỗi cấu hình và dừng lại để đảm bảo an toàn.
