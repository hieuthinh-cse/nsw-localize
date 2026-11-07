# nsw-localize

CLI Python dùng [`nstool`](https://github.com/jakcron/nstool) để trích xuất nội dung NSP và NCA phục vụ quy trình Việt hoá game Nintendo Switch.

Chỉ sử dụng với game, firmware và keyset bạn tự dump từ thiết bị của mình và sở hữu hợp pháp. Công cụ này không kèm key, game, hay cơ chế vượt qua bảo vệ bản quyền.

## Yêu cầu

- [uv](https://docs.astral.sh/uv/) và Python 3.9 trở lên.
- Một file `nstool` tương thích với hệ điều hành. Mặc định CLI tìm `./nstool` tại thư mục đang chạy; dùng `--nstool PATH` để chọn binary khác.
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
