Dưới đây là quy trình Việt hoá game Nintendo Switch từ file NSP (dành cho máy đã hack/CFW và game bạn sở hữu hợp pháp).

## Tổng quan

Game Switch lưu text trong các file được đóng gói (NCA → RomFS/ExeFS). Quy trình chung: **giải nén → tìm file text → dịch → đóng gói lại → chạy bằng LayeredFS (không cần đóng gói lại NSP)**.

## Bước 1: Chuẩn bị

- **prod.keys** và **title.keys** (dump từ chính máy Switch của bạn bằng Lockpick_RCM).
- **Hactool** hoặc **hactoolnet**: giải mã NCA.
- **NSC_Builder** hoặc **nsZip/NSP Tool**: trích xuất NSP.
- **Hactool/SwitchToolbox**, **Atmosphere CFW** trên máy.
- Công cụ tuỳ game: **Notepad++/VS Code**, **HxD**, **Kuriimu2**, **Unity AssetStudio / UABEA** (game Unity), **Switch Toolbox**.
- Font hỗ trợ tiếng Việt (có dấu), vd: Noto Sans.

## Bước 2: Giải nén NSP

1. Dùng NSC_Builder hoặc `hactoolnet` để giải NSP ra các file NCA.
2. Xác định NCA loại **Program** (chứa exefs + romfs):
   ```
   hactoolnet -t pfs0 game.nsp --outdir=nsp_out
   hactoolnet -t nca --romfsdir=romfs --exefsdir=exefs ten_file.nca
   ```
3. Nếu game có **Update/DLC**, giải nén cả hai. Bản update ghi đè nội dung bản gốc, nên text thường nằm ở bản update mới nhất.

## Bước 3: Tìm file text

Mở thư mục `romfs` và tìm các định dạng thường gặp:

| Engine/Định dạng | Gợi ý công cụ |
|---|---|
| Unity (`.assets`, `.bundle`) | UABEA, AssetStudio |
| Unreal (`.pak`) | UnrealPak, UAssetGUI |
| `.msbt/.msbp` (game Nintendo) | Kuriimu2, MSBT Editor |
| `.csv/.json/.xml/.txt` | Notepad++ |
| `.bin/.dat` tự chế | HxD, tool riêng của cộng đồng |

Tìm trên **GitHub/GBAtemp/Romhacking.net** xem game đó đã có tool hoặc dự án Việt hoá/ngôn ngữ khác chưa, vì nhiều game có sẵn tool trích/nhập text.

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