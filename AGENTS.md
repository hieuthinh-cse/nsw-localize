Dưới đây là quy trình Việt hoá game Nintendo Switch từ file NSP (dành cho máy đã hack/CFW và game bạn sở hữu hợp pháp).

## Tổng quan

Game Switch lưu text trong các file được đóng gói (NCA → RomFS/ExeFS). Quy trình chung: **giải nén → tìm file text → dịch → đóng gói lại → chạy bằng LayeredFS (không cần đóng gói lại NSP)**.

## Bước 1: Chuẩn bị

- **prod.keys** và **title.keys** (đặt tại `~/.switch/` để CLI tự động nhận diện khóa giải mã).
- **CLI nội bộ `nsl`** (chạy qua `uv run nsl` hoặc `.venv/bin/nsl`). CLI tự động nhận diện binary phù hợp theo hệ điều hành (`nstool.exe` trên Windows, `nstool` trên macOS/POSIX).
- **LƯU Ý QUAN TRỌNG:** Tuyệt đối không gọi trực tiếp binary `nstool` hay `nstool.exe`. Mọi thao tác trích xuất và giải mã bắt buộc phải thực hiện thông qua CLI `nsl`.
- Font hỗ trợ tiếng Việt (có dấu), vd: Noto Sans.

## Bước 2: Giải nén NSP và NCA (Bắt buộc dùng CLI `nsl`)

Dự án đã xây dựng sẵn CLI `nsl` (wrapper chuẩn hóa quanh engine giải mã) để trích xuất nội dung:

1. **Giải nén NSP ra các file NCA:**
   ```sh
   uv run nsl unpack nsp "path/to/game.nsp" --output extracted/nsp_out
   ```
   Lệnh sẽ trích xuất container PFS0 và liệt kê danh sách các file `.nca` (Program, Control, Manual, Metadata) cùng file ticket (`.tik`).

2. **Giải mã và trích xuất RomFS / ExeFS từ NCA:**
   - Trích xuất phân vùng RomFS (`/1`):
     ```sh
     uv run nsl unpack nca extracted/nsp_out/<program>.nca \
       --keyset "path/to/prod.keys" \
       --virtual-path /1 \
       --output extracted/romfs
     ```
   - Trích xuất phân vùng ExeFS (`/0`):
     ```sh
     uv run nsl unpack nca extracted/nsp_out/<program>.nca \
       --keyset "path/to/prod.keys" \
       --virtual-path /0 \
       --output extracted/exefs
     ```
   - Hợp nhất Base Program NCA và Update Program NCA để lấy RomFS hoàn chỉnh (`merge-nca`):
     ```sh
     uv run nsl merge-nca \
       --base extracted/base/<program>.nca \
       --patch extracted/update/<program>.nca \
       --output extracted/merged_romfs
     ```
     *(Tự động sử dụng `~/.switch/prod.keys` nếu không truyền `--keyset`, có thể thêm `--tik` nếu có file ticket)*.
   - *Lưu ý về Title Key (eShop):* Đảm bảo file `title.keys` đã có trong `~/.switch/` để CLI tự động áp dụng khóa giải mã cho Program NCA. Không gọi lệnh công cụ bên ngoài trực tiếp.

## Bước 3: Tìm file text

Mở thư mục `romfs` và tìm các định dạng thường gặp:

| Engine/Định dạng | Gợi ý công cụ |
|---|---|
| Unity (`.assets`, `.bundle`) | UABEA, AssetStudio |
| Unreal (`.pak`) | UnrealPak, UAssetGUI |
| `.msbt/.msbp` (game Nintendo) | Kuriimu2, MSBT Editor |
| `.csv/.json/.xml/.txt` | Notepad++ |
| `.bin/.dat` tự chế | HxD, tool riêng của cộng đồng |

## Bước 4: Dịch và xử lý font

- Trích text ra bảng (Excel/CSV), giữ nguyên **mã điều khiển** (`%s`, `{0}`, `\n`, tag màu…).
- Dịch và kiểm tra độ dài: tiếng Việt thường dài hơn tiếng Anh, có thể tràn khung.
- **Font**: nhiều game không có glyph tiếng Việt. Cần thay/chèn font (file `.bfttf`, `.ttf`, font atlas) hoặc dùng bảng map ký tự. Đây thường là phần khó nhất.
- Mã hoá UTF-8/UTF-16 đúng với game.

## Bước 5: Đóng gói và cài (LayeredFS)

Cách đơn giản nhất, không cần dựng lại NSP:

1. Đặt file đã sửa theo đúng cấu trúc:
   ```
   sdmc:/atmosphere/contents/<TitleID>/romfs/<đường dẫn file giống bản gốc>
   ```
2. Với file nằm ở exefs thì dùng `exefs/` (cần patch IPS/PCHTXT riêng).
3. Chép vào thẻ SD, khởi động Atmosphere và chạy game.

`TitleID` là chuỗi 16 ký tự hex của game (xem trong tên NSP hoặc DBI/Checkpoint).

## Bước 6: Kiểm tra và sửa lỗi

- Game crash: thường do file sai kích thước/định dạng hoặc thiếu mã điều khiển.
- Lỗi hiển thị chữ: kiểm tra font và mã hoá.
- Chơi thử toàn bộ, ghi lại chỗ tràn chữ để chỉnh.