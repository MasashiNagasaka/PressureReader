import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, PngImagePlugin
import cv2
import numpy as np
import os
from tkinter import filedialog
import csv
from pdf2image import convert_from_path
from datetime import datetime
import base64
from io import BytesIO
import sys
import atexit
import shutil
import uuid
import subprocess
from scipy.interpolate import interp1d
import math
import pyautogui
from openpyxl import Workbook                  #26/04/16追加
from openpyxl.utils import get_column_letter   #26/04/16追加
from openpyxl.formatting.rule import ColorScaleRule



version = "3.5.0"

image = None
canvas = None
photo = None
image_with_metadata = None
photo = None
image_path = None
image_id = None
image_meta = None
cv_image = None
cv_image_2 = None
start_x, start_y, end_x, end_y = 0, 0, 0, 0
scale = 0.0
image_org_w, image_org_h = 0, 0
canvas_width, canvas_height = 0, 0
processed_image = None

press_Max = 0.0
press_Min = 0.0
bri_Max = 0.0
bri_Min = 0.0

white_Value = 250
white_Value2 = 5
white_Press = 0
white_flag = False
x01, x02, x03, x04, x06, x07, x08, x09, x10, x11, x13, x15 = [0.0] * 12

oval_size = 10 # 選択範囲の点の大きさ
oval_width = 2 # 選択範囲の点の枠線太さ
mm2fontsize = 12

moving_point = None
dragging = False
reset_confirm_open = False
image_switch_confirm_open = False
suppress_sheet_type_reset = False
contact_info_window = None

# 多角形選択モード用
polygon_points = []
point_ids = []
polygon_id = None
first_polygon_point = None

top_circle_px = None
top_circle_py = None
any_dir = None
source_image_path = None
px_count = 0

# PDF⇒PNG変換品質(デフォルト：1200/300)
p2p_size = 1200
p2p_dpi = 300

#　画面の解像度を取得
screen_width, screen_height = pyautogui.size()

# 実行ファイル化された場合の処理
if getattr(sys, 'frozen', False):  # 実行ファイル化された場合
    # exeファイルがあるディレクトリ（書き込み用）
    PR_dir = os.path.dirname(sys.executable)
    # onefile展開先（同梱リソース参照用）
    RESOURCE_dir = getattr(sys, "_MEIPASS", PR_dir)
else:
    # スクリプトが実行されているディレクトリ
    PR_dir = os.path.dirname(__file__)
    RESOURCE_dir = PR_dir

# onefile実行時のTk参照先を明示（PyInstaller環境差異対策）
if getattr(sys, 'frozen', False):
    tcl_root = os.path.join(RESOURCE_dir, "tcl")
    os.environ.setdefault("TCL_LIBRARY", os.path.join(tcl_root, "tcl8.6"))
    os.environ.setdefault("TK_LIBRARY", os.path.join(tcl_root, "tk8.6"))
ima_path = os.path.join(RESOURCE_dir, "pr_images")
tmp_dir = os.path.join(PR_dir, "_pressure_tmp")
sheet_setting_path = os.path.join(RESOURCE_dir, "config", "sheet_setting.csv")
sheet_setting_config = {}
sheet_setting_load_error = None
sheet_setting_error_shown = False


def is_path_in_dir(path, base_dir):
    abs_path = os.path.abspath(path)
    abs_base_dir = os.path.abspath(base_dir)
    try:
        return os.path.commonpath([abs_path, abs_base_dir]) == abs_base_dir
    except ValueError:
        return False


def cleanup_temp_pngs():
    os.makedirs(tmp_dir, exist_ok=True)
    for entry in os.scandir(tmp_dir):
        if not entry.is_file():
            continue
        if not entry.name.lower().endswith(".png"):
            continue
        file_path = os.path.abspath(entry.path)
        if not is_path_in_dir(file_path, tmp_dir):
            print(f"[WARN] Skip cleanup outside tmp dir: {file_path}")
            continue
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"[WARN] Failed to remove temp PNG: {file_path} ({e})")
    try:
        expected_tmp_dir = os.path.abspath(os.path.join(PR_dir, "_pressure_tmp"))
        if os.path.abspath(tmp_dir) == expected_tmp_dir and os.path.isdir(tmp_dir) and not os.listdir(tmp_dir):
            os.rmdir(tmp_dir)
    except OSError as e:
        print(f"[WARN] Failed to remove tmp dir: {tmp_dir} ({e})")


def schedule_cleanup_tmp_dir_after_exit():
    if not getattr(sys, 'frozen', False):
        return
    tmp_abs = os.path.abspath(tmp_dir)
    expected_tmp_dir = os.path.abspath(os.path.join(PR_dir, "_pressure_tmp"))
    if tmp_abs != expected_tmp_dir:
        return
    # Bootloader側の後片付け完了後に、空フォルダだけ削除する
    cmd = f'ping 127.0.0.1 -n 3 > nul & rmdir "{tmp_abs}" 2>nul'
    try:
        subprocess.Popen(
            ["cmd", "/c", cmd],
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except OSError as e:
        print(f"[WARN] Failed to schedule tmp dir cleanup: {tmp_abs} ({e})")


def _parse_bool_text(value_text):
    text = str(value_text).strip().lower()
    if text in ("true", "1"):
        return True
    if text in ("false", "0"):
        return False
    raise ValueError(f"Invalid boolean text: {value_text}")


def _parse_float_list(tokens):
    values = []
    for token in tokens:
        token_text = str(token).strip()
        if token_text == "":
            continue
        values.append(float(token_text))
    return values


def load_sheet_setting_config():
    config = {}
    current_sheet = None
    current_region = None

    if not os.path.isfile(sheet_setting_path):
        raise FileNotFoundError(f"sheet setting csv not found: {sheet_setting_path}")

    rows = None
    decode_error = None
    for encoding in ("utf-8-sig", "cp932"):
        try:
            with open(sheet_setting_path, "r", encoding=encoding, newline="") as f:
                rows = list(csv.reader(f))
            break
        except UnicodeDecodeError as e:
            decode_error = e

    if rows is None:
        raise decode_error if decode_error is not None else RuntimeError("failed to read sheet setting csv")

    for row_no, row in enumerate(rows, start=1):
        if not row:
            continue

        row = [cell.strip() for cell in row]
        kind = row[0]
        if kind == "":
            continue

        if kind == "sheet":
            if len(row) < 2 or row[1] == "":
                raise ValueError(f"row {row_no}: sheet type is empty")
            current_sheet = row[1]
            current_region = None
            config[current_sheet] = {
                "press_max": None,
                "press_min": None,
                "temp_humidity_enabled": None,
                "brightness": [],
                "lines": [],
                "regions": [],
                "charts": {},
            }
            continue

        if current_sheet is None:
            raise ValueError(f"row {row_no}: data row before sheet row")

        item = config[current_sheet]

        if kind == "condition":
            if len(row) < 4:
                raise ValueError(f"row {row_no}: condition requires 3 values")
            item["press_max"] = float(row[1])
            item["press_min"] = float(row[2])
            item["temp_humidity_enabled"] = _parse_bool_text(row[3])
        elif kind == "brightness":
            if len(row) < 3:
                raise ValueError(f"row {row_no}: brightness requires seq/value")
            item["brightness"].append((int(row[1]), float(row[2])))
        elif kind == "line":
            if len(row) < 4:
                raise ValueError(f"row {row_no}: line requires seq/m/b")
            item["lines"].append((int(row[1]), float(row[2]), float(row[3])))
        elif kind == "region":
            if len(row) < 2 or row[1] == "":
                raise ValueError(f"row {row_no}: region name is empty")
            current_region = row[1]
            item["regions"].append(current_region)
            item["charts"][current_region] = [[], []]
        elif kind == "Standard_Chart_x":
            values = _parse_float_list(row[1:])
            if item["temp_humidity_enabled"] is False:
                chart = item["charts"].setdefault("_DEFAULT_", [[], []])
                chart[0] = values
            else:
                if current_region is None:
                    raise ValueError(f"row {row_no}: Standard_Chart_x before region")
                item["charts"][current_region][0] = values
        elif kind == "Standard_Chart_y":
            values = _parse_float_list(row[1:])
            if item["temp_humidity_enabled"] is False:
                chart = item["charts"].setdefault("_DEFAULT_", [[], []])
                chart[1] = values
            else:
                if current_region is None:
                    raise ValueError(f"row {row_no}: Standard_Chart_y before region")
                item["charts"][current_region][1] = values
        else:
            raise ValueError(f"row {row_no}: unknown record type {kind}")

    # Validate and normalize
    for sheet_type, item in config.items():
        if item["press_max"] is None or item["press_min"] is None:
            raise ValueError(f"{sheet_type}: condition is missing")
        if item["temp_humidity_enabled"] is None:
            raise ValueError(f"{sheet_type}: temp_humidity_enabled is missing")
        if len(item["brightness"]) == 0:
            raise ValueError(f"{sheet_type}: brightness is missing")

        item["brightness"].sort(key=lambda t: t[0])
        brightness_indices = [idx for idx, _ in item["brightness"]]
        if brightness_indices != list(range(len(item["brightness"]))):
            raise ValueError(f"{sheet_type}: brightness seq is not contiguous")
        item["brightness"] = [val for _, val in item["brightness"]]

        item["lines"].sort(key=lambda t: t[0])
        line_indices = [idx for idx, _, _ in item["lines"]]
        if len(line_indices) > 0 and line_indices != list(range(len(line_indices))):
            raise ValueError(f"{sheet_type}: line seq is not contiguous")
        item["lines"] = [(m, b) for _, m, b in item["lines"]]

        if item["temp_humidity_enabled"]:
            if len(item["regions"]) == 0:
                raise ValueError(f"{sheet_type}: regions are missing")
            if len(item["lines"]) + 1 != len(item["regions"]):
                raise ValueError(f"{sheet_type}: line/region count mismatch")
            for region_name in item["regions"]:
                if region_name not in item["charts"]:
                    raise ValueError(f"{sheet_type}: chart for region {region_name} is missing")
                xs, ys = item["charts"][region_name]
                if len(xs) == 0 or len(ys) == 0:
                    raise ValueError(f"{sheet_type}: chart values for region {region_name} are empty")
                if len(xs) != len(ys):
                    raise ValueError(f"{sheet_type}: chart x/y count mismatch for region {region_name}")
                item["charts"][region_name] = (np.array(xs), np.array(ys))
        else:
            if "_DEFAULT_" not in item["charts"]:
                raise ValueError(f"{sheet_type}: default chart is missing")
            xs, ys = item["charts"]["_DEFAULT_"]
            if len(xs) == 0 or len(ys) == 0:
                raise ValueError(f"{sheet_type}: default chart values are empty")
            if len(xs) != len(ys):
                raise ValueError(f"{sheet_type}: default chart x/y count mismatch")
            item["charts"]["_DEFAULT_"] = (np.array(xs), np.array(ys))

    return config


cleanup_temp_pngs()
atexit.register(cleanup_temp_pngs)
try:
    sheet_setting_config = load_sheet_setting_config()
except Exception as e:
    sheet_setting_load_error = str(e)
    print(f"[WARN] failed to load sheet setting csv: {e}")



# スプラッシュ表示●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●

# Tkinterウィンドウを作成
root = tk.Tk()
root.title("画像表示")
root.configure(bg="white")
root.overrideredirect(True)

image_path = os.path.join(ima_path, "PR_splash.png")

# 画面の高さでリサイズ係数を調整
new_width = int(600 * (screen_height / 1080))
new_height = int(278 * (screen_height / 1080))
# Canvasの作成
canvas = tk.Canvas(root, width=new_width, height=new_height, highlightthickness=0)
canvas.pack()

# 画像を読み込んで表示する関数
def show_image_with_text():
    image = Image.open(image_path)
    image = image.resize((new_width, new_height), Image.LANCZOS)
    tk_image = ImageTk.PhotoImage(image)

    # 画像をキャンバスに表示
    canvas.create_image(0, 0, anchor="nw", image=tk_image)
    canvas.image = tk_image  # 参照保持

    # テキストを画像上に重ねて表示
    canvas.create_text(
        new_width - 50,             # X位置（中央）
        new_height - 20,            # Y位置（下寄り）
        text=f"v{version}",  # 表示する文字列
        font=("Arial", 20, "bold"), # フォント指定
        fill="#404040"                # 文字色（例: 白）
    )

# 画像と文字を表示
show_image_with_text()

# ウィンドウを画面中央に配置
x = (screen_width - new_width) // 2
y = (screen_height - new_height) // 2
root.geometry(f"{new_width}x{new_height}+{x}+{y}")

# 一定時間後にウィンドウを閉じる
root.after(2000, root.destroy)

# メインループ開始
root.mainloop()

# スプラッシュ表示●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●


# スプラッシュ2（案内ウィンドウ） *****************************************************************************************
def show_startup_info_window():
    info_root = tk.Tk()
    info_root.title("事前準備")
    info_root.configure(bg="#f4f7fb")
    info_root.resizable(False, False)

    window_width = int(900 * (screen_height / 1080))
    window_height = int(300 * (screen_height / 1080))
    info_root.geometry(
        f"{window_width}x{window_height}+{(screen_width - window_width) // 2}+{(screen_height - window_height) // 2}"
    )

    header_frame = tk.Frame(info_root, bg="#1f3a5f", height=56)
    header_frame.pack(fill=tk.X, side=tk.TOP)
    header_frame.pack_propagate(False)

    header_label = tk.Label(
        header_frame,
        text="事前準備",
        bg="#1f3a5f",
        fg="#ffffff",
        font=("Meiryo ui", 16, "bold"),
        padx=16,
    )
    header_label.pack(anchor="w", pady=(12, 0))

    body_frame = tk.Frame(info_root, bg="#f4f7fb")
    body_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

    intro_label = tk.Label(
        body_frame,
        text="本アプリ使用時は、事前に下記を準備して下さい。",
        justify=tk.LEFT,
        anchor="w",
        bg="#f4f7fb",
        fg="#1f2d3d",
        font=("Meiryo ui", 14),
    )
    intro_label.pack(anchor="w", pady=(0, 10))

    body_color = "#1f2d3d"
    highlight_color = "#c942a5"

    def add_segmented_labels(container, segments):
        for text, is_highlight in segments:
            tk.Label(
                container,
                text=text,
                justify=tk.LEFT,
                anchor="w",
                bg="#f4f7fb",
                fg=highlight_color if is_highlight else body_color,
                font=("Meiryo ui", 14, "bold") if is_highlight else ("Meiryo ui", 14),
            ).pack(side=tk.LEFT)

    table_frame = tk.Frame(body_frame, bg="#f4f7fb")
    table_frame.pack(anchor="w", fill=tk.X)
    table_frame.grid_columnconfigure(1, minsize=250)
    table_frame.grid_columnconfigure(3, weight=1)

    def add_aligned_item(row_index, left_segments, right_segments):
        bullet_label = tk.Label(
            table_frame,
            text="・",
            justify=tk.LEFT,
            anchor="w",
            bg="#f4f7fb",
            fg=body_color,
            font=("Meiryo ui", 14),
        )
        bullet_label.grid(row=row_index, column=0, sticky="nw", pady=(0, 6))

        left_container = tk.Frame(table_frame, bg="#f4f7fb")
        left_container.grid(row=row_index, column=1, sticky="nw", pady=(0, 6))
        add_segmented_labels(left_container, left_segments)

        sep_label = tk.Label(
            table_frame,
            text="…",
            justify=tk.LEFT,
            anchor="w",
            bg="#f4f7fb",
            fg=body_color,
            font=("Meiryo ui", 14),
            padx=2,
        )
        sep_label.grid(row=row_index, column=2, sticky="nw", pady=(0, 6))

        right_container = tk.Frame(table_frame, bg="#f4f7fb")
        right_container.grid(row=row_index, column=3, sticky="nw", pady=(0, 6))
        add_segmented_labels(right_container, right_segments)

    add_aligned_item(
        0,
        [("画像PDF", True)],
        [("感圧紙", True), ("  および  ", False), ("標準色見本", True)],
    )
    add_aligned_item(
        1,
        [("温度[℃]", True), ("、", False), ("湿度[%]", True)],
        [("圧力計測時の値", True)],
    )
    add_aligned_item(
        2,
        [("スケール", True)],
        [("感圧紙の", False), ("寸法[mm]", True)],
    )

    info_root.after(8000, info_root.destroy)
    info_root.mainloop()


show_startup_info_window()



def update_canvas_image():
    """Canvasのサイズに合わせてリサイズして表示"""
    global image_with_metadata, photo, image_id, scale

    if image_with_metadata is None:
        return

    if apply_threshold_flag.get():
        apply_threshold()
    else:
        # チェックが外れていたら元の画像を表示
        global processed_image
        processed_image = image_with_metadata.copy()

    # Canvasの現在のサイズを取得（ボタンエリアを除外）
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()

    if canvas_width == 1 or canvas_height == 1:
        return  # 初回起動時はサイズが未確定なので無視

    # 画像のアスペクト比を維持してリサイズ
    img_width, img_height = processed_image.size
    scale = min(canvas_width / img_width, canvas_height / img_height)
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    resized_image = processed_image.resize((new_width, new_height), Image.LANCZOS)

    # 画像をTkinter用に変換
    photo = ImageTk.PhotoImage(resized_image)

    # 画像をCanvasに描画（中央に配置）
    canvas.delete("image", "rect", "text", "line", "point_pressure")
    x_offset = (canvas_width - new_width) // 2
    y_offset = (canvas_height - new_height) // 2
    canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=photo, tags="image")




def c2p(brightness):
    global brightness_entry_15, brightness_entry_13, brightness_entry_11, brightness_entry_10, brightness_entry_09, brightness_entry_08, brightness_entry_07, \
    brightness_entry_06, brightness_entry_05, brightness_entry_04, brightness_entry_03, brightness_entry_02, brightness_entry_01, \
    press_Max, press_Min, bri_Max, bri_Min, white_flag, white_Press, white_Value2, sheet_setting_error_shown, sheet_setting_load_error

    def calculate_brightness(press_value, forward_interp, before_values, after_values):
        result_recal = forward_interp(press_value)

        if result_recal > after_values[0]:
            y0, y1 = after_values[0], after_values[1]
            x0, x1 = before_values[0], before_values[1]
        elif result_recal < after_values[-1]:
            y0, y1 = after_values[-2], after_values[-1]
            x0, x1 = before_values[-2], before_values[-1]
        else:
            index = np.searchsorted(after_values[::-1], result_recal, side='left')
            index = len(after_values) - 1 - index
            y0, y1 = after_values[index], after_values[index + 1]
            x0, x1 = before_values[index], before_values[index + 1]
        return x0 + (result_recal - y0) * ((x1 - x0) / (y1 - y0))

    def warn_sheet_setting_once(message):
        global sheet_setting_error_shown
        if sheet_setting_error_shown:
            return
        sheet_setting_error_shown = True
        messagebox.showwarning("設定読み込み警告", message)

    class BrightnessInputError(ValueError):
        pass

    sheet_type = selected_var.get()

    if sheet_type not in sheet_setting_config:
        if sheet_setting_load_error:
            warn_message = (
                "sheet_setting.csv の読み込みに失敗しているため、圧力変換を実行できません。\n"
                f"{sheet_setting_load_error}"
            )
        else:
            warn_message = (
                "sheet_setting.csv に選択中の感圧紙設定がないため、圧力変換を実行できません。\n"
                f"sheet_type: {sheet_type}"
            )
        warn_sheet_setting_once(warn_message)
        print(f"[WARN] csv config required: {warn_message}")
        return -9999

    try:
        item = sheet_setting_config[sheet_type]
        entry_by_key = {
            "15": brightness_entry_15,
            "13": brightness_entry_13,
            "11": brightness_entry_11,
            "10": brightness_entry_10,
            "09": brightness_entry_09,
            "08": brightness_entry_08,
            "07": brightness_entry_07,
            "06": brightness_entry_06,
            "05": brightness_entry_05,
            "04": brightness_entry_04,
            "03": brightness_entry_03,
            "02": brightness_entry_02,
            "01": brightness_entry_01,
        }

        after_values = list(item["brightness"])
        if len(after_values) < 2:
            raise ValueError(f"{sheet_type}: brightness count is less than 2")

        active_keys = get_active_brightness_keys(sheet_type)
        if len(active_keys) != len(after_values):
            raise ValueError(
                f"{sheet_type}: brightness count mismatch (csv={len(after_values)}, active={len(active_keys)})"
            )

        before_values = []
        for key in active_keys:
            entry = entry_by_key.get(key)
            if entry is None:
                raise ValueError(f"{sheet_type}: brightness key {key} is unsupported")
            value_text = entry.get().strip()
            if value_text == "":
                raise BrightnessInputError(f"{sheet_type}: brightness {key} is empty")
            before_values.append(float(value_text))

        if brightness < before_values[0]:
            x0, x1 = before_values[0], before_values[1]
            y0, y1 = after_values[0], after_values[1]
            result = y0 + (y1 - y0) * ((brightness - x0) / (x1 - x0))
        elif brightness > before_values[-1]:
            x0, x1 = before_values[-2], before_values[-1]
            y0, y1 = after_values[-2], after_values[-1]
            result = y0 + (y1 - y0) * ((brightness - x0) / (x1 - x0))
        else:
            index = np.searchsorted(before_values, brightness, side='right') - 1
            if index >= len(before_values) - 1:
                index = len(before_values) - 2
            x0, x1 = before_values[index], before_values[index + 1]
            y0, y1 = after_values[index], after_values[index + 1]
            result = y0 + (y1 - y0) * ((brightness - x0) / (x1 - x0))

        if item["temp_humidity_enabled"]:
            ondo_text = ondo_entry.get().strip()
            shitsudo_text = shitsudo_entry.get().strip()
            if ondo_text == "" or shitsudo_text == "":
                return -9999
            x, y = float(ondo_text), float(shitsudo_text)
            lines = item["lines"]
            regions = item["regions"]
            for i, (m, b) in enumerate(lines):
                y_line = m * x + b
                if y > y_line:
                    region = regions[i]
                    break
            else:
                region = regions[-1]
            Standard_Chart_x, Standard_Chart_y = item["charts"][region]
        else:
            Standard_Chart_x, Standard_Chart_y = item["charts"]["_DEFAULT_"]

        inverse_interp = interp1d(Standard_Chart_y, Standard_Chart_x, kind='linear', bounds_error=False, fill_value="extrapolate")
        Press_value = inverse_interp(result)

        press_Max = float(item["press_max"])
        press_Min = float(item["press_min"])
        forward_interp = interp1d(Standard_Chart_x, Standard_Chart_y, kind='linear', bounds_error=False, fill_value="extrapolate")
        bri_Max = calculate_brightness(press_Max, forward_interp, before_values, after_values)
        bri_Min = calculate_brightness(press_Min, forward_interp, before_values, after_values)

        if Press_value > press_Max:
            return press_Max + 0.1
        elif Press_value <= press_Max and Press_value >= press_Min:
            return Press_value
        elif Press_value < press_Min:
            if white_flag == True:
                white_flag = False
                return Press_value
            elif Press_value > white_Press:
                return press_Min - 0.1
            else:
                return -9999
    except BrightnessInputError as e:
        # 入力不足は読取失敗として扱い、CSV設定エラー警告は表示しない
        print(f"[WARN] brightness input required: {e}")
        return -9999
    except Exception as e:
        warn_message = f"sheet_setting.csv の設定利用に失敗したため、圧力変換を実行できません。\n{e}"
        warn_sheet_setting_once(warn_message)
        print(f"[WARN] csv config required: {e}")
        return -9999
# 警告メッセージ******************************************************************************************************************
def no_image(canvas, root):
    items = canvas.find_withtag("image")
    if not items:
        comment_label = tk.Label(root, text=" 『PDF⇒PNG変換』ボタン、もしくは『PNGを開く』ボタンを押してください ",
                                 fg="white", bg="#c942a5", font=("Meiryo ui", 16, "bold"))
        comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        root.after(2000, comment_label.destroy)
        return True
    return False

def no_rect(canvas, root):
    items = canvas.find_withtag("rect")
    if not items:
        comment_label = tk.Label(root, text=" 選択範囲を作成してください ",
                                 fg="white", bg="#c942a5", font=("Meiryo ui", 16, "bold"))
        comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        root.after(2000, comment_label.destroy)
        return True
    return False

def no_selection_for_export(canvas, root):
    global mode, polygon_points, polygon_id, circle_id, radius_x, radius_y
    if mode == "rect":
        return no_rect(canvas, root)
    if mode == "polygon":
        if not polygon_points or polygon_id is None or len(polygon_points) < 3:
            comment_label = tk.Label(root, text=" 選択範囲を作成してください ",
                                     fg="white", bg="#c942a5", font=("Meiryo ui", 16, "bold"))
            comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            root.after(2000, comment_label.destroy)
            return True
        return False
    if mode == "circle":
        if circle_id is None or radius_x <= 0 or radius_y <= 0:
            comment_label = tk.Label(root, text=" 選択範囲を作成してください ",
                                     fg="white", bg="#c942a5", font=("Meiryo ui", 16, "bold"))
            comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            root.after(2000, comment_label.destroy)
            return True
        return False
    return no_rect(canvas, root)

def completed_p2p():
    comment_label = tk.Label(root, text=" 変換が完了しました ",
                             fg="white", bg="#c942a5", font=("Meiryo ui", 16, "bold"))
    comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    root.after(1000, comment_label.destroy)


# *******************************************************************************************************************************

        
root = tk.Tk()
root.state('zoomed')  # Windowsで最大化

encoded_string = "iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAcW3pUWHRSYXcgcHJvZmlsZSB0eXBlIGV4aWYAAHjarZtplhy7cqT/YxW9BMzDcjCe0zvQ8vszRGSySOpKT6/FIquyMiIRgA9m5g7Q7P/4v8f8H/4Un6yJqdTccrb8iS0233lR7fNn3O/Oxvv9/gn+veZ+f998L3jeCrrz+bV93t+8z2v3/t7eh7jP/Z+BPi9c51X6daH39/3x+/vjHdDXPwd6ZxDc82S73g/071KeGcXn9/nOKLdaflvamu+T4/tW/fUvhuJzyq5EvkdvS8mN19XbWLDn0kTP9O0OlB6Dft/4/P651TMnv4MLlu8h5GeWQf9S6PyM93sx3OhC5hcfyv3eruEtrmQKzLS9D+r2a8yftvllo3/4868sy/KQs3XzD699f/4RN99X7h/ef8Pg67Wa3wvhd7fa/P35n77v0megz4XwfY7/+eQ6v0/+7f15jfXrj/np7nNWPXfRrKLHjC3yu6jPUu4r7huy4v1U5qvYbIjaygt9Nb6q7XYSU4tHDr6ma87j++OiW6674/b9Od1kitFvX/jp/TQ+3DcrTmp+BgVD1Jc7voQWVqiExLwxFIP/zsXdx7b7uOmqXcYux63eMZjjI//2l/lXbzxHueScrV9bMS+v7GQW1uF+/eA2POLOa9R0Dfz5+vOP/BrwYLpmriyw22GeIUZyv4IrXEcHbkz8fLLelfUOgIl4dGIyLuABm11ILjOj4n1xDkNWHNSZug/RDzzgUvKLSfpIruIcsoNn85ni7q0++edtUDVEQw5n0rXioY6zYkzET4mVGOoppJhSyqmkmlrqOWRlXs4lC557CSWWVHIppZrSSq+hxppqrqXW2mpvvgXgOzXytNXWWu88tDNy59OdG3offoQRRxp5lFFHM6NPwmfGmWaeZdbZZl9+hUWCr7zKqqutvt0mlHbcaedddt1t90OonXDiSSefYk497fSv1163/vX1P/Cae73mr6d0Y/l6jXdL+QzhBCdJPsNjPjocXvAaHiOw5TNbXYxenpPP4COyInkmmeSc5eQxPBi38+m4r+9ezxms+L/iN1Pq9Zv///Wckev+Rc/97bf/zGurX9gL10NKQxnVhiNKdNglLn1PrYeTmosp1BTu90Q2jNgNAd4wQ/eucneH3JKvfcQ4XOaCf37zEBbjQXMdoJsFhy9YO6RcNapf3lgW3WOsIyZ3B4yJd+J912du7iQo0/H3Fb+7pPczwwLaKfj0fNSkoFTWyxnvD96AFENfd/IldR7P6mMZfqYfi+z+PtPhEC6gj1YIPDy5MIbbtfO6acY1Y+6ZK7emXM7wJwH6cOJxo50zjl+HQffZc64Yjtll4oWzzwrlYDqfc9zE08DbS/YJZ+H7Ws48dU28cnpmxF7KyTkdDa4r5selIVO8gwzZdb33SmI8o6B6npsRUMn1fx7IthVrKRHSx5aDQF/jDtSO14rIyhPvmtwKd8DDkjpLMj/WVNvJzW4MhcTJfdZ7Lze/935u9Xov53W03JaeqZg7l86iwl7erYU7MIwv8YzlVp5727Kyf5eTQ+prenIrOt93UBrBjCk3010JM2F6sic30KPg0YHb8lRYWEJUsaVXCqNe43xikTeyorZ2XJIVkPz0rYIEFod7LAiovPHTZmRFUzEAYw3vxy7L7REY3N5oCrZeFzSjX9+bQJATuKPvPqYPuCTjuD5zOPDI3ok44S8ICwPNfdrzkF3DDCytprFJ20mUzniY2w4VDSAJ32ZGYux1gI65STEs0oVToRBes56IoWskonYz+7rXu+vKtO9E32u6pAu8kzaQVXBjTAzX6yjyVGM0P0DPkGARIqOBRHmFfYodo9bFjCpQXsaCKUHVFPaQbNyx9bRvOHXFad3XPoHA3YY0UaTwmRujPiz9FFqdZu9s+kkj2hoWwdVW3fn0hbm47qoGrcTTCkajfQe7C3yvfC7wdia8osKpdwVhxZaPAcYvA5jHAvUa7fP+D5u1QiATcHXhixAmAF7GBjj8GsR0ixutF+qeJqw87BpIOIYadWai+s7L7RvNm9SxWky6ixnlu5jf12L+YTGul2cB8Gh2bYEtQRc0OmN3JCA3wHpjLQhqe7MS6hEumsDOTm5y2/hpjxFwex4ThikLvidy5vnMI/lRj00Fg1CLnL1Y2wA/rr1CmwTvPklgcjrG4ZmkvGulwDEQcG5ulu2FV4JzYgLGM1WPwZIHgTU3CY38lUGLVjDaFHykGxKkEdAy9rENpqN6DQd3ctU71ktRkxLrco08IGCypjFmt2dB3c4veHr2Pt1e4MQid0CQbHceMHnPozfmSxJPE33ZZ8KQKIMdC57zeSqr5goeq4eEFdbEkiRERnfj97owRYZGgNaAR7HRBo96ShNDzDW1ogQGELJImlLJ9NVH56k5KeTR7TnEA7OSs1BaFUCV1QQC" \
    "podLNh4hIH6PtQq3Ppd7en+W4otAC/gbzwfq9woL9c70Xx+CYnRHY2pcstAJ2Yq7sZu7rAR2oSQQNqWKjYWk2zJVD62aP8XAVwsktEBaivcCJAN9ANbB+QemLEMB4oF1lTQjg2ymAnpdBdA5Yd5IQoavTSxtAmbmomqrE/Ul7lELGkiyCgCvxQM2LGO0VNc2rsPVcbcHexE9Bfjoq4Fam5tmgZiClp1j3eiCikfjwQGF4PIsnLm16MDsE3apc5BZ8lnH6KxhgHQbfC/N+7zRfmsh/ewOg7+lJ9zJrcp0JTIACYz0I8wTmJGpU50MCIu8Y0qrSRjVBa0wdilzAnUVa8Uld0aysVGv5Yh2NWBh2GRlL9IfsS6KkVQgVlQU1WgbzQFSKF9cifqdi3lPgIs8wcSagPMEbTDl4u6uxPAB4cntAS8nVr4Y76BVQ6JGWMBtQnbOtrxPDSFHgJMr1U301MzRIKHI2hHscI70yhstViQAhZaVKrMlPjFBI2ijgwgd6UwutIzoJ8+UXJqKgWUG5S612VgTOM17VccqcTzxCOsTfLAQnA72kNzIWdJnbDTLQQCvCy+4yFjBp884cC9ACB2c8kByoIZnj1V194SfcukXfAJOjWkFdEYvRDnAB3z7kg046oUkyG9KchQJcX9cWMMHxGFUQAHxVxnlk8gCbOfJ2oG23/jdKoXHZkbIcpiwkN+E3+oh7CYglJoczYtZMhIATZIpMnhUSEyA+X4UrF9I3G7Nssz/q2azSBClvQCmeqg/fsjYXPkQ6R+vPgUiSVBZgaDcEqN32uAHqYFUQ0YToQ+rPUkj8mhEQ0ark4Iqb6XaWAhxxI0eTcM9ZiiRVZhgp7Hd82GbJ9Ge1v3NI9I65eomQtKZmnGKQywHMN07YqeoQTwimjfZolCBmBr8ieKJN22gjDxu/CaI7wndiYnTH5mGhvwr0/gdmJwUfqvBukHjZCYFcdfSryHmgGRGvQMjftcEuAyqM4e9gz/UAmhesByHUjROBwdIhkGe1HrMPADUDuqmCCsMcEDQDneRmrgDoQWTTXIWGQ0uIXFRecQ1yoRpqL7G9kC55CHas+2AVL5Cg3oF5B0oUaJjGAkpgK4Azs5RnJI5UwFALDghs++EDipEfJmrSry1CVrwDqaOpCiJR8RWA6PD8VynHpzLdVLVg4uIR+zRKG7vekge3k4etqq4Bll3tZpt2LwgOFwxADBLDSkpeBsStaCnK4kQppVaRypRdJeFz4e0LLjicT/ZFmUn+fOis+GjgFVPFKtMCJnKx7jz5BFzoBa/mSCj2jcXfksFUoRgnJCsOUTDUk15OakoFffJlUh4VFtGxtf63tMvU7kyVLO/n0Re6qf5XvbIH9jevh+Cqh3ZnA+CBNA+kNC5mYx8wsDC7klA9v28nw1RRFHoAm4D8SvwjLeAnaib5oebeEGlhu4K/c3Nl7aqcoeyJphv8lwN9KaPkke5U37mjg072+NuPAONjH49V84dGjoKTnA3Uvmv8iu/+QOZEsfEa0FgAbZQxlGWnK+xCUp31tYIrPu5vOuWqGGFq2W4Fmxk7BI9ZffjLBvB0qxa0xC5OKsQ13AZyGbJKLgJ1kIWRXzYb4pI6GH02VUxtgSqghkJAVaAVAfsMyNKx3aUYGsEhAUSA3BPhB2lTUM9zcoo8PqM81YiYPyt8ToaHPAF6fm2DOEtD82hqq1TiJW5VmJhRzJVvuwwEcp58xLJSLTjwnsfKWYJ1F0haJK2TNW4UfVXKtntxKQt8o1bqFLzU9iwFlUcrAV9k1zZzCzBaIgAza7teJU/H6zfCKfIXntDf2H8MqrS/xDkMONSnYtwI6/DJ7gxgbn3DVg4qJO0mohkqiDm+4DTC+L1yx1k2W89HNLyE+fmt0CfqtbJFmxWCENcjQ+ntDGpfMCODUQvrBFu4ePBZZEMHErhhwRUnXiv/bxyLyDcqzTYwSPuj1gHP5+EuOlgHjqxSKj/hjtubK90c+STIU9+KPeCuflRbRhpWZUy7S5IoUAaIWgnQoFU0McgSvIQVBoduEbjsJDsQOftPEyr3aY+FgkwYvMoXFEzujG3pq7ExEaeYgTp1ahBc0FVMRLjBdIDTKAYOUszqi2UfCGETGsno1YaIiNLU+AhNyj5G/wyUsjUfeQhQEuN3Kgw+qH+2IBucAa2nlUtwx352jydOEDQIOo6sU/tgnki5sXn2RX0UFJoTeayqL+IIDxOEWMCvyGktvKQInEAyaok4VXUENTpG3qJTyPn8GX2kQTImaiWLNuZ/LVFLG7wJ6URscOyEK1N2xXQ1z5rNcpqB29YFdBgTqbKo8xqcZ1RrIrCEGJWBwRJaShVlkenbEI2RLiR2knqMJZd8SSPJ5SyXypvep61DdAso234fJEmoOo8xL2BgsqK2/LF8KE8EIFlof2bV2Hc7qP9TY39SiJCpFc1NP/KokDY3fbl8iSDgtg9NXVrUluDWio3R" \
    "KiqkPq0GTC9atqnGspOqZcBlHQJQwB/KeMHYfxXXILXvKJ+JnFJBtszAK3vDl4PceVo5dR8WQRwcTjJY8JQUAMRFN9eYqgYdWxxrcKxiKTR7M2qtppL/RJLyl4RE5+5nKefRAKft5CjqkA5NW1n+BlboOzXxug4KukJejW+grQRcLphFCiB+odYxQPhkgqppSRsBArqDMXWiFeiT0obiKb0xsLAGdCAuLA4JU2Y2ML2LUjM1qf52ZCKeVS1muYhIGEDFWTIlNLgH0TdpgxIckhrVBKEU5ROnyusSuZRuTKmiwcCoYazU9tFrncTC7729faNtXavAgfSK5ZRGb5SBGcX0e/S3OvxyGiUczkvtX4pfpBVgP9t6rqisko6mixkHPUd7AB1DvnWqD7D3K43pzTIQqPdAB7si45Sbo1pJqpF3TJolioqOulLQHoqX+WwtNSIt9fPEdk4N64riNNilcAbWcE0cwbY0rl6mBKSW1QnruZh5SFtpAqo66+0QdI2ZaxUzdAlBGkzE5AuJEW3ydUylQ2T+T11e9OSG2RAKiYFHqCAKhxcPmg3qjLcMjFpQ+/Wod0O6WMzUbM14yrpFJX19kpcVuhhu0qBQsHkWfcGYMHOsIFvsgisJtyIAkAR71UD7EkwShMIGpJTF1n5T+ru3ZH8WR3k4mJWa/jBgq7zB14yPEiPKl7M3bmA1tE6XV0Rb18wUDkmMz8bG4TgUB9+XnIc9RGUCUEUlUrwGhcLQkEjM7EjcU0tHHTRXw6uT4IHRMm6+xD7CgEBS3eXR+OGR00rd5cuq86eeBWhpKCR8j5/lWAuTAIiiry7Eg7dM/LwFHsHWVMR/xVI6T5rTzniz7kogcUWkFy+DVkwZGhPQ/ZVJ3KPuc/TqTyXmI36QZeX34pOyU7FvnYoiOR9Fdh0iE64oi51/YSUTLZm9ZWx9qxVuxBnqJwl0amgHNFZcww5jAbEEDS3LCI0gB8oNV9k0vKOU6MUWQ+yq3efnMG6RMkYwWm6BVVTqRgIoxO6Pkbhg+HVQIT40J5MDYHBJLzaLxkV50ZLZZmg8ZLa4B1VpYbDLB7zSWRNyg6CC8chq5GzY5HxqYFY1B2ZSpIh4LDj+xwGgEHOMADUhw4g/GE8CjnCYLro1HiM0C0hndqw6KFRio++ardO/YUSIuVVPqa3AbRuqybwZtTZOq/UY0GtXV2GgpVm0G7aImMo2+JgqKjmknogxOeox0SEJp8IDsBcfTiUJUmE8i6pEghgPDFZS1SbBv2tNlW/kI9O3w0YxneAZKfwU9sbJHzoVbtGTf/qH9t31n+3YpDez54g+cBgT2qZfze3/kwt8+/m1q/UevLI/K5Rf+94kC//cnvD/Oxv/NXeeIVAGlZz1byRJxTrgC62HpsK6w6M5kP5V7VkuY4opDCDewYWgGOUmfYMCiIMUXbOc0YJdkIHTl7INYTf3anIxK/2suG8NS6NUHB15N1AkUW0MOG/LGSKdrNThWEEAvdxfmlXscMwVHtYrA7tZTvtULsEyyYJromULUtF/7oVPwnFcNoS2AfV1h5VeP9BgrCWG4hrtw1CIPi1vd4r3oZ6opgt+5nPNa4aI836TBVdqnZlmNsBCPhLOU+FhyAHLgxImBX+xLzVVt9eTo0NlFRksjNrl1UBsOpyjypkrtrNenbsv2Fq6uUEBvq1/3y38KkOkna0SFjFVXK5v2ikMs1h6o6eljGJZC7r1BgeAKVKRXlEiGfP3z8S41ADpaoz388zvjrfvz0hmNl0d5xI2OXqeXNAWrte1xb7dN0pp58nfMYnHPgIvAcOkPlmqxAmX8SFmHkRRV1ndrQNohr/1rq5LVzHbDOO16kq1JF6cQzflS6zTwOOu/r2A/9qafzGRf6/bWnYxbrhKPHOjlRKjLaZ2IU11pufiu4pQVeet8Wpg1oWYt8uVdIlmIpwW9oZ6yWQhl0C00vSqMa+O+c+3ko+xgQyjBOp3pIdTvCvvnSAn3ZOZpLK5AxaOkoSobrilZeD5YuDkqQp4Cz8QEGALwkEdePqQwFqpdjxNhkukqCrUxkCPwn7qfvWeOR+Onorquqr5C8Bj0bWViXh7W6QQzqoI+YbTNuSaxQ8YMA60sn5BLKD/EbBkSrgMwXR6R4Gpv7CKM/WTCjRL6DNYULYwASSijs97q4EGOjmVmsAzUZzwjWoKko7iAMRCRZLwWV//CyUmfE2elCw3G2GGqDhL9MmT9pr66Jq6UB8RnH8ivkniqla2seEhqQ4waJOojatfuRYvBlgVxc2v+MTSe7eSix8b1W6xGZ09zf43we9A/+8+zNw+HNWgDrZ1Zy5pwXUmwcPdMDkcygme+rPl9kgqigpIugFFN1NNJIBVlfY4YnaRUdUmxFiLzoKQp2tXvW+nDTEELNFeC7eHdfUOnBelXg7q6+QtJervX/AH9ZDi6HI52y4G9+lbol6kuyf8uqTVgA78md5FX8G2Y+uQT" \
    "zcdjQsoJOqjuRGcN0tl6njoYgVYpEKAC/xFgtCqyPGIyZZW0OYewKAZ9nLUB0KQq0l4BhbZy5a/O/W9AADk6g8CE2H+FfR8hwK8vjUH1OpArizPYdK4NmpyhWts9BeWducFBDa0GpHTSxuwILUHiloH4NsUVEJ4po1wKopXtapAvVhqL6pWoj6vWZTvxBNA/ESkQOtlr136lI6nQRAiDH7OQlnbUG3yzFxa/MAuS2SxXMiWeqbCOoUn/KVGT27aYG5FVWu8Fh+i6CnDsQpZWGBqHwvZKGv1CaZiBSQjDULyYgKlw5Q6Tqmjs2QdZaEAATj06B4TmlEERbp+VQrVxw9XOWAZeofdYYIEIWnLt+gre2eqErawRbCHwNwXoBfAWWNTM1+w24pWWw2tBUKOIThtDe3odhRdbjFo2lLY+kuw29YsmYzc1VhR96njZ3ulBAt5e22gNWqFRKw1VQJ4GuE9dB+Osvyc+wshB4VXis2oiPS3dBYpBQIL7ldwJE4pWKAJ36sCphUVb3UHKz2dhbCAPyxV8gGTgrElFewBnTrEPMLl4lAsBC7BqeeJqKIRxz/dKlxTBdIuU0B5IgHBrqHn6hWSBiq4q1Cxk8VW9SSVNDHMRf1/CArHYBUN9tWwOvdsia89oIYTEs6X0LpPhm/90XtHInnjGaraJNSIwQ3EoU01QtzqcBuRGtJE/MArzOOkmQwretO5xEZGGijDiGKbJ2j6GBE14kSjEfW6lASbyhYknqJOqvEUH3lPav1RDaPpaAnk4sONVzoV7h5CF3b5E7nICn7oJauV7AWyaozjE7tYytaIn6N44HE+JI/1Il+olP13w1Z/z3AB869TfMG6T7d6xTVLazKV+jo2/1Ozt0bGVjSq92dn8+ncUjP6NQadbaqUSZGIK2JPpGG1CIbhQ+a56HRSr+gzFPGad7riBUFViG6UTwIGrUfahdqJNeoLiQkdNhp7m2YJ2URlR9QCNegJ0NW79I20nfcppvopupADaZ5TiipWUVBmS8Ab+XNMISDuwVIRqpmUIbSZCiH+gCr70bfddx7iMi5i6i93I7bi65oNLjfg0Dl6gc15452/YOOhkj2LUgHmiBSQGq3nkpkCGRRFM+pKKkVsE9bPq48p6LEvveB93FijyTxR/5QtWpDOjwf/fGsH096jlY9D3sfdc+mfR50j1mJOT4H074XvhNA8QAXBvWNXCapAH2kVnX5NpPHBCw32iQ4vlAHOjOgspSSgLoAReCYG7qqU0pRLxeDP9BYRVu8mM9r6fGMZ0d7qPS6U38sci/ct3UoTYdu3XvUq3Qj1QNRwmXUX6Qo2kkHxHU6KOnUCfUJJK2zQcigrWMolNFVR/fJKaHXDNOF7kzRPk+jXFb3pDWdeNF5X200SR5LSo4ExqzhdaBBJ8K4e0SdebC9eWDEhdnxmnaEAgp+CoxiA30WcKCaCeNpOkCfNpHXLT6ETx6swpgUP8r2iaM2SauDEE1VNzOP177U7whEIEEdPAy5CqgxJd+cusbHXmmv3ZKcn2N/z+bBfDZtdKwrP2xmI7pAxwsQWUtBv9W5vK4eOqVBNYSNSWKEsAgR7l/DqFvapJjVRATOEfP2iRg1nP6IGEXYFTZ/xFiDIBuWAix0OE69ksitM+mk/Ib8spQEkAr7kEfqUC2d1qkLE0CkPomtVQ+r7lc7ynehDgkS/kqQ8L79V6L2CCYs9cRJoYwasXk3SSBPZbuFZOESGXEOeG9X4epZQBZi/NlUxHxObqXmt3BsArqAL51kQfQi+UJrzxmN1KWqQdmMtmdIijKdc9PuOFT0wVjtEJZnd/G+Z7qi6dlFl/qq97KOs7wbhFPR8d0utDqDclVwcOrSgJmUSMFXSgiQ4D3DjbzTAV/fGtpk5GbJQ5uDJ109QN1SUIWggxOymNVhRO0NpNu6N0VHeNUS1xm2t57946bkMGx79yIItHs6G9UNsWriQV2Gd3v1GeH9vI5O3xHsjzE0wnPm5+cYlJDea+M1Av7fJ8Xvk+Kg4gvPOexlUcnEwD1YWKXJRXKADu7QmbxIvQDtBKPwqjpi4gXesoQ6Qtr1QBvB1DJprt/Wg42SYR1KVIs/bKvjgINa1nSbJxmqvTAmSEIfKqDz9ECLwnQqWpmEQ4Xkf5inNsX/aQlTDbq4yM9/XKb7ecX88XGJvUF+AMlUJGSandqT8ScSg/f/y1mde7st9udotn00LEtTj4m5V2xBJN5j0U7/M0O7c+NRtTpB9fn/AtHW1J8z4Nm79TmvaOztH34+mN7t79t+fMaw9W1N1l/C5GlM/urxMIh5tevv8+z3f4Q18/8AuRGCJz2NtrQAAAGEaUNDUElDQyBwcm9maWxlAAB4nH2RPUjDQBzFX9NqRSoOFhRxyFCd7KKijqWKRbBQ2gqtOphc+iE0aUhSXBwF14KDH4tVBxdnXR1cBUHwA8RdcFJ0kRL/lxRaxHhw3I939x537wC" \
    "hUWGqGYgBqmYZ6URczOVXxOArAujGIGYQlZipJzMLWXiOr3v4+HoX5Vne5/4cfUrBZIBPJI4x3bCI14mnNy2d8z5xmJUlhficeNygCxI/cl12+Y1zyWGBZ4aNbHqOOEwsljpY7mBWNlTiKeKIomqUL+RcVjhvcVYrNda6J39hqKAtZ7hOcwQJLCKJFETIqGEDFViI0qqRYiJN+3EP/7DjT5FLJtcGGDnmUYUKyfGD/8Hvbs3i5ISbFIoDXS+2/TEKBHeBZt22v49tu3kC+J+BK63trzaA2U/S620tcgT0bwMX121N3gMud4ChJ10yJEfy0xSKReD9jL4pDwzcAr2rbm+tfZw+AFnqaukGODgExkqUvebx7p7O3v490+rvBwxRcuTDKhh2AAAPNGlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNC40LjAtRXhpdjIiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iCiAgICB4bWxuczpzdEV2dD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL3NUeXBlL1Jlc291cmNlRXZlbnQjIgogICAgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIgogICAgeG1sbnM6R0lNUD0iaHR0cDovL3d3dy5naW1wLm9yZy94bXAvIgogICAgeG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iCiAgICB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iCiAgIHhtcE1NOkRvY3VtZW50SUQ9ImdpbXA6ZG9jaWQ6Z2ltcDpmYTQyYmQ0Zi1lMWYyLTQwNDYtYTdhZS0yNWZiM2FhZWYzODMiCiAgIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6OTRkMmRjZDgtODM2OC00OWJjLTg2MzYtMDc2NzM3OTRlYjAwIgogICB4bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6MDk4ZjRhNzQtMDc2My00ZjdhLWJmNDQtNWEyMzE1OTlhODMyIgogICBkYzpGb3JtYXQ9ImltYWdlL3BuZyIKICAgR0lNUDpBUEk9IjIuMCIKICAgR0lNUDpQbGF0Zm9ybT0iV2luZG93cyIKICAgR0lNUDpUaW1lU3RhbXA9IjE3NDQwMTA4NTMyNTkwMDkiCiAgIEdJTVA6VmVyc2lvbj0iMi4xMC4zNiIKICAgdGlmZjpPcmllbnRhdGlvbj0iMSIKICAgeG1wOkNyZWF0b3JUb29sPSJHSU1QIDIuMTAiCiAgIHhtcDpNZXRhZGF0YURhdGU9IjIwMjU6MDQ6MDdUMTY6Mjc6MjkrMDk6MDAiCiAgIHhtcDpNb2RpZnlEYXRlPSIyMDI1OjA0OjA3VDE2OjI3OjI5KzA5OjAwIj4KICAgPHhtcE1NOkhpc3Rvcnk+CiAgICA8cmRmOlNlcT4KICAgICA8cmRmOmxpCiAgICAgIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiCiAgICAgIHN0RXZ0OmNoYW5nZWQ9Ii8iCiAgICAgIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6ZGJkYWVjZmItYzI0YS00MGIyLThjZTctZTdmZDM4MWQ0ODFlIgogICAgICBzdEV2dDpzb2Z0d2FyZUFnZW50PSJHaW1wIDIuMTAgKFdpbmRvd3MpIgogICAgICBzdEV2dDp3aGVuPSIyMDI0LTA4LTIxVDE0OjI1OjM2Ii8+CiAgICAgPHJkZjpsaQogICAgICBzdEV2dDphY3Rpb249InNhdmVkIgogICAgICBzdEV2dDpjaGFuZ2VkPSIvIgogICAgICBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOjQ1ZDJhNzk0LTg5NDEtNGZhMS04NmI2LTk1N2I5NDIwMTliZSIKICAgICAgc3RFdnQ6c29mdHdhcmVBZ2VudD0iR2ltcCAyLjEwIChXaW5kb3dzKSIKICAgICAgc3RFdnQ6d2hlbj0iMjAyNC0wOC0yMVQxNToyMDowNyIvPgogICAgIDxyZGY6bGkKICAgICAgc3RFdnQ6YWN0aW9u" \
    "PSJzYXZlZCIKICAgICAgc3RFdnQ6Y2hhbmdlZD0iLyIKICAgICAgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDpkZWE1YjE5ZS01YTZhLTQzY2EtYTg3NS03ZGQ0NzZlNjM3MzkiCiAgICAgIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkdpbXAgMi4xMCAoV2luZG93cykiCiAgICAgIHN0RXZ0OndoZW49IjIwMjUtMDQtMDdUMTY6Mjc6MzMiLz4KICAgIDwvcmRmOlNlcT4KICAgPC94bXBNTTpIaXN0b3J5PgogIDwvcmRmOkRlc2NyaXB0aW9uPgogPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI" \
    "CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgIAo8P3hwYWNrZXQgZW5kPSJ3Ij8+N8DEHgAAAAZiS0dEAEAAQABAp/YvZgAAAAlwSFlzAAAuIwAALiMBeKU/dgAAAAd0SU1FB+kEBwcbIXXYs9IAAAAZdEVYdENvbW1lbnQAQ3JlYXRlZCB3aXRoIEdJTVBXgQ4XAAAG/ElEQVRo3t2ZW2wU1xnHf99c9u5LbWNssLExGHGpG7vUxiUBp9SJKC2kiaJEVEVVg/rSPhTKS4ryUKmV1TdoS6XiqiKJFYmkCjRP1KSWq4rIDmnSWulFFsUJWssYqI2pvbbXlz198Oxldmbx2hjH5kijOfOdc2bPf77L//vOCsDE5peCiHYS0Y8gejmig+go6z53aSTlmk2m0FLGtZTnZF+JQLyPOO+INUdABIVY49YdUp5BQRikTUHLus6vR2Ri03eCiPYnRG/EtvGlAiLWmiUHMrcGuoFmDdRJUI2s3tao4KSGUkdY/e2IBpQ/AkDKNR6RZsw7o8iL8cN9c06Y7pSWw9nG4n2xnFEJKFC3x4kNRJjtGoZxtfxApDCA+eyTS/eLszFmwsNMf9TP1Kv/QY3ElghIjo/0s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"

image_data = base64.b64decode(encoded_string)

# バイナリデータから画像を作成
PR_icon = Image.open(BytesIO(image_data))

photo_ico = ImageTk.PhotoImage(PR_icon)
root.iconphoto(False, photo_ico)
root.title(f"PressureReader v{version}")
root.minsize(700, 680)

# メインフレーム（左：画像エリア, 右：ボタンエリア）
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Create canvas to display image
canvas = tk.Canvas(main_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#2026/3/27 画面初期表示変更
canvas.bind("<Configure>", lambda e: update_canvas_image())

# ボタンエリア（固定幅）
#button_frame_container = tk.Frame(main_frame, width=175)
button_frame_container = tk.Frame(main_frame, width=280)
button_frame_container.pack(side=tk.RIGHT, fill=tk.Y)
#button_frame_container.pack_propagate(False)  # 26/04/16 スクロールバーを表示

# Canvas + Scrollbar を button_frame_container に設置
#button_canvas = tk.Canvas(button_frame_container, width=175, highlightthickness=0, bd=0)
button_canvas = tk.Canvas(button_frame_container, width=280, highlightthickness=0, bd=0)
scrollbar = tk.Scrollbar(button_frame_container, orient=tk.VERTICAL, command=button_canvas.yview)
button_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
button_canvas.configure(yscrollcommand=scrollbar.set)

button_frame = tk.Frame(button_canvas)
button_canvas.create_window((0, 0), window=button_frame, anchor='nw')

# サイズに応じてスクロール範囲を更新し、スクロールバーの表示を制御
def on_frame_configure(event):
    # 更新されたサイズに基づいてスクロール領域を設定
    button_canvas.configure(scrollregion=button_canvas.bbox("all"))

    # button_canvas の現在の高さを取得
    canvas_height = button_canvas.winfo_height()
    # button_frame の要求サイズ（高さ）を取得
    frame_height = button_frame.winfo_reqheight()

    if frame_height > canvas_height:
        # コンテンツがはみ出している場合、スクロールバーを表示
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    else:
        # コンテンツが全て収まっている場合、スクロールバーを非表示
        scrollbar.pack_forget()

button_frame.bind("<Configure>", on_frame_configure)

# マウスホイールでもスクロールできるようにする（必要な場合のみ）
def _on_mousewheel(event):
    canvas_height = button_canvas.winfo_height()
    frame_height = button_frame.winfo_reqheight()
    if frame_height > canvas_height:
        # マウスホイールイベントの方向に応じてスクロール
        button_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# プラットフォームに依存せずマウスホイールイベントをバインド
def bind_mousewheel(widget):
    widget.bind("<Enter>", lambda e: widget.bind_all("<MouseWheel>", _on_mousewheel))
    widget.bind("<Leave>", lambda e: widget.unbind_all("<MouseWheel>"))

bind_mousewheel(button_canvas)

style_1 = ttk.Style()
style_1.configure("Custom.TLabel", font=("Meiryo ui", 10, "bold"))
style_2 = ttk.Style()
style_2.configure("Custom2.TLabel", foreground="#c942a5", background="#ffffff")
custom_font=("Meiryo ui", 16, "bold")
detected_value_font=("Meiryo ui", 13, "bold")
style_3 = ttk.Style()
style_3.configure("Custom3.TMenubutton", font=("Meiryo ui", 11, "bold"), foreground="#c942a5")
style_4 = ttk.Style()
style_4.configure("Custom4.TLabel", font=("Meiryo ui", 9, "bold"))

SHEET_TYPE_PLACEHOLDER_DISPLAY = "感圧紙を選択"
SHEET_TYPE_PLACEHOLDER_VALUE = "感圧紙を選択"


def is_sheet_type_unselected(value=None):
    if value is None:
        try:
            value = selected_var.get()
        except Exception:
            return True
    return value in ("", SHEET_TYPE_PLACEHOLDER_DISPLAY, SHEET_TYPE_PLACEHOLDER_VALUE)


def set_sheet_type_unselected():
    global suppress_sheet_type_reset
    suppress_sheet_type_reset = True
    try:
        selected_var.set(SHEET_TYPE_PLACEHOLDER_VALUE)
    finally:
        suppress_sheet_type_reset = False


def update_entries_and_buttons(*args):
    global suppress_sheet_type_reset, swatch_brightness_bounds
    if not suppress_sheet_type_reset:
        for entry in all_entries:
            entry.delete(0, tk.END)
        swatch_brightness_bounds.clear()
        clear_detected_value_entries()

    # 全てのエントリ/ボタン/状態表示を非表示にする
    for entry, button in zip(all_entries, all_buttons):
        entry.grid_forget()
        button.grid_forget()
    for status_label in brightness_status_labels.values():
        status_label.grid_forget()

    is_unselected = is_sheet_type_unselected()
    detail_widget_names = [
        "button_iromihon",
        "label_jouken1",
        "label_jouken2",
        "ondo_entry",
        "shitsudo_entry",
        "button_pixmm",
        "pixmm_unit_frame",
        "button_jouken",
        "button_metacopy",
    ]
    for widget_name in detail_widget_names:
        widget = globals().get(widget_name)
        if widget is None:
            continue
        try:
            if is_unselected:
                if widget.winfo_manager() == "grid":
                    widget.grid_remove()
            else:
                widget.grid()
        except tk.TclError:
            pass

    if is_unselected:
        return

    # 感圧紙種類に応じて、見本ボタン＋状態ラベルを表示
    active_slots = get_active_brightness_slots()
    for i, (value_key, entry, button) in enumerate(active_slots):
        button.grid(row=7+i, column=0, columnspan=2, padx=(10,0), pady=(0,0), sticky=tk.E)
        brightness_status_labels[value_key].grid(row=7+i, column=2, columnspan=2, padx=(5,20), pady=(0,0), sticky=tk.W)
        if suppress_sheet_type_reset:
            if entry.get().strip() == "":
                set_brightness_status(value_key, "unset")
            else:
                set_brightness_status(value_key, "success")
        else:
            set_brightness_status(value_key, "unset")

def is_valid_numeric_entry(entry):
    value = entry.get().strip()
    if value == "":
        return False
    try:
        float(value)
        return True
    except ValueError:
        return False


def get_analysis_condition_missing_message():
    if is_sheet_type_unselected():
        return " 感圧紙の種類をリストから選択してください "

    # 明度は最優先で案内する（標準色見本処理が必要なため）
    for entry in get_active_brightness_entries():
        if not is_valid_numeric_entry(entry):
            return " 標準色見本処理ボタンで色見本を設定してください "

    has_ondo = is_valid_numeric_entry(ondo_entry)
    has_shitsudo = is_valid_numeric_entry(shitsudo_entry)

    if not has_ondo and not has_shitsudo:
        return " 温度[℃]、湿度[%]を入力してください "
    if not has_ondo:
        return " 温度[℃]を入力してください "
    if not has_shitsudo:
        return " 湿度[%]を入力してください "

    return None


def are_all_entries_valid(all_entries, ondo_entry, shitsudo_entry):
    missing_message = get_analysis_condition_missing_message()
    if missing_message is not None:
        comment_label = tk.Label(root, text=missing_message,
                                 fg="white", bg="#c942a5", font=("Meiryo ui", 16, "bold"))
        comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        root.after(2000, comment_label.destroy)
        return False
    return True



# ボタンフレーム******************************************************************************************************************************************************************

# プレスケール選択欄***********************************************************************************************************************
selected_var = tk.StringVar(value=SHEET_TYPE_PLACEHOLDER_VALUE)
# selected_var.set("4LW 持続圧")  # 初期選択
selected_var.trace("w", update_entries_and_buttons)  # 値変更時にupdate_entriesを呼び出し


def clear_detected_value_entries():
    if "atai_ave_entry" in globals():
        atai_ave_entry.delete(0, tk.END)
    if "atai_max_entry" in globals():
        atai_max_entry.delete(0, tk.END)
    if "atai_min_entry" in globals():
        atai_min_entry.delete(0, tk.END)


def get_selected_sheet_pressure_limits():
    selected = selected_var.get()
    if selected in ("3LW 持続圧", "3LW 瞬間圧"):
        return 0.2, 0.6
    if selected in ("4LW 持続圧", "4LW 瞬間圧"):
        return 0.05, 0.2
    if selected in ("5LW 持続圧", "5LW 瞬間圧"):
        return 0.006, 0.05
    if selected in ("LLW 持続圧", "LLW 瞬間圧"):
        return 0.5, 2.5
    if selected in ("LW 持続圧", "LW 瞬間圧"):
        return 2.5, 10.0
    if selected in ("MS 持続圧", "MS 瞬間圧"):
        return 10.0, 50.0
    if selected in ("HS 持続圧", "HS 瞬間圧"):
        return 50.0, 130.0
    if selected == "HHS":
        return 130.0, 300.0
    return None, None


def format_detected_pressure_value(press_value):
    lower, upper = get_selected_sheet_pressure_limits()
    if press_value is None or lower is None or upper is None:
        return "測定範囲外"
    try:
        pressure = float(press_value)
    except (TypeError, ValueError):
        return "測定範囲外"

    if lower <= pressure <= upper:
        return f"{pressure:.6f}"
    return "測定範囲外"


def update_detected_value_entries(avg_press, max_press, min_press):
    clear_detected_value_entries()
    atai_ave_entry.insert(0, format_detected_pressure_value(avg_press))
    atai_max_entry.insert(0, format_detected_pressure_value(max_press))
    atai_min_entry.insert(0, format_detected_pressure_value(min_press))

# オプションメニューの作成
options = ["5LW 持続圧","5LW 瞬間圧","4LW 持続圧","4LW 瞬間圧","3LW 持続圧","3LW 瞬間圧","LLW 持続圧","LLW 瞬間圧","LW 持続圧","LW 瞬間圧","MS 持続圧","MS 瞬間圧","HS 持続圧","HS 瞬間圧","HHS", SHEET_TYPE_PLACEHOLDER_VALUE]
option_menu = ttk.OptionMenu(button_frame, selected_var, SHEET_TYPE_PLACEHOLDER_DISPLAY, *options, style="Custom3.TMenubutton")
option_menu.grid(row=4, column=0, columnspan=4, padx=(0,0), pady=(0,0), sticky=tk.W)

label_ken = ttk.Label(button_frame, text="解析条件：", style="Custom.TLabel")
label_ken.grid(row=3, column=0, columnspan=4, padx=(5,0), pady=(0,0), sticky=tk.W)

# Create buttons to select region
button_mihon_15 = ttk.Button(button_frame, text="1.5", width=7)
button_mihon_13 = ttk.Button(button_frame, text="1.3", width=7)
button_mihon_11 = ttk.Button(button_frame, text="1.1", width=7)
button_mihon_10 = ttk.Button(button_frame, text="1.0", width=7)
button_mihon_09 = ttk.Button(button_frame, text="0.9", width=7)
button_mihon_08 = ttk.Button(button_frame, text="0.8", width=7)
button_mihon_07 = ttk.Button(button_frame, text="0.7", width=7)
button_mihon_06 = ttk.Button(button_frame, text="0.6", width=7)
button_mihon_05 = ttk.Button(button_frame, text="0.5", width=7)
button_mihon_04 = ttk.Button(button_frame, text="0.4", width=7)
button_mihon_03 = ttk.Button(button_frame, text="0.3", width=7)
button_mihon_02 = ttk.Button(button_frame, text="0.2", width=7)
button_mihon_01 = ttk.Button(button_frame, text="0.1", width=7)

# Create textboxes to display brightness values
brightness_entry_15 = ttk.Entry(button_frame, width=15)
brightness_entry_13 = ttk.Entry(button_frame, width=15)
brightness_entry_11 = ttk.Entry(button_frame, width=15)
brightness_entry_10 = ttk.Entry(button_frame, width=15)
brightness_entry_09 = ttk.Entry(button_frame, width=15)
brightness_entry_08 = ttk.Entry(button_frame, width=15)
brightness_entry_07 = ttk.Entry(button_frame, width=15)
brightness_entry_06 = ttk.Entry(button_frame, width=15)
brightness_entry_05 = ttk.Entry(button_frame, width=15)
brightness_entry_04 = ttk.Entry(button_frame, width=15)
brightness_entry_03 = ttk.Entry(button_frame, width=15)
brightness_entry_02 = ttk.Entry(button_frame, width=15)
brightness_entry_01 = ttk.Entry(button_frame, width=15)

all_entries = [brightness_entry_15, brightness_entry_13, brightness_entry_11, brightness_entry_10, brightness_entry_09, brightness_entry_08, brightness_entry_07, brightness_entry_06, brightness_entry_05, brightness_entry_04, brightness_entry_03, brightness_entry_02, brightness_entry_01]
all_buttons = [button_mihon_15, button_mihon_13, button_mihon_11, button_mihon_10, button_mihon_09, button_mihon_08, button_mihon_07, button_mihon_06, button_mihon_05, button_mihon_04, button_mihon_03, button_mihon_02, button_mihon_01]

brightness_slots = [
    ("15", brightness_entry_15, button_mihon_15),
    ("13", brightness_entry_13, button_mihon_13),
    ("11", brightness_entry_11, button_mihon_11),
    ("10", brightness_entry_10, button_mihon_10),
    ("09", brightness_entry_09, button_mihon_09),
    ("08", brightness_entry_08, button_mihon_08),
    ("07", brightness_entry_07, button_mihon_07),
    ("06", brightness_entry_06, button_mihon_06),
    ("05", brightness_entry_05, button_mihon_05),
    ("04", brightness_entry_04, button_mihon_04),
    ("03", brightness_entry_03, button_mihon_03),
    ("02", brightness_entry_02, button_mihon_02),
    ("01", brightness_entry_01, button_mihon_01),
]

brightness_status_labels = {
    key: tk.Label(
        button_frame,
        text="",
        fg="black",
        bg=button_frame.cget("bg"),
        bd=0,
        relief="flat",
        highlightthickness=0,
        font=("Meiryo ui", 10),
    )
    for key, _, _ in brightness_slots
}
swatch_brightness_bounds = {}


def get_active_brightness_keys(selected_value=None):
    if selected_value is None:
        selected_value = selected_var.get()
    if selected_value in ["HS 持続圧", "HS 瞬間圧", "3LW 持続圧", "3LW 瞬間圧", "HHS"]:
        return ["13", "11", "09", "07", "05", "03", "01"]
    if selected_value in ["MS 持続圧", "MS 瞬間圧", "LW 持続圧", "LW 瞬間圧", "LLW 持続圧", "LLW 瞬間圧"]:
        return ["15", "13", "11", "09", "07", "05", "03", "01"]
    if selected_value in ["4LW 持続圧", "4LW 瞬間圧", "5LW 持続圧", "5LW 瞬間圧"]:
        return ["10", "08", "06", "04", "02", "01"]
    return []


def get_active_brightness_slots(selected_value=None):
    keys = set(get_active_brightness_keys(selected_value))
    return [slot for slot in brightness_slots if slot[0] in keys]


def get_active_brightness_entries(selected_value=None):
    return [entry for _, entry, _ in get_active_brightness_slots(selected_value)]


def set_brightness_status(value_key, status):
    label = brightness_status_labels[value_key]
    if status == "success":
        label.config(text="色見本 設定完了", fg="black", font=("Meiryo ui", 10))
    elif status == "failed":
        label.config(text="読取失敗(やり直し)", fg="#d10000", font=("Meiryo ui", 10, "bold"))
    else:
        label.config(text="未設定", fg="#0057d9", font=("Meiryo ui", 10, "bold"))


def format_brightness_key(value_key):
    return f"{int(value_key) / 10:.1f}"

update_entries_and_buttons()

label_jouken1 = ttk.Label(button_frame, text="温度[℃]")
label_jouken1.grid(row=15, column=0, columnspan=2, padx=(10,0), pady=(8,0), sticky=tk.W)
label_jouken2 = ttk.Label(button_frame, text="湿度[%]")
label_jouken2.grid(row=16, column=0, columnspan=2, padx=(10,0), pady=(0,0), sticky=tk.W)

ondo_entry = ttk.Entry(button_frame, width=15)
ondo_entry.grid(row=15, column=2, columnspan=2, padx=(5,10), pady=(8,0), sticky=tk.W)
shitsudo_entry = ttk.Entry(button_frame, width=15)
shitsudo_entry.grid(row=16, column=2, columnspan=2, padx=(5,10), pady=(0,0), sticky=tk.W)


# スケーリングボタン*****************************************************************************************************

# pixelをmmに
def set_conversion_factor():
    global line_start, line_end, temp_line1, temp_line2, conversion_factor, scale, photo_ico
    
    if no_image(canvas, root):
        return
    
    def custom_askfloat(title, prompt):
        """ カスタムダイアログを作成し、アイコンを設定 """
        dialog = tk.Toplevel(root)
        dialog.title(title)
        w = 280  # 幅
        h = 140  # 高さ
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        
        # アイコン設定
        dialog.iconphoto(False, photo_ico)
        tk.Label(dialog, text=prompt).pack(pady=(10, 6))
        entry = tk.Entry(dialog)
        entry.pack(pady=4)
        
        result = None
        def submit():
            nonlocal result
            try:
                result = float(entry.get())
                dialog.destroy()
            except ValueError:
                entry.delete(0, tk.END)
    
        tk.Button(dialog, text="OK", command=submit, width=13).pack(pady=(8, 10))
        
        dialog.grab_set()  # モーダルにする
        root.wait_window(dialog)  # ダイアログが閉じるまで待機
        
        return result

    def on_line_draw(event):
        global line_start, line_end, temp_line1, temp_line2, conversion_factor, scale
    
        if not line_start:
            # 最初のクリックで開始点を設定
            line_start = (event.x, event.y)
        else:
            # 次のクリックで終了点を設定
            line_end = (event.x, event.y)
            temp_line2 = canvas.create_line(
                line_start[0], line_start[1], line_end[0], line_end[1], fill="red", width=3, tags="line"
            )
    
            # ピクセル距離を計算
            pixel_distance = math.sqrt((line_end[0] - line_start[0]) ** 2 + (line_end[1] - line_start[1]) ** 2) / scale
    
            # 実寸を入力して換算係数を設定
            real_length = custom_askfloat("mm⇒px換算値", "線分の実寸[mm]を入力してください")
            if real_length is None:
                # キャンセルされた場合
                canvas.delete("line")
                reset_selection()
                return
    
            if real_length > 0:
                # 換算係数を計算して表示
                conversion_factor = round(real_length / pixel_distance, 6)
                pixmm_entry.delete(0, 'end')
                pixmm_entry.insert(0, conversion_factor)
                
                messagebox.showinfo("成功", f"換算係数を設定しました: {conversion_factor:.4f} mm/px")
            else:
                messagebox.showwarning("エラー", "有効な実寸を入力してください。")
    
            # 最終的に線を消去
            canvas.delete("line")
            reset_selection()

    def reset_selection():
        """選択状態をリセットし、イベントを解除する。"""
        global line_start, line_end, temp_line1, temp_line2
        line_start, line_end, temp_line1, temp_line2 = None, None, None, None
        canvas.unbind("<Motion>")
        canvas.unbind("<Button-1>")

        # 必要に応じて他のイベントを再バインド
        canvas.bind("<Button-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)

    def on_mouse_move(event):
        """マウス移動中の線を描画"""
        global temp_line1
        if line_start:
            # 既存の仮線を削除して新しい線を描画
            if temp_line1:
                canvas.delete(temp_line1)
            temp_line1 = canvas.create_line(
                line_start[0], line_start[1], event.x, event.y, fill="blue", dash=(8, 2), width=2, tags="line"
            )

    canvas.delete("mark","line","text","rect")
    # マウスイベントのバインド
    canvas.bind("<Button-1>", on_line_draw)
    canvas.bind("<Motion>", on_mouse_move)
    temp_line1 = None

button_pixmm = ttk.Button(button_frame, text="ｽｹｰﾘﾝｸﾞ", width=7, command=set_conversion_factor)
button_pixmm.grid(row=17, column=0, columnspan=2, padx=(10,0), pady=(5,0), sticky=tk.W)

pixmm_unit_frame = tk.Frame(button_frame)
pixmm_unit_frame.grid(row=17, column=2, columnspan=1, padx=(5,0), pady=(5,0), sticky=tk.W)

pixmm_entry = ttk.Entry(pixmm_unit_frame, width=10)
pixmm_entry.pack(side=tk.LEFT, padx=(0,0))

label_pixmm_unit = ttk.Label(pixmm_unit_frame, text="mm/px")
label_pixmm_unit.pack(side=tk.LEFT, padx=(1,0))


def get_scaling_factor_value():
    value = pixmm_entry.get().strip()
    if value == "":
        return None
    try:
        factor = float(value)
    except ValueError:
        return None
    if factor <= 0:
        return None
    return factor


def get_circle_input_unit():
    factor = get_scaling_factor_value()
    if factor is not None:
        return "mm", factor
    return "px", None


def ask_circle_radius_value(unit_label):
    dialog = tk.Toplevel(root)
    dialog.title("円サイズ入力")
    w = 300
    h = 160
    x = (screen_width - w) // 2
    y = (screen_height - h) // 2
    dialog.geometry(f"{w}x{h}+{x}+{y}")
    dialog.iconphoto(False, photo_ico)

    tk.Label(dialog, text="半径を入力してください").pack(pady=(10, 6))

    input_frame = tk.Frame(dialog)
    input_frame.pack(pady=4)
    entry = tk.Entry(input_frame, width=12)
    entry.pack(side=tk.LEFT, padx=(0, 4))
    tk.Label(input_frame, text=unit_label).pack(side=tk.LEFT)

    result = None

    def submit():
        nonlocal result
        try:
            value = float(entry.get())
        except ValueError:
            messagebox.showwarning("エラー", "有効な数値を入力してください。")
            entry.focus_set()
            entry.selection_range(0, tk.END)
            return
        if value <= 0:
            messagebox.showwarning("エラー", "0より大きい値を入力してください。")
            entry.focus_set()
            entry.selection_range(0, tk.END)
            return
        result = value
        dialog.destroy()

    def cancel():
        dialog.destroy()

    button_frame_dialog = tk.Frame(dialog)
    button_frame_dialog.pack(pady=(10, 10))
    tk.Button(button_frame_dialog, text="OK", command=submit, width=10).pack(side=tk.LEFT, padx=(0, 8))
    tk.Button(button_frame_dialog, text="キャンセル", command=cancel, width=10).pack(side=tk.LEFT)

    dialog.protocol("WM_DELETE_WINDOW", cancel)
    dialog.grab_set()
    entry.focus_set()
    root.wait_window(dialog)
    return result


def get_circle_size_display_text():
    unit_label, scaling_factor = get_circle_input_unit()
    rx_value = float(radius_x)
    ry_value = float(radius_y)
    if unit_label == "mm" and scaling_factor is not None:
        rx_value *= scaling_factor
        ry_value *= scaling_factor

    if abs(rx_value - ry_value) < 1e-6:
        return f"半径 {rx_value:.3f}{unit_label}"
    return f"半径X {rx_value:.3f}{unit_label} / 半径Y {ry_value:.3f}{unit_label}"



# 標準色見本処理 ボタン**********************************************************************************************

def insert_to_visible_entries(avg_list, bounds_list=None, debug_failed_observed_values=None):
    global current_value, swatch_brightness_bounds
    active_slots = get_active_brightness_slots()
    failed_keys = []

    # 明度値を内部エントリーへ保持し、状態表示を更新
    for i, (value_key, entry, _) in enumerate(active_slots):
        entry.delete(0, tk.END)
        if i < len(avg_list):
            avg_value = avg_list[i]
            entry.insert(0, f"{avg_value:.2f}")
            set_brightness_status(value_key, "success")
            if bounds_list is not None and i < len(bounds_list):
                min_value, max_value = bounds_list[i]
                swatch_brightness_bounds[value_key] = (float(min_value), float(max_value))
            else:
                swatch_brightness_bounds.pop(value_key, None)
            print(f"[DEBUG] swatch brightness {format_brightness_key(value_key)} = {avg_value:.2f}")
        else:
            entry.insert(0, "")
            set_brightness_status(value_key, "failed")
            swatch_brightness_bounds.pop(value_key, None)
            failed_keys.append(format_brightness_key(value_key))
            observed_value = None
            if debug_failed_observed_values is not None:
                observed_value = debug_failed_observed_values.get(value_key)
            if observed_value is not None:
                print(
                    f"[DEBUG] swatch brightness {format_brightness_key(value_key)} = "
                    f"{float(observed_value):.2f} (failed-observed-pctl)"
                )
            else:
                print(
                    f"[DEBUG] swatch brightness {format_brightness_key(value_key)} = "
                    f"0.00 (failed-observed-empty)"
                )

    if failed_keys:
        print(f"[DEBUG] swatch missing brightness keys: {', '.join(failed_keys)}")

#ボタン設置
def on_enter_iromihon(event):
    button_iromihon.config(image=icon14)
def on_leave_iromihon(event):
    button_iromihon.config(image=icon13)

# 画像の読み込みとリサイズ
icon13 = tk.PhotoImage(file=os.path.join(ima_path, "iromihon_off.png"))  # 画像のリサイズ
icon14 = tk.PhotoImage(file=os.path.join(ima_path, "iromihon_on.png"))  # 画像のリサイズ

# ボタン作成
button_iromihon = ttk.Button(
    button_frame,
    image=icon13,
    text='標準色見本処理',
    compound=tk.LEFT,
    command=lambda: set_mode_rect("14"),
    padding=[5, 0, 22, 0]
)

button_iromihon.image = icon13
button_iromihon.grid(row=5, column=0, columnspan=4, padx=(8, 0), pady=(5, 0), sticky=tk.W)
button_iromihon.bind("<Enter>", on_enter_iromihon)
button_iromihon.bind("<Leave>", on_leave_iromihon)



# PNGに条件保存　ボタン --------------------------------------------------------------------------------------------

def meta():
    global brightness_entry_15, brightness_entry_13, brightness_entry_11, brightness_entry_10, brightness_entry_09, brightness_entry_08, brightness_entry_07, \
    brightness_entry_06, brightness_entry_05, brightness_entry_04, brightness_entry_03, brightness_entry_02, brightness_entry_01, ondo_entry, shitsudo_entry, \
    image_path, root, image_meta, selected_var, pixmm_entry, any_dir, source_image_path
    # エントリから値を取得
    png_values = [
        selected_var.get(),
        brightness_entry_15.get(),
        brightness_entry_13.get(),
        brightness_entry_11.get(),
        brightness_entry_10.get(),
        brightness_entry_09.get(),
        brightness_entry_08.get(),
        brightness_entry_07.get(),
        brightness_entry_06.get(),
        brightness_entry_05.get(),
        brightness_entry_04.get(),
        brightness_entry_03.get(),
        brightness_entry_02.get(),
        brightness_entry_01.get(),
        ondo_entry.get(),
        shitsudo_entry.get(),
        pixmm_entry.get()
    ]
    data_string = f"press{{{','.join(png_values)}}}"

    if image_path is not None:
        # 既存のPNG画像を開く
        image_meta = Image.open(image_path)
    
        # メタデータとして設定
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("info", data_string)
    
        # メタデータを含めて画像を保存
        image_meta.save(image_path, "PNG", pnginfo=metadata)
        
        if source_image_path:
            image_meta.save(source_image_path, "PNG", pnginfo=metadata)
        
        
        # コメントを1秒間表示する
        comment_label = tk.Label(root, text=" 保存しました ", fg="white", bg="#c942a5", font=("Meiryo ui", 16, "bold"))
        comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
        # 1秒後にラベルを削除する
        root.after(1000, comment_label.destroy)
    else:
        # コメントを1秒間表示する
        comment_label = tk.Label(root, text=" 画像を開いてください ", fg="white", bg="#c942a5", font=("Meiryo ui", 16, "bold"))
        comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
        # 1秒後にラベルを削除する
        root.after(1000, comment_label.destroy)


def on_enter_jouken(event):
    button_jouken.config(image=icon8)
def on_leave_jouken(event):
    button_jouken.config(image=icon7)

# 画像の読み込みとリサイズ
icon7 = tk.PhotoImage(file=os.path.join(ima_path, "jouken_off.png"))  # 画像のリサイズ
icon8 = tk.PhotoImage(file=os.path.join(ima_path, "jouken_on.png"))  # 画像のリサイズ

# ボタン作成
button_jouken = ttk.Button(
    button_frame,
    image=icon7,
    text='PNGに解析条件保存',
    compound=tk.LEFT,
    command=meta,
    padding=[5, 0, 1, 0] # 左, 上, 右, 下
)

button_jouken.image = icon7
button_jouken.grid(row=18, column=0, columnspan=4, padx=(8, 0), pady=(0, 0), sticky=tk.W)
button_jouken.bind("<Enter>", on_enter_jouken)
button_jouken.bind("<Leave>", on_leave_jouken)


# 圧力表示*****************************************************************************************************************************
label_ken = ttk.Label(button_frame, text="選択範囲の検出値（MPa）：", style="Custom.TLabel")
label_ken.grid(row=26, column=0, columnspan=4, padx=(5,0), pady=(20,0), sticky=tk.W)

detected_value_frame = ttk.Frame(button_frame)
detected_value_frame.grid(row=27, column=0, columnspan=4, padx=(11,12), pady=(0,0), sticky=tk.W)

label_detected_avg = ttk.Label(detected_value_frame, text="検出値（平均）", style="Custom4.TLabel")
label_detected_avg.grid(row=0, column=0, padx=(0,0), pady=(8,0), sticky=tk.W)
atai_ave_entry = tk.Entry(
    detected_value_frame,
    width=8,
    font=detected_value_font,
    fg="#c942a5",
    bg="#ffffff",
    relief="flat",
    bd=0,
    highlightthickness=0,
    highlightbackground="#ffffff",
    highlightcolor="#ffffff"
)
atai_ave_entry.grid(row=0, column=1, padx=(3,0), pady=(8,0), sticky=tk.W)
label_mpa_avg = ttk.Label(detected_value_frame, text="MPa", style="Custom4.TLabel")
label_mpa_avg.grid(row=0, column=2, padx=(3,6), pady=(8,0), sticky=tk.W)

label_detected_max = ttk.Label(detected_value_frame, text="検出値（最大）", style="Custom4.TLabel")
label_detected_max.grid(row=1, column=0, padx=(0,0), pady=(2,0), sticky=tk.W)
atai_max_entry = tk.Entry(
    detected_value_frame,
    width=8,
    font=detected_value_font,
    fg="#c942a5",
    bg="#ffffff",
    relief="flat",
    bd=0,
    highlightthickness=0,
    highlightbackground="#ffffff",
    highlightcolor="#ffffff"
)
atai_max_entry.grid(row=1, column=1, padx=(3,0), pady=(2,0), sticky=tk.W)
label_mpa_max = ttk.Label(detected_value_frame, text="MPa", style="Custom4.TLabel")
label_mpa_max.grid(row=1, column=2, padx=(3,6), pady=(2,0), sticky=tk.W)

label_detected_min = ttk.Label(detected_value_frame, text="検出値（最小）", style="Custom4.TLabel")
label_detected_min.grid(row=2, column=0, padx=(0,0), pady=(2,0), sticky=tk.W)
atai_min_entry = tk.Entry(
    detected_value_frame,
    width=8,
    font=detected_value_font,
    fg="#c942a5",
    bg="#ffffff",
    relief="flat",
    bd=0,
    highlightthickness=0,
    highlightbackground="#ffffff",
    highlightcolor="#ffffff"
)
atai_min_entry.grid(row=2, column=1, padx=(3,0), pady=(2,0), sticky=tk.W)
label_mpa_min = ttk.Label(detected_value_frame, text="MPa", style="Custom4.TLabel")
label_mpa_min.grid(row=2, column=2, padx=(3,6), pady=(2,0), sticky=tk.W)



# 圧力最大点 スライダー****************************************************************************************************************

def update_label(value):
    global marks, rect, image_id, start_x, start_y, end_x, end_y
    
    slider_value.set(f"{int(float(value))}")
    canvas.delete("mark")
    mark_lowest_brightness_points()
    

# 圧力の高い点にマークする
def mark_lowest_brightness_points():
    global marks, rect, scale, image_org_w, image_org_h, canvas_width, canvas_height, image_with_metadata
    global mode, polygon_points, polygon_id, center_x, center_y, radius_x, radius_y, circle_id
    global start_x, start_y, end_x, end_y
    
    try:
        num_points = int(slider_value.get())
    except ValueError:
        print("Error: Invalid number in mode_3_entry.")
        return
    if num_points <= 0:
        return
    try:
        min_brightness_threshold = 0.0  # 任意の明るさのしきい値を設定
    except ValueError:
        print("Error: Invalid value in brightness_entry_10.")
        return

    if cv_image_2 is None:
        return

    gray_image = cv2.cvtColor(cv_image_2, cv2.COLOR_RGB2GRAY)

    if scale <= 0:
        return
    inv_scale = 1 / scale  # 逆スケール変換
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    img_width, img_height = (
        int(image_with_metadata.size[0] * scale),
        int(image_with_metadata.size[1] * scale),
    )
    offset_x = int((canvas_width - img_width) / 2)
    offset_y = int((canvas_height - img_height) / 2)

    selection_mask = np.zeros((image_org_h, image_org_w), dtype=np.uint8)
    has_selection = False

    if mode == "rect":
        if rect is not None:
            x1 = max(0, min(int(start_x), int(end_x)) - offset_x)
            y1 = max(0, min(int(start_y), int(end_y)) - offset_y)
            x2 = min(img_width, max(int(start_x), int(end_x)) - offset_x)
            y2 = min(img_height, max(int(start_y), int(end_y)) - offset_y)
            sx = max(0, int(x1 * inv_scale))
            sy = max(0, int(y1 * inv_scale))
            ex = min(image_org_w, int(x2 * inv_scale))
            ey = min(image_org_h, int(y2 * inv_scale))
            if ex > sx and ey > sy:
                selection_mask[sy:ey, sx:ex] = 255
                has_selection = True
    elif mode == "polygon":
        if polygon_id is not None and len(polygon_points) >= 3:
            scaled_polygon_points = [
                (int((x - offset_x) * inv_scale), int((y - offset_y) * inv_scale))
                for x, y in polygon_points
            ]
            cv2.fillPoly(selection_mask, [np.array(scaled_polygon_points, dtype=np.int32)], 255)
            has_selection = np.any(selection_mask > 0)
    elif mode == "circle":
        if circle_id is not None and radius_x > 0 and radius_y > 0:
            cx = int((center_x - offset_x) * inv_scale)
            cy = int((center_y - offset_y) * inv_scale)
            rx = max(1, int(radius_x * inv_scale))
            ry = max(1, int(radius_y * inv_scale))
            cv2.ellipse(selection_mask, (cx, cy), (rx, ry), 0, 0, 360, 255, -1)
            has_selection = np.any(selection_mask > 0)

    if has_selection:
        mask = (selection_mask > 0) & (gray_image > min_brightness_threshold)
        filtered_image = np.full_like(gray_image, 255)
        filtered_image[mask] = gray_image[mask]
    else:
        mask = gray_image > min_brightness_threshold
        filtered_image = np.where(mask, gray_image, 255)

    if not np.any(filtered_image < 255):
        return
    min_points = []
    
    for _ in range(num_points):
        min_val, _, min_loc, _ = cv2.minMaxLoc(filtered_image)
        if min_val < 255:
            min_points.append(min_loc)
            filtered_image[min_loc[1], min_loc[0]] = 255
        else:
            break
        
    marks = []
    for (x, y) in min_points:
        x_scaled = int((x * scale)+((canvas_width-img_width)/2))
        y_scaled = int((y * scale)+((canvas_height-img_height)/2))
        mark = canvas.create_oval(x_scaled-5, y_scaled-5, x_scaled+5, y_scaled+5, outline='blue', fill='blue', tags="mark")
        marks.append(mark)


def calculate_point_pressure(canvas_x, canvas_y):
    global scale, image_with_metadata, cv_image_2, white_Value, image_org_w, image_org_h
    if cv_image_2 is None or image_with_metadata is None or scale <= 0:
        return None

    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    img_width, img_height = (
        int(image_with_metadata.size[0] * scale),
        int(image_with_metadata.size[1] * scale),
    )
    offset_x = int((canvas_width - img_width) / 2)
    offset_y = int((canvas_height - img_height) / 2)

    image_x = int((canvas_x - offset_x) * (1 / scale))
    image_y = int((canvas_y - offset_y) * (1 / scale))

    if image_x < 0 or image_y < 0 or image_x >= image_org_w or image_y >= image_org_h:
        return None

    gray_image = cv2.cvtColor(cv_image_2, cv2.COLOR_RGB2GRAY)
    brightness = gray_image[image_y, image_x]
    if brightness > white_Value:
        return None

    try:
        return c2p(brightness)
    except (ValueError, TypeError):
        return None


def show_point_pressure_text(canvas_x, canvas_y, pressure_value):
    canvas.delete("point_pressure")
    pressure_text = format_detected_pressure_value(pressure_value)
    text = "測定範囲外" if pressure_text == "測定範囲外" else f"{pressure_text}MPa"

    canvas.create_text(
        canvas_x,
        canvas_y - 10,
        text=text,
        anchor="s",
        fill="blue",
        font=("Arial", mm2fontsize),
        tags=("point_pressure", "point_pressure_single"),
    )


def show_polygon_point_pressure_text(point_index, canvas_x, canvas_y, pressure_value):
    point_tag = f"point_pressure_poly_{point_index}"
    canvas.delete(point_tag)
    pressure_text = format_detected_pressure_value(pressure_value)
    text = "測定範囲外" if pressure_text == "測定範囲外" else f"{pressure_text}MPa"

    canvas.create_text(
        canvas_x,
        canvas_y - 10,
        text=text,
        anchor="s",
        fill="blue",
        font=("Arial", mm2fontsize),
        tags=("point_pressure", point_tag),
    )

label_slider = ttk.Label(
    button_frame,
    text="高圧検出箇所",
    style="Custom.TLabel"
)
label_slider.grid(row=28, column=0, columnspan=4, padx=(10,0), pady=(5,0), sticky=tk.W)
label_slider_setting = ttk.Label(button_frame, text="表示数の設定", font=("Meiryo ui", 9))
label_slider_setting.grid(row=29, column=0, columnspan=4, padx=(10,0), pady=(0,0), sticky=tk.W)
slider_value = tk.StringVar()
slider_value.set("0")
label_20 = ttk.Label(button_frame, textvariable=slider_value)
label_20.grid(row=30, column=0, padx=(10,0), pady=(5,0), sticky=tk.W)
scale = ttk.Scale(button_frame, from_=0, to=100, orient="horizontal", length=105, command=update_label)
scale.grid(row=30, column=1, columnspan=3, padx=(0,0), pady=(0,0), sticky=tk.W)



# 測定範囲可視化 ボタン*************************************************************************************************
def apply_threshold():
    """しきい値に基づき画像の特定の明度範囲を色変換"""
    global processed_image, bri_Max, bri_Min, white_Value
    
    if image_with_metadata is None:
        print("No image loaded.")
        return
    try:
        # 境界誤差を抑えるため、固定マージン1でしきい値を内側へ寄せる
        threshold_margin = 1
        low_threshold = max(0, int(math.floor(bri_Max)) - threshold_margin)
        high_threshold = min(255, int(math.ceil(bri_Min)) + threshold_margin)

        # 色見本端点（先頭/末尾）は必ずレンジ内へ入るようにクランプ
        active_slots = get_active_brightness_slots()
        if len(active_slots) > 0:
            top_key = active_slots[0][0]
            bottom_key = active_slots[-1][0]

            top_bounds = swatch_brightness_bounds.get(top_key)
            if top_bounds is not None:
                top_brightness_min = top_bounds[0]
                low_threshold = min(low_threshold, int(math.floor(top_brightness_min)))
            else:
                top_entry = active_slots[0][1].get().strip()
                try:
                    top_brightness_min = float(top_entry)
                    low_threshold = min(low_threshold, int(math.floor(top_brightness_min)))
                except (ValueError, TypeError):
                    top_brightness_min = None

            bottom_bounds = swatch_brightness_bounds.get(bottom_key)
            if bottom_bounds is not None:
                bottom_brightness_max = bottom_bounds[1]
                high_threshold = max(high_threshold, int(math.ceil(bottom_brightness_max)))
            else:
                bottom_entry = active_slots[-1][1].get().strip()
                try:
                    bottom_brightness_max = float(bottom_entry)
                    high_threshold = max(high_threshold, int(math.ceil(bottom_brightness_max)))
                except (ValueError, TypeError):
                    bottom_brightness_max = None
        else:
            top_key = None
            bottom_key = None
            top_brightness_min = None
            bottom_brightness_max = None

        if low_threshold >= high_threshold:
            print("Error: Low threshold must be smaller than High threshold.")
            return
    except ValueError:
        print("Invalid threshold values.")
        return

    # NumPy 配列に変換
    image_np = np.array(image_with_metadata)
    
    # チャンネル数取得
    has_alpha = image_np.shape[2] == 4 if len(image_np.shape) == 3 else False
    
    # RGB 部分だけ抽出（RGBAでも対応）
    rgb_np = image_np[:, :, :3] if has_alpha else image_np
    
    # グレースケール画像を作成
    gray = cv2.cvtColor(rgb_np, cv2.COLOR_RGB2GRAY)
    
    # 色変換の定義（3要素）
    high_color = [0, 255, 1]
    low_color = [255, 255, 1]
    
    # 明度しきい値に基づいてマスク作成
    mask_high = (gray > high_threshold) & (gray <= white_Value)
    mask_low = gray < low_threshold
    print(
        f"[DEBUG] threshold low={low_threshold} high={high_threshold} "
        f"top_key={top_key} top_min={top_brightness_min} "
        f"bottom_key={bottom_key} bottom_max={bottom_brightness_max} "
        f"mask_low={int(mask_low.sum())} mask_high={int(mask_high.sum())}"
    )
    
    # 画像を1次元ビューに変換
    flat_rgb = rgb_np.reshape(-1, 3)
    flat_mask_high = mask_high.flatten()
    flat_mask_low = mask_low.flatten()
    
    # 対応する画素に色を代入
    flat_rgb[flat_mask_high] = high_color
    flat_rgb[flat_mask_low] = low_color
    
    # 元の形に戻す
    rgb_np[:, :, :] = flat_rgb.reshape(rgb_np.shape)
    
    # RGBAが元画像に含まれていた場合、alphaチャンネルを元に戻す
    if has_alpha:
        image_np[:, :, :3] = rgb_np
    else:
        image_np = rgb_np
    
    # 画像をPILに変換して保存
    processed_image = Image.fromarray(image_np)

# ボタン設置
apply_threshold_flag = tk.BooleanVar()
def pressrange_change():
    global apply_threshold_flag
    if apply_threshold_flag.get() == False:
        apply_threshold_flag.set(True)
        button_pressrange.config(image=icon4, text='測定範囲可視化：ON')
        button_pressrange.image = icon4
    else:
        apply_threshold_flag.set(False)
        button_pressrange.config(image=icon3, text='測定範囲可視化：OFF')
        button_pressrange.image = icon3
    update_canvas_image()
def pressrange_off():
    global apply_threshold_flag
    if apply_threshold_flag.get() == True:
        apply_threshold_flag.set(False)
        button_pressrange.config(image=icon3, text='測定範囲可視化：OFF')
        button_pressrange.image = icon3
        update_canvas_image()

icon3 = tk.PhotoImage(file=os.path.join(ima_path, "pressrange_off.png")).subsample(2, 2)
icon4 = tk.PhotoImage(file=os.path.join(ima_path, "pressrange_on.png")).subsample(2, 2)

button_pressrange = ttk.Button(
    button_frame,
    image=icon3,
    text='測定範囲可視化：OFF',
    compound=tk.TOP,
    command=pressrange_change,  # クリックでフラグと画像を切り替える
    padding=[0, 0]
)

button_pressrange.image = icon3  # 初期画像を保持
button_pressrange.grid(row=25, column=0, columnspan=4, padx=(8, 0), pady=(10, 0), sticky=tk.W)



# 選択範囲モード選択*******************************************************************************************************

start_x, start_y, end_x, end_y = None, None, None, None
line_start, line_end = None, None
conversion_factor = None  # ピクセル/mm の換算係数
# conversion_factor = pixmm_entry.get()
rect = None #　長方形の範囲
mode = "rect"
dimension_text = None  # 寸法表示用のテキスト
temp_line1 = None # pixel⇒mm変換時の線
temp_line2 = None # pixel⇒mm変換時の線


# 四角形モードの処理
def calculate_brightness(start_x, start_y, end_x, end_y, value_key, polygon_points=None):
    global scale, image_org_w, image_org_h, canvas_width, canvas_height, image_with_metadata, white_Value, \
        cv_image, cv_image_2, mode, canvas, white_Press, white_flag, white_Value2, press_Max, press_Min, px_count
    
    inv_scale = 1 / scale  # 逆スケール変換
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    img_width, img_height = (int(image_with_metadata.size[0] * scale), int(image_with_metadata.size[1] * scale))

    ave_press = None
    max_press = None
    min_press = None

    if mode == "rect":
        start_x2 = max(0, int(start_x) - int((canvas_width - img_width) / 2))
        start_y2 = max(0, int(start_y) - int((canvas_height - img_height) / 2))
        end_x2 = min(canvas_width, int(end_x) - int((canvas_width - img_width) / 2))
        end_y2 = min(canvas_height, int(end_y) - int((canvas_height - img_height) / 2))
    
        start_x3 = int(start_x2 * inv_scale)
        start_y3 = int(start_y2 * inv_scale)
        end_x3 = int(end_x2 * inv_scale)
        end_y3 = int(end_y2 * inv_scale)
        
        region = cv_image_2[start_y3:end_y3, start_x3:end_x3]
    
        # グレースケール変換
        gray_region = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
        # 有効なピクセルをフィルタリング
        valid_pixels = gray_region[gray_region <= white_Value]
        
        if value_key != "99":
            average_brightness = np.mean(valid_pixels)
            px_count = valid_pixels.size  # 有効なピクセル数をカウント
        else:
            # c2pを適用した値をNumPy配列として作成
            c2p_values = np.array([c2p(p) for p in valid_pixels])
            
            # ブールインデクシングを使用して範囲内の値を抽出
            filtered_values = c2p_values[(c2p_values >= press_Min) & (c2p_values <= press_Max)]
            px_count = filtered_values.size
            
            # 平均を計算
            if filtered_values.size > 0:
                ave_press = np.mean(filtered_values)
                max_press = np.max(filtered_values)
                min_press = np.min(filtered_values)
            else:
                ave_press = None  # 範囲内に値がない場合の処理
            
        
    if value_key == "14":

    # 標準色見本採色処理
        if cv_image is not None:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape
            x0, x1 = max(0, start_x3), min(w, end_x3)
            y0, y1 = max(0, start_y3), min(h, end_y3)
            roi = gray[y0:y1, x0:x1]
            if roi.size > 0:
    
                # === ラベリング処理 ===
                threshold_min = 30
                threshold_max = 250
                mask = cv2.inRange(roi, threshold_min, threshold_max)
    
                num_labels, labels = cv2.connectedComponents(mask)
                results = []
                total_pixels = roi.shape[0] * roi.shape[1]
                min_region_size = total_pixels * 0.07
                brightest_min_region_size = total_pixels * 0.02
                upper_gain_brightest = 0.10
                component_candidates = []
                prefilter_candidates = []
                
                for i in range(1, num_labels):
                    region_mask = (labels == i)
                    region_size = np.sum(region_mask)
                 
                    region_values = roi[region_mask]
                    if region_values.size == 0:
                        continue

                    mean_initial = float(np.mean(region_values))
                    prefilter_candidates.append(
                        {
                            "region_size": int(region_size),
                            "region_values": region_values,
                            "mean_initial": mean_initial,
                            "p99_nonwhite": None,
                        }
                    )

                brightest_prefilter_index = None
                if prefilter_candidates:
                    valid_p99_indices = []
                    for idx, candidate in enumerate(prefilter_candidates):
                        nonwhite_pixels = candidate["region_values"][candidate["region_values"] < 255]
                        if nonwhite_pixels.size > 0:
                            candidate["p99_nonwhite"] = float(np.percentile(nonwhite_pixels, 99))
                            valid_p99_indices.append(idx)

                    if valid_p99_indices:
                        selected_by = "p99_nonwhite"
                        brightest_prefilter_index = max(
                            valid_p99_indices,
                            key=lambda idx: prefilter_candidates[idx]["p99_nonwhite"],
                        )
                    else:
                        selected_by = "mean_fallback"
                        brightest_prefilter_index = max(
                            range(len(prefilter_candidates)),
                            key=lambda idx: prefilter_candidates[idx]["mean_initial"],
                        )

                    selected_candidate = prefilter_candidates[brightest_prefilter_index]
                    p99_text = "None"
                    if selected_candidate["p99_nonwhite"] is not None:
                        p99_text = f"{selected_candidate['p99_nonwhite']:.2f}"
                    print(
                        f"[DEBUG] swatch brightest selector: selected_by={selected_by} "
                        f"mean_initial={selected_candidate['mean_initial']:.2f} p99_nonwhite={p99_text}"
                    )

                for idx, pre_candidate in enumerate(prefilter_candidates):
                    mean_initial = pre_candidate["mean_initial"]
                    lower = mean_initial * (1 - 0.7)
                    upper_gain = upper_gain_brightest if idx == brightest_prefilter_index else 0.0
                    upper = mean_initial * (1 + upper_gain)
                    filtered = pre_candidate["region_values"][
                        (pre_candidate["region_values"] >= lower) & (pre_candidate["region_values"] <= upper)
                    ]
                    if filtered.size == 0:
                        continue
                 
                    mean_final = np.mean(filtered)
                    min_final = np.min(filtered)
                    max_final = np.max(filtered)

                    component_candidates.append(
                        {
                            "region_size": pre_candidate["region_size"],
                            "mean_final": float(mean_final),
                            "min_final": float(min_final),
                            "max_final": float(max_final),
                            "from_brightest_prefilter": idx == brightest_prefilter_index,
                        }
                    )

                if component_candidates:
                    flagged_indices = [
                        idx for idx, candidate in enumerate(component_candidates)
                        if candidate.get("from_brightest_prefilter", False)
                    ]
                    if flagged_indices:
                        brightest_index = flagged_indices[0]
                    else:
                        brightest_index = max(
                            range(len(component_candidates)),
                            key=lambda idx: component_candidates[idx]["mean_final"],
                        )
                    brightest_candidate = component_candidates[brightest_index]
                    brightest_adopted = brightest_candidate["region_size"] >= brightest_min_region_size
                    print(
                        f"[DEBUG] swatch brightest region check: "
                        f"size={brightest_candidate['region_size']} "
                        f"threshold={brightest_min_region_size:.1f} adopted={brightest_adopted} "
                        f"upper_gain_brightest={upper_gain_brightest:.2f}"
                    )
                    for idx, candidate in enumerate(component_candidates):
                        required_size = brightest_min_region_size if idx == brightest_index else min_region_size
                        if candidate["region_size"] < required_size:
                            continue
                        results.append(
                            (
                                candidate["region_size"],
                                candidate["mean_final"],
                                candidate["min_final"],
                                candidate["max_final"],
                            )
                        )
                
                # 出力とエントリーへの記入処理
                avg_list = [avg for _, avg, _, _ in results]
                bounds_list = [(min_v, max_v) for _, _, min_v, max_v in results]
                active_slots = get_active_brightness_slots()
                active_slot_count = len(active_slots)
                active_keys = [value_key for value_key, _, _ in active_slots]

                if avg_list:
                    avg_text = ", ".join(f"{v:.2f}" for v in avg_list)
                else:
                    avg_text = "(none)"
                print(f"[DEBUG] swatch detected brightness values: {avg_text}")

                candidate_pixels_raw = roi
                debug_failed_observed_values = {}
                if candidate_pixels_raw.size > 0 and active_slot_count > 0:
                    if active_slot_count == 1:
                        debug_failed_observed_values[active_keys[0]] = float(np.percentile(candidate_pixels_raw, 50))
                    else:
                        for idx, key in enumerate(active_keys):
                            percentile = 100.0 * idx / (active_slot_count - 1)
                            debug_failed_observed_values[key] = float(np.percentile(candidate_pixels_raw, percentile))

                if len(avg_list) < active_slot_count:
                    roi_min = float(np.min(roi))
                    roi_max = float(np.max(roi))
                    roi_mean = float(np.mean(roi))
                    print(
                        f"[DEBUG] swatch failure roi stats: "
                        f"min={roi_min:.2f} max={roi_max:.2f} mean={roi_mean:.2f} "
                        f"detected={len(avg_list)}/{active_slot_count}"
                    )
                insert_to_visible_entries(
                    avg_list,
                    bounds_list,
                    debug_failed_observed_values=debug_failed_observed_values,
                )

                # value_key=="14" 後は、部分設定でも通常モードへ戻す
                if len(avg_list) > 0:
                    root.after_idle(lambda: set_mode_rect("99"))

                # 白基準値は entry_01 優先。空欄時は可視 entry の末尾有効値を使う
                base_brightness = None
                try:
                    base_brightness = float(brightness_entry_01.get())
                except (ValueError, TypeError):
                    active_entries = get_active_brightness_entries()
                    for entry in reversed(active_entries):
                        candidate = entry.get().strip()
                        if not candidate:
                            continue
                        try:
                            base_brightness = float(candidate)
                            break
                        except (ValueError, TypeError):
                            continue

                if base_brightness is not None:
                    white_Value = base_brightness + white_Value2
                    white_flag = True
                    try:
                        white_Press = c2p(white_Value)
                    except ValueError:
                        pass
            value_key = "99"
    
    elif value_key == "99":
        update_detected_value_entries(ave_press, max_press, min_press)
                


# 多角形モードの処理
def calculate_brightness2(polygon_points):
    global scale, image_org_w, image_org_h, canvas_width, canvas_height, image_with_metadata, white_Value, \
        cv_image_2, first_polygon_point, conversion_factor, pixmm_entry, canvas, mm2fontsize, px_count
    
    inv_scale = 1 / scale  # 逆スケール変換
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    img_width, img_height = (int(image_with_metadata.size[0] * scale), int(image_with_metadata.size[1] * scale))

    # ウィンドウ中央補正
    offset_x = int((canvas_width - img_width) / 2)
    offset_y = int((canvas_height - img_height) / 2)

    # ウィンドウ上の座標を元の画像の座標に変換
    scaled_polygon_points = [(int((x - offset_x) * inv_scale), int((y - offset_y) * inv_scale)) for x, y in polygon_points]
    
    # グレースケール変換
    gray_image = cv2.cvtColor(cv_image_2, cv2.COLOR_RGB2GRAY)
    
    # マスク作成（元の画像サイズに合わせる）
    mask = np.zeros((image_org_h, image_org_w), dtype=np.uint8)
    cv2.fillPoly(mask, [np.array(scaled_polygon_points, dtype=np.int32)], 255)
    
    # マスク面積を計算
    pixel_area = np.count_nonzero(mask)
    
    # マスクを適用
    polygon = cv2.bitwise_and(gray_image, gray_image, mask=mask)

    # マスク範囲内の white_Value 以下のピクセルを取得
    valid_pixels = polygon[(mask > 0) & (polygon <= white_Value)]

    ave_press = None
    max_press = None
    min_press = None

    if valid_pixels.size > 0:
        # c2pを適用した値をNumPy配列として作成
        c2p_values = np.array([c2p(p) for p in valid_pixels])
        
        # ブールインデクシングを使用して範囲内の値を抽出
        filtered_values = c2p_values[(c2p_values >= press_Min) & (c2p_values <= press_Max)]
        px_count = filtered_values.size
        
        # 平均を計算
        if filtered_values.size > 0:
            ave_press = np.mean(filtered_values)
            max_press = np.max(filtered_values)
            min_press = np.min(filtered_values)
        else:
            ave_press = None  # 範囲内に値がない場合の処理
        
        
        # 面積の表示
        entry_value = pixmm_entry.get()
        try:
            float_value = float(entry_value)
            area_mm2 = pixel_area * (float_value) ** 2
            px_mm2 = px_count * (float_value) ** 2
            display_text = f"選択範囲面積 {area_mm2:.3f}mm²\n有効測定範囲面積 {px_mm2:.3f}mm²"
        except ValueError:
            display_text = f"選択範囲面積 {pixel_area:.3f}px²\n有効測定範囲面積 {px_count:.3f}px²"
        canvas.delete("text")
        
        first_polygon_point = polygon_points[0]
        x_fpp, y_fpp = first_polygon_point
        canvas.create_text(x_fpp, y_fpp-45, text=display_text, anchor="nw", fill="blue", font=("Arial", mm2fontsize), tags="text")
        
    else:
        # 有効なピクセルがない場合のデフォルト値
        ave_press = c2p(0)
        max_press = ave_press
        min_press = ave_press
    
    
    
    update_detected_value_entries(ave_press, max_press, min_press)


# 円形モードの処理
def calculate_brightness3():
    global center_x, center_y, radius_x, radius_y, scale, image_org_w, image_org_h, \
        canvas_width, canvas_height, image_with_metadata, white_Value, \
        cv_image_2, conversion_factor, top_circle_px, top_circle_py, pixmm_entry, canvas, mm2fontsize, px_count
    
    inv_scale = 1 / scale
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    img_width, img_height = (int(image_with_metadata.size[0] * scale), int(image_with_metadata.size[1] * scale))
    
    offset_x = int((canvas_width - img_width) / 2)
    offset_y = int((canvas_height - img_height) / 2)
    
    # スケール変換後の楕円の中心座標
    cx = int((center_x - offset_x) * inv_scale)
    cy = int((center_y - offset_y) * inv_scale)
    
    # スケール変換後の楕円の半径
    rx = int(radius_x * inv_scale)
    ry = int(radius_y * inv_scale)
    
    gray_image = cv2.cvtColor(cv_image_2, cv2.COLOR_RGB2GRAY)
    mask = np.zeros((image_org_h, image_org_w), dtype=np.uint8)
    
    # 楕円のマスクを作成
    cv2.ellipse(mask, (cx, cy), (rx, ry), 0, 0, 360, 255, -1)
    
    # マスク面積を計算
    pixel_area = np.count_nonzero(mask)
    
    entry_value = pixmm_entry.get()

    
    # マスクを適用して楕円内のピクセルを取得
    ellipse_pixels = cv2.bitwise_and(gray_image, gray_image, mask=mask)
    
    # マスク内の有効なピクセルを抽出
    valid_pixels = ellipse_pixels[(mask > 0) & (ellipse_pixels <= white_Value)]
    
    ave_press = None
    max_press = None
    min_press = None
    px_count = 0

    if valid_pixels.size > 0:
        # c2pを適用した値をNumPy配列として作成
        c2p_values = np.array([c2p(p) for p in valid_pixels])
        
        # ブールインデクシングを使用して範囲内の値を抽出
        filtered_values = c2p_values[(c2p_values >= press_Min) & (c2p_values <= press_Max)]
        
        px_count = filtered_values.size
        
        # 平均を計算
        if filtered_values.size > 0:
            ave_press = np.mean(filtered_values)
            max_press = np.max(filtered_values)
            min_press = np.min(filtered_values)
        else:
            ave_press = None  # 範囲内に値がない場合の処理
             
    else:
        # 有効なピクセルがない場合のデフォルト値
        ave_press = c2p(0)
        max_press = ave_press
        min_press = ave_press
    
    try:
        float_value = float(entry_value)
        area_mm2 = pixel_area * (float_value) ** 2
        px_mm2 = px_count * (float_value) ** 2
        area_text = f"選択範囲面積 {area_mm2:.3f}mm²\n有効測定範囲面積 {px_mm2:.3f}mm²"
    except ValueError:
        area_text = f"選択範囲面積 {pixel_area:.3f}px²\n有効測定範囲面積 {px_count:.3f}px²"
    
    size_text = get_circle_size_display_text()
    display_text = f"{size_text}\n{area_text}"
    
    
    # テキスト表示の更新
    canvas.delete("text")
    canvas.create_text(
        top_circle_px, top_circle_py - 45, 
        text=display_text, 
        anchor="nw", 
        fill="blue", 
        font=("Arial", mm2fontsize), 
        tags="text"
    )
    
    
    
    
    update_detected_value_entries(ave_press, max_press, min_press)


def update_polygon_preview():
    global polygon_points, polygon_id
    canvas.delete("polygon_preview")
    if polygon_id is not None:
        return
    if len(polygon_points) < 2:
        return

    coords = []
    for x, y in polygon_points:
        coords.extend([x, y])
    canvas.create_line(*coords, fill="blue", width=1, tags="polygon_preview")


# 範囲選択モード切替
def set_mode_rect(value):
    global mode, current_value, rect_selected, polygon_points, point_ids, polygon_id, moving_point, dragging
    global dragging_handle, center_x, center_y, radius, circle_id, oval_handles, radius_x, radius_y
    global circle_click_point, circle_dragged
    global polygon_click_point, polygon_dragged
    mode = "rect"
    current_value = value
    rect_selected = True
    canvas.delete("rect","text","line","mark","polygon","circle","point_pressure","polygon_preview")
    polygon_points = []
    point_ids = []
    polygon_id = None
    moving_point = None
    dragging = False
    dragging_handle = None
    center_x = center_y = radius = 0
    circle_id = None
    oval_handles = [None] * 4
    radius_x = radius_y = 0
    circle_click_point = None
    circle_dragged = False
    polygon_click_point = None
    polygon_dragged = False

def set_mode_polygon():
    global mode, rect_selected, rect, polygon_points, point_ids, polygon_id, moving_point, dragging
    global circle_click_point, circle_dragged
    global polygon_click_point, polygon_dragged
    mode = "polygon"
    rect_selected = False
    canvas.delete("mark","line","text","rect","polygon","circle","point_pressure","polygon_preview")
    polygon_points = []
    point_ids = []
    polygon_id = None
    moving_point = None
    dragging = False
    circle_click_point = None
    circle_dragged = False
    polygon_click_point = None
    polygon_dragged = False
    
def set_mode_circle():
    global mode, rect_selected, rect, polygon_points, point_ids, polygon_id, moving_point, dragging,dragging_handle,center_x,center_y,radius,circle_id
    global circle_click_point, circle_dragged
    global polygon_click_point, polygon_dragged
    mode = "circle"
    rect_selected = False
    canvas.delete("mark","line","text","rect","polygon","circle","point_pressure","polygon_preview")
    polygon_points = []
    point_ids = []
    polygon_id = None
    moving_point = None
    dragging = False

    dragging_handle = None
    center_x = center_y = radius = 0
    circle_id = None
    circle_click_point = None
    circle_dragged = False
    polygon_click_point = None
    polygon_dragged = False


def on_mouse_down(event):
    global start_x, start_y, rect, rect_selected, dimension_text, temp_line1, temp_line2, polygon_points, point_ids, polygon_id ,\
        center_x, center_y, radius, dragging_handle, oval_handles, drawing_circle, moving_circle, oval_size, oval_width, radius_x ,\
            radius_y, top_circle_px, top_circle_py, current_value, circle_click_point, circle_dragged, polygon_click_point, polygon_dragged

    if no_image(canvas, root):
        return
    if current_value == "99":
        if not are_all_entries_valid(all_entries, ondo_entry, shitsudo_entry):
            return
    
    if mode == "rect":
        start_x = event.x
        start_y = event.y
        rect_selected = True
        canvas.delete("rect","text","line","mark","point_pressure")
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='blue',width=1, tags="rect")
        if current_value == "99":
            point_press = calculate_point_pressure(start_x, start_y)
            show_point_pressure_text(start_x, start_y, point_press)
        
    elif mode == "polygon":
        if polygon_id:
            polygon_click_point = (event.x, event.y)
            polygon_dragged = False
            return  # すでに確定した多角形がある場合は新しい点を追加しない
        start_x = event.x
        start_y = event.y
        polygon_click_point = None
        polygon_dragged = False
        polygon_points.append((start_x, start_y))
        point_id = canvas.create_oval(start_x - oval_size, start_y - oval_size, start_x + oval_size, start_y + oval_size, width=oval_width, fill="cyan", outline="blue", tags="mark")
        point_ids.append(point_id)
        update_polygon_preview()
        rect_selected = False
        if current_value == "99":
            point_press = calculate_point_pressure(start_x, start_y)
            show_polygon_point_pressure_text(len(polygon_points) - 1, start_x, start_y, point_press)
        
    elif mode == "circle":
        moving_circle = False
        dragging_handle = None
        drawing_circle = False  # 初期化
        circle_dragged = False
        circle_click_point = None
    
        # 既存の楕円がある場合
        if circle_id:
            x0, y0, x1, y1 = canvas.coords(circle_id)
            top_circle_px = x0
            top_circle_py = y0
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2  # 楕円の中心
            r_x = (x1 - x0) / 2  # X方向の半径
            r_y = (y1 - y0) / 2  # Y方向の半径
    
            # 楕円の内部がクリックされた場合、移動モードにする
            if ((event.x - cx) ** 2) / (r_x ** 2) + ((event.y - cy) ** 2) / (r_y ** 2) <= 1:
                moving_circle = True
                start_x, start_y = event.x, event.y
                circle_click_point = (event.x, event.y)
                return
    
            # ハンドルがクリックされたか確認
            for i, handle in enumerate(oval_handles):
                if handle:
                    hx0, hy0, hx1, hy1 = canvas.coords(handle)
                    if hx0 <= event.x <= hx1 and hy0 <= event.y <= hy1:
                        dragging_handle = i
                        return

            # 確定済み円がある状態では、円外クリックで新規作成を開始しない
            if current_value == "99":
                point_press = calculate_point_pressure(event.x, event.y)
                show_point_pressure_text(event.x, event.y, point_press)
            return
        
        # 新しい円の作成（サイズ入力ダイアログ）
        center_x, center_y = event.x, event.y
        radius = 0
        radius_x = radius_y = 0
        unit_label, scaling_factor = get_circle_input_unit()
        input_radius = ask_circle_radius_value(unit_label)
        if input_radius is None:
            return

        if unit_label == "mm" and scaling_factor is not None:
            radius_px = input_radius / scaling_factor
        else:
            radius_px = input_radius

        if radius_px <= 0:
            return

        radius_x = radius_y = float(radius_px)
        drawing_circle = False
        update_circle()
        canvas.delete("point_pressure")
        calculate_brightness3()
        mark_lowest_brightness_points()


def right_click(event):
    global polygon_points, polygon_id, point_ids, radius_x, radius_y, offset_x, offset_y, inv_scale
    if mode == "polygon":
        if len(polygon_points) < 3:
            return  # 3点未満では多角形を作成できない
        
        if polygon_id:
            canvas.delete("rect","text","line","polygon")  # 既存の多角形を削除
        
        canvas.delete("point_pressure","polygon_preview")
        polygon_id = canvas.create_polygon(polygon_points, outline="blue", fill="", width=1, tags="polygon")
        calculate_brightness2(polygon_points)
        mark_lowest_brightness_points()
    elif mode == "circle":
        radius_max = max(radius_x ,radius_y)
        radius_x = radius_max
        radius_y = radius_max
        canvas.delete("point_pressure")
        update_circle()
        calculate_brightness3()
        mark_lowest_brightness_points()
        

def on_mouse_drag(event):
    global polygon_points, polygon_id, moving_point, dragging, start_x, start_y, radius, dragging_handle, rect_selected, \
        moving_circle, circle_id, drawing_circle, center_x, center_y, oval_size, oval_width, radius_x, radius_y, first_polygon_point, circle_dragged
    global polygon_dragged
    
    if mode == "rect" and rect_selected:
        canvas.coords(rect, start_x, start_y, event.x, event.y)
    elif mode == "polygon":
        
        if not polygon_points or polygon_id is None:
            return  # 多角形が存在しない場合は処理を行わない
        
        if moving_point is None:
            # 移動対象の点を探す
            for i, (px, py) in enumerate(polygon_points):
                if abs(px - event.x) < 5 and abs(py - event.y) < 5:
                    moving_point = i
                    break
        
        if moving_point is not None:
            # 指定した点を移動
            prev_x, prev_y = polygon_points[moving_point]
            polygon_points[moving_point] = (event.x, event.y)
            if prev_x != event.x or prev_y != event.y:
                polygon_dragged = True
            canvas.coords(point_ids[moving_point], event.x - oval_size, event.y - oval_size, event.x + oval_size, event.y + oval_size)
        
        else:
            # マウスの位置が多角形の線分上にあるかをチェック
            closest = canvas.find_closest(event.x, event.y)
            if not closest or closest[0] != polygon_id:
                return  # 線分上でない場合は移動しない
            
            # 多角形全体を移動
            if not dragging:
                start_x, start_y = event.x, event.y
                dragging = True
            
            dx, dy = event.x - start_x, event.y - start_y
            if dx != 0 or dy != 0:
                polygon_dragged = True
            polygon_points = [(x + dx, y + dy) for x, y in polygon_points]
            for i, (x, y) in enumerate(polygon_points):
                canvas.coords(point_ids[i], x - oval_size, y - oval_size, x + oval_size, y + oval_size)
            start_x, start_y = event.x, event.y
        
        # 多角形を再描画
        if polygon_id:
            canvas.delete(polygon_id)
        polygon_id = canvas.create_polygon(polygon_points, outline="blue", fill="", width=1, tags="polygon")
        
        first_polygon_point = polygon_points[0]

    elif mode == "circle":
        if drawing_circle:  # 新しい円のサイズ決定
            circle_dragged = True
            radius_x = abs(event.x - center_x)  # x方向の半径
            radius_y = abs(event.y - center_y)  # y方向の半径
            update_circle()

        elif moving_circle:  # 既存の円を移動
            dx = event.x - start_x
            dy = event.y - start_y
            if dx != 0 or dy != 0:
                circle_dragged = True
            center_x += dx
            center_y += dy
            start_x, start_y = event.x, event.y  # 更新
            update_circle()

        elif dragging_handle is not None:  # ハンドルで拡大縮小
            circle_dragged = True
            if circle_id:
                x0, y0, x1, y1 = canvas.coords(circle_id)
                min_size = 2.0

                if dragging_handle == 0:  # 左ハンドル
                    x0 = min(event.x, x1 - min_size)
                elif dragging_handle == 1:  # 右ハンドル
                    x1 = max(event.x, x0 + min_size)
                elif dragging_handle == 2:  # 上ハンドル
                    y0 = min(event.y, y1 - min_size)
                elif dragging_handle == 3:  # 下ハンドル
                    y1 = max(event.y, y0 + min_size)

                center_x = (x0 + x1) / 2
                center_y = (y0 + y1) / 2
                radius_x = (x1 - x0) / 2
                radius_y = (y1 - y0) / 2
                update_circle()


def on_mouse_up(event):
    global rect_selected, start_x, start_y, end_x, end_y, dimension_text, pixmm_entry, scale, moving_point, dragging, dragging_handle, \
        drawing_circle, moving_circle, current_value, polygon_id, px_count, circle_click_point, circle_dragged
    global polygon_click_point, polygon_dragged
    if mode == "rect" and rect_selected:
        end_x, end_y = event.x, event.y
        rect_selected = False

        # 左上と右下の座標を計算
        x1, y1 = min(start_x, end_x), min(start_y, end_y)
        x2, y2 = max(start_x, end_x), max(start_y, end_y)
        # print(x1,x2,y1,y2)

        # ドラッグしていないクリックのみの場合は、点圧表示を維持して終了
        if abs(x2 - x1) <= 1 and abs(y2 - y1) <= 1:
            return

        # 既存の処理を保持
        canvas.delete("point_pressure")
        calculate_brightness(x1, y1, x2, y2, current_value)
        mark_lowest_brightness_points()
        
        # ピクセル面積を計算
        img_width, img_height = image_with_metadata.size
        pixel_width = (x2 - x1)  / scale
        pixel_height = (y2 - y1) / scale
        pixel_area = pixel_width * pixel_height
        if pixmm_entry.get() == "":
            conversion_factor = None
        else:
            conversion_factor = float(pixmm_entry.get())

        # ピクセル面積を表示（換算係数が設定されていない場合）
        if conversion_factor and current_value == "99":
            width_mm = pixel_width * conversion_factor
            height_mm = pixel_height * conversion_factor
            area_mm2 = width_mm * height_mm
            px_mm2 = px_count * (conversion_factor**2)
            display_text = f"選択範囲面積 {area_mm2:.3f}mm²\n有効測定範囲面積 {px_mm2:.3f}mm²"
            dimension_text = canvas.create_text(x1, y1-36, text=display_text, anchor="nw", fill="blue", font=("Arial", mm2fontsize), tags="text")
        elif current_value == "99":
            display_text = f"選択範囲面積 {pixel_area:.3f}px²\n有効測定範囲面積 {px_count:.3f}px²"
            dimension_text = canvas.create_text(x1, y1-36, text=display_text, anchor="nw", fill="blue", font=("Arial", mm2fontsize), tags="text")
        
        if current_value != "99":
            set_mode_rect("99")

        # 寸法情報を描画
    elif mode == "polygon":
        was_polygon_dragged = polygon_dragged
        point_for_click = polygon_click_point
        moving_point = None
        dragging = False
        
        if not polygon_points or polygon_id is None:
            polygon_click_point = None
            polygon_dragged = False
            return  # 多角形が存在しない場合は処理を行わない

        if was_polygon_dragged:
            canvas.delete("point_pressure")
            calculate_brightness2(polygon_points)
            mark_lowest_brightness_points()
        elif current_value == "99" and point_for_click is not None:
            point_x, point_y = point_for_click
            point_press = calculate_point_pressure(point_x, point_y)
            show_point_pressure_text(point_x, point_y, point_press)

        polygon_click_point = None
        polygon_dragged = False
        return
    
    elif mode == "circle":
        was_drawing_circle = drawing_circle
        was_moving_circle = moving_circle
        was_dragging_handle = dragging_handle is not None
        moving_circle = False
        dragging_handle = None

        if was_drawing_circle:
            # ドラッグせずクリックのみのときは点圧表示を維持
            if radius_x <= 0 and radius_y <= 0:
                drawing_circle = False
                circle_click_point = None
                circle_dragged = False
                return

            drawing_circle = False  # 円の描画を確定
            canvas.delete("point_pressure")
            calculate_brightness3()
            mark_lowest_brightness_points()
            circle_click_point = None
            circle_dragged = False
            return

        # 確定済み円のクリック/ドラッグを処理
        if circle_id is not None:
            if was_moving_circle or was_dragging_handle:
                if circle_dragged:
                    canvas.delete("point_pressure")
                    calculate_brightness3()
                    mark_lowest_brightness_points()
                elif current_value == "99" and circle_click_point is not None:
                    point_x, point_y = circle_click_point
                    point_press = calculate_point_pressure(point_x, point_y)
                    show_point_pressure_text(point_x, point_y, point_press)

            drawing_circle = False
            circle_click_point = None
            circle_dragged = False
            return

def update_circle():
    global circle_id, oval_handles, center_x, center_y, radius_x, radius_y, oval_size, oval_width, top_circle_px, top_circle_py
    if circle_id:
        canvas.delete(circle_id)

    # 楕円を描画（xとyの半径を別々に指定）
    circle_id = canvas.create_oval(
        center_x - radius_x, center_y - radius_y, 
        center_x + radius_x, center_y + radius_y,
        outline="blue", width=1, tags="circle"
    )

    # 楕円の四隅の制御点（ハンドル）の座標
    handle_positions = [
        (center_x - radius_x, center_y),  # 左
        (center_x + radius_x, center_y),  # 右
        (center_x, center_y - radius_y),  # 上
        (center_x, center_y + radius_y)   # 下
    ]

    for i, (hx, hy) in enumerate(handle_positions):
        if i >= len(oval_handles) or oval_handles[i] is None or not canvas.find_withtag(oval_handles[i]):
            # 新しく oval を作成
            oval_handles[i] = canvas.create_oval(
                hx - oval_size, hy - oval_size, hx + oval_size, hy + oval_size,
                width=oval_width, fill="cyan", outline="blue", tags="circle"
            )
        else:
            # 既存の oval を移動
            canvas.coords(oval_handles[i], hx - oval_size, hy - oval_size, hx + oval_size, hy + oval_size)
    top_circle_px = center_x
    top_circle_py = center_y - radius_y


label_ken = ttk.Label(button_frame, text="範囲選択形状：", style="Custom.TLabel")
label_ken.grid(row=20, column=0, columnspan=4, padx=(5,0), pady=(10,0), sticky=tk.W)

modevar = tk.IntVar()
button_Region_mode = ttk.Radiobutton(button_frame, text="四角形モード", variable=modevar, value=1, width=24, command=lambda: set_mode_rect("99"))
button_Region_mode.grid(row=21, column=0, columnspan=4, padx=(8,0), pady=(0,0), sticky=tk.W)
button_Polygon_mode = ttk.Radiobutton(button_frame, text="多角形モード", variable=modevar, value=2, width=24, command=lambda: set_mode_polygon())
button_Polygon_mode.grid(row=22, column=0, columnspan=4, padx=(8,0), pady=(0,0), sticky=tk.W)
button_Circle_mode = ttk.Radiobutton(button_frame, text="円形モード", variable=modevar, value=3, width=24, command=lambda: set_mode_circle())
button_Circle_mode.grid(row=23, column=0, columnspan=4, padx=(8,0), pady=(0,0), sticky=tk.W)
button_Region_mode.state(['selected'])


def clear_selectarea():
    global polygon_points, point_ids, polygon_id, moving_point, dragging
    global dragging_handle, center_x, center_y, radius, circle_id, oval_handles, radius_x, radius_y
    global circle_click_point, circle_dragged
    global polygon_click_point, polygon_dragged
    canvas.delete("rect", "text", "line", "mark", "polygon", "circle", "point_pressure", "polygon_preview")
    polygon_points = []
    point_ids = []
    polygon_id = None
    moving_point = None
    dragging = False
    dragging_handle = None
    center_x = center_y = radius = 0
    circle_id = None
    oval_handles = [None] * 4
    radius_x = radius_y = 0
    circle_click_point = None
    circle_dragged = False
    polygon_click_point = None
    polygon_dragged = False
    clear_detected_value_entries()

    if mode == "rect":
        modevar.set(1)
        set_mode_rect("99")
    elif mode == "polygon":
        modevar.set(2)
        set_mode_polygon()
    elif mode == "circle":
        modevar.set(3)
        set_mode_circle()
    else:
        modevar.set(1)
        set_mode_rect("99")


def reset_to_startup_state():
    global polygon_points, point_ids, polygon_id, moving_point, dragging
    global dragging_handle, center_x, center_y, radius, circle_id, oval_handles, radius_x, radius_y
    global circle_click_point, circle_dragged
    global polygon_click_point, polygon_dragged
    global image_with_metadata, cv_image, cv_image_2, image_tk, image_id, image_path, processed_image
    global conversion_factor, original_cv_image, any_dir, photo, source_image_path
    global start_x, start_y, end_x, end_y, line_start, line_end, temp_line1, temp_line2
    global white_Value, white_Press, white_flag, px_count

    # キャンバス上の表示をクリア（画像を含む）
    canvas.delete("image", "rect", "text", "line", "mark", "polygon", "circle", "point_pressure", "polygon_preview")

    # 画像・計算関連の状態を起動直後相当に戻す
    image_with_metadata = None
    cv_image = None
    cv_image_2 = None
    image_tk = None
    image_id = None
    image_path = None
    processed_image = None
    original_cv_image = None
    photo = None
    conversion_factor = None
    any_dir = None
    source_image_path = None
    white_Value = 250
    white_Press = 0
    white_flag = False
    px_count = 0

    # 選択関連の内部状態を初期化
    polygon_points = []
    point_ids = []
    polygon_id = None
    moving_point = None
    dragging = False
    dragging_handle = None
    center_x = center_y = radius = 0
    circle_id = None
    oval_handles = [None] * 4
    radius_x = radius_y = 0
    circle_click_point = None
    circle_dragged = False
    polygon_click_point = None
    polygon_dragged = False

    # 一時座標・描画補助状態を初期化
    start_x = start_y = end_x = end_y = None
    line_start = line_end = None
    temp_line1 = None
    temp_line2 = None

    # 解析条件入力欄をクリア
    for entry in all_entries:
        entry.delete(0, tk.END)
    ondo_entry.delete(0, tk.END)
    shitsudo_entry.delete(0, tk.END)
    pixmm_entry.delete(0, tk.END)
    clear_detected_value_entries()

    # 起動直後のUI状態へ復帰
    set_sheet_type_unselected()
    button_pressrange.config(image=icon3, text='測定範囲可視化：OFF')
    button_pressrange.image = icon3
    apply_threshold_flag.set(False)
    modevar.set(1)
    set_mode_rect("99")


def confirm_reset_window():
    global reset_confirm_open
    if reset_confirm_open:
        return

    reset_confirm_open = True
    try:
        result = messagebox.askokcancel(
            "画面リセット確認",
            "現在の作業状態を初期化して、起動直後の状態に戻します。\nよろしいですか？"
        )
        if result:
            reset_to_startup_state()
    finally:
        reset_confirm_open = False

def has_displayed_image():
    return bool(canvas.find_withtag("image"))

def confirm_image_switch():
    global image_switch_confirm_open
    if image_switch_confirm_open:
        return False

    image_switch_confirm_open = True
    try:
        return messagebox.askokcancel(
            "画像切替確認",
            "現在表示中の画像を新しい画像に切り替えます。よろしいですか？"
        )
    finally:
        image_switch_confirm_open = False

button_clear = ttk.Button(button_frame, text="選択範囲クリア", width=24, command=clear_selectarea)
button_clear.grid(row=24, column=0, columnspan=4, padx=(8,0), pady=(0,0), sticky=tk.W)



# PDF to PNG　ボタン --------------------------------------------------------------------------------------------

def select_pdf_files():
    """ 複数のPDFファイルを選択するダイアログ """
    file_paths = filedialog.askopenfilenames(
        filetypes=[("PDF files", "*.pdf")],
        title="PNGに変換したいPDFを選択してください（複数可）"
    )
    return file_paths

image_path_p2p = None
def save_images_as_png(images, pdf_path, output_folder):
    global image_path_p2p, p2p_size
    # 現在の年月日時分を取得
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    
    base_name = os.path.basename(pdf_path)
    name_without_ext = os.path.splitext(base_name)[0]

    for i, image in enumerate(images):
        # アスペクト比を維持してリサイズ
        max_size = p2p_size
        width, height = image.size
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))

        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # ファイル名を生成
        image_name = f"{name_without_ext}_{timestamp}_page_{i + 1}.png"
        image_path_p2p = os.path.join(output_folder, image_name)
        
        resized_image.save(image_path_p2p, 'PNG')

def pdf_to_png():
    pdf_paths = select_pdf_files()
    global any_path, image_path_p2p, p2p_dpi
    if pdf_paths:
        latest_image_path = None
        for pdf_path in pdf_paths:
            any_path = os.path.dirname(pdf_path)
            
            poppler_path = os.path.join(RESOURCE_dir, 'poppler', 'Library', 'bin')
            if not os.path.isdir(poppler_path):
                fallback_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                poppler_path = os.path.join(fallback_dir, 'poppler', 'Library', 'bin')
            try: # Popplerを明示的に指定してPDFを画像に変換
                images = convert_from_path(pdf_path, dpi=p2p_dpi, poppler_path=poppler_path)
                save_images_as_png(images, pdf_path, any_path)  # PDFファイルと同じ場所に保存する
                # 画像を90度回転
                image = Image.open(image_path_p2p)
                width, height = image.size # 画像の縦横サイズを取得
                if height > width: # 縦長の場合のみ回転処理を行う
                    rotated_image = image.rotate(90, expand=True)
                    rotated_image.save(image_path_p2p)
                latest_image_path = image_path_p2p
                completed_p2p()
            except Exception as e:
                print(f"Error during convert_from_path for {pdf_path}: {e}")
        if latest_image_path:
            original_askopenfilename = filedialog.askopenfilename
            try:
                filedialog.askopenfilename = lambda *args, **kwargs: latest_image_path
                load_image(show_sheettype_guidance=True)
            finally:
                filedialog.askopenfilename = original_askopenfilename
    else:
        print("PDFファイルが選択されませんでした")


#ボタン設置
def on_enter_p2p(event):
    button_p2p.config(image=icon2)
def on_leave_p2p(event):
    button_p2p.config(image=icon1)

# 画像の読み込みとリサイズ
icon1 = tk.PhotoImage(file=os.path.join(ima_path, "p2p_off.png"))  # 画像のリサイズ
icon2 = tk.PhotoImage(file=os.path.join(ima_path, "p2p_on.png"))  # 画像のリサイズ

label_junbi = ttk.Label(button_frame, text="画像準備：", style="Custom.TLabel")
label_junbi.grid(row=0, column=0, columnspan=4, padx=(5,0), pady=(0,0), sticky=tk.W)

# ボタン作成
button_p2p = ttk.Button(
    button_frame,
    image=icon1,
    text='PDF⇒PNG変換',
    compound=tk.LEFT,
    command=pdf_to_png,
    padding=[5, 0, 25, 0]
)

button_p2p.image = icon1
button_p2p.grid(row=1, column=0, columnspan=4, padx=(8, 0), pady=(10, 0), sticky=tk.W)
button_p2p.bind("<Enter>", on_enter_p2p)
button_p2p.bind("<Leave>", on_leave_p2p)



# PNGを開く　ボタン --------------------------------------------------------------------------------------------

# 画像を読み込む処理
def load_image(show_sheettype_guidance=False):
    global image_with_metadata, cv_image, cv_image_2, image_tk, image_id, image_path, original_cv_image, selected_var, \
        conversion_factor, atai_ave_entry, image_org_w, image_org_h, processed_image, any_dir, white_Value, white_Press, white_flag, white_Value2, source_image_path, suppress_sheet_type_reset
    
    # ファイル選択ダイアログを開き、PR_dir フォルダを初期ディレクトリに設定
    if any_dir:
        file_path = filedialog.askopenfilename(
            initialdir=any_dir,  # PR_dataフォルダを最初に表示
            filetypes=[("PNG files", "*.png")],
            title="PNGファイルを選択してください"
        )
    else:
        file_path = filedialog.askopenfilename(
            filetypes=[("PNG files", "*.png")],
            title="PNGファイルを選択してください"
        )
    
    if file_path and has_displayed_image() and not confirm_image_switch():
        return

    if file_path:
        # 選択したファイルをカレントディレクトリにコピー
        os.makedirs(tmp_dir, exist_ok=True)
        image_name = os.path.basename(file_path)
        name_root, ext = os.path.splitext(image_name)
        temp_file_name = f"{name_root}_{uuid.uuid4().hex}{ext}"
        image_path = os.path.join(tmp_dir, temp_file_name)
        shutil.copy(file_path, image_path)
        any_dir = os.path.dirname(file_path)
        source_image_path = file_path
        
        # 画像の読み込み
        #cv_image = cv2.imread(image_path) #26/03/27 日本語ファイル名対応------------------
        with open(image_path, "rb") as f:
            data = f.read()
        
        cv_image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        #------------------
        
        cv_image_2 = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        original_cv_image = cv_image_2.copy()
        image = Image.fromarray(cv_image_2)
        image_tk = ImageTk.PhotoImage(image)
        
        # Clear previous image if exists
        #2026/3/27 PNGファイルデフォルト表示対応
        #if image_id is not None:
        #    canvas.delete(image_id)
        #image_id = canvas.create_image(0, 0, anchor=tk.NW, image=image_tk, tags="image")
        
        # 画像を開く
        image_with_metadata = Image.open(image_path)  # PR_dirにコピーしたファイルを使用
        image_org_w, image_org_h = image_with_metadata.size
        # update_canvas_image()
        processed_image = image_with_metadata.copy()
        
        
        # 2026/3/27 PNGファイルの画像表示のデフォルト表示サイズ修正
        #update_canvas_image()
        # ★ 画像読み込み後、強制的に1回だけ再描画
        canvas.update_idletasks()
        update_canvas_image()
        
        # entryをクリア
        brightness_entry_15.delete(0, 'end')
        brightness_entry_13.delete(0, 'end')
        brightness_entry_11.delete(0, 'end')
        brightness_entry_10.delete(0, 'end')
        brightness_entry_09.delete(0, 'end')
        brightness_entry_08.delete(0, 'end')
        brightness_entry_07.delete(0, 'end')
        brightness_entry_06.delete(0, 'end')
        brightness_entry_05.delete(0, 'end')
        brightness_entry_04.delete(0, 'end')
        brightness_entry_03.delete(0, 'end')
        brightness_entry_02.delete(0, 'end')
        brightness_entry_01.delete(0, 'end')
        ondo_entry.delete(0, 'end')
        shitsudo_entry.delete(0, 'end')
        pixmm_entry.delete(0, 'end')
        clear_detected_value_entries()
        
        
        # メタデータを読み取る
        metadata_read = image_with_metadata.info
        data_string_read = metadata_read.get("info", "")
        conversion_factor = None
            
        # データを解析して元の値を取得する
        if (
            data_string_read.startswith("press{") and 
            data_string_read.endswith("}") and 
            len(data_string_read.strip("press{}").split(",")) == 17
        ):
            
            
            entries = data_string_read[6:-1].split(',')
            sheet_Type,color_15,color_13,color_11,color_10,color_09,color_08,color_07,color_06,color_05,color_04,color_03,color_02,color_01,png_ondo,png_shitsudo,png_pixmm = entries
        
            # 各エントリウィジェットに値を設定
            brightness_entry_15.delete(0, 'end')
            brightness_entry_15.insert(0, color_15)
            brightness_entry_13.delete(0, 'end')
            brightness_entry_13.insert(0, color_13)
            brightness_entry_11.delete(0, 'end')
            brightness_entry_11.insert(0, color_11)
            brightness_entry_10.delete(0, 'end')
            brightness_entry_10.insert(0, color_10)
            brightness_entry_09.delete(0, 'end')
            brightness_entry_09.insert(0, color_09)
            brightness_entry_08.delete(0, 'end')
            brightness_entry_08.insert(0, color_08)
            brightness_entry_07.delete(0, 'end')
            brightness_entry_07.insert(0, color_07)
            brightness_entry_06.delete(0, 'end')
            brightness_entry_06.insert(0, color_06)
            brightness_entry_05.delete(0, 'end')
            brightness_entry_05.insert(0, color_05)
            brightness_entry_04.delete(0, 'end')
            brightness_entry_04.insert(0, color_04)
            brightness_entry_03.delete(0, 'end')
            brightness_entry_03.insert(0, color_03)
            brightness_entry_02.delete(0, 'end')
            brightness_entry_02.insert(0, color_02)
            brightness_entry_01.delete(0, 'end')
            brightness_entry_01.insert(0, color_01)
            ondo_entry.delete(0, 'end')
            ondo_entry.insert(0, png_ondo)
            shitsudo_entry.delete(0, 'end')
            shitsudo_entry.insert(0, png_shitsudo)
            pixmm_entry.delete(0, 'end')
            pixmm_entry.insert(0, png_pixmm)
            if png_pixmm != "":
                conversion_factor = float(png_pixmm)
            
            sheet_type_applied = False
            suppress_sheet_type_reset = True
            try:
                if sheet_Type == "HHS":
                   selected_var.set("HHS")
                   sheet_type_applied = True
                elif sheet_Type == "HS 持続圧":
                   selected_var.set("HS 持続圧")
                   sheet_type_applied = True
                elif sheet_Type == "HS 瞬間圧":
                   selected_var.set("HS 瞬間圧")
                   sheet_type_applied = True
                elif sheet_Type == "MS 持続圧":
                   selected_var.set("MS 持続圧")
                   sheet_type_applied = True
                elif sheet_Type == "MS 瞬間圧":
                   selected_var.set("MS 瞬間圧")
                   sheet_type_applied = True
                elif sheet_Type == "LW 持続圧":
                   selected_var.set("LW 持続圧")
                   sheet_type_applied = True
                elif sheet_Type == "LW 瞬間圧":
                   selected_var.set("LW 瞬間圧")
                   sheet_type_applied = True
                elif sheet_Type == "LLW 持続圧":
                   selected_var.set("LLW 持続圧")
                   sheet_type_applied = True
                elif sheet_Type == "LLW 瞬間圧":
                   selected_var.set("LLW 瞬間圧")
                   sheet_type_applied = True
                elif sheet_Type == "3LW 持続圧":
                   selected_var.set("3LW 持続圧")
                   sheet_type_applied = True
                elif sheet_Type == "3LW 瞬間圧":
                   selected_var.set("3LW 瞬間圧")
                   sheet_type_applied = True
                elif sheet_Type == "4LW 持続圧":
                   selected_var.set("4LW 持続圧")
                   sheet_type_applied = True
                elif sheet_Type == "4LW 瞬間圧":
                   selected_var.set("4LW 瞬間圧")
                   sheet_type_applied = True
                elif sheet_Type == "5LW 持続圧":
                   selected_var.set("5LW 持続圧")
                   sheet_type_applied = True
                elif sheet_Type == "5LW 瞬間圧":
                   selected_var.set("5LW 瞬間圧")
                   sheet_type_applied = True
            finally:
                suppress_sheet_type_reset = False
            if not sheet_type_applied:
                set_sheet_type_unselected()
        else:
            print("メタデータが見つかりません。")
            set_sheet_type_unselected()
        
        pressrange_off()
        apply_threshold_flag.set(False)
        conversion_factor = None
        
        brightness_01 = brightness_entry_01.get().strip()
        if brightness_01 != "":
            white_Value = float(brightness_01) + white_Value2
            white_flag = True
            white_Press = c2p(white_Value)
        else:
            # メタデータなし画像でも読み込み完了できるようにする
            white_Value = 250
            white_Press = 0
            white_flag = False
        
        # 2026/3/27 PNGファイルの画像表示のデフォルト表示サイズ修正
        #update_canvas_image()
        # ★ 画像読み込み後、強制的に1回だけ再描画
        canvas.update_idletasks()
        update_canvas_image()

        if show_sheettype_guidance:
            set_sheet_type_unselected()
            comment_label = tk.Label(
                root,
                text=" 感圧紙の種類をリストから選択してください ",
                fg="white",
                bg="#c942a5",
                font=("Meiryo ui", 16, "bold"),
            )
            comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            root.after(8000, comment_label.destroy)

    else:
        print("No file selected")


def resize_image(event=None):
    """ ウィンドウサイズ変更時に画像をリサイズ """
    if image_with_metadata:
        update_canvas_image()


# ボタン設置
def on_enter_hiraku(event):
    button_hiraku.config(image=icon6)
def on_leave_hiraku(event):
    button_hiraku.config(image=icon5)

icon5 = tk.PhotoImage(file=os.path.join(ima_path, "folder_off.png"))  # 画像のリサイズ
icon6 = tk.PhotoImage(file=os.path.join(ima_path, "folder_on.png"))  # 画像のリサイズ

button_hiraku = ttk.Button(
    button_frame,
    image=icon5,
    text='PNGを開く',
    compound=tk.LEFT,
    command=load_image,
    padding=[0, 0, 45, 0] # 左, 上, 右, 下
)

button_hiraku.image = icon5
button_hiraku.grid(row=2, column=0, columnspan=4, padx=(8, 0), pady=(0, 0), sticky=tk.W)
button_hiraku.bind("<Enter>", on_enter_hiraku)
button_hiraku.bind("<Leave>", on_leave_hiraku)




# xl保存　ボタン --------------------------------------------------------------------------------------------

def save_brightness_to_xlsx(): #26/04/16 関数名変更
    global start_x, start_y, end_x, end_y, canvas_width,canvas_height,cv_image_2, conversion_factor, press_Max, press_Min
    global mode, polygon_points, polygon_id, center_x, center_y, radius_x, radius_y, image_org_h, image_org_w

    if no_image(canvas, root):
        return
    if is_sheet_type_unselected():
        comment_label = tk.Label(root, text=" 感圧紙の種類をリストから選択してください ",
                                 fg="white", bg="#c942a5", font=("Meiryo ui", 16, "bold"))
        comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        root.after(2000, comment_label.destroy)
        return
    if no_selection_for_export(canvas, root):
        return

    pixmm_value = pixmm_entry.get().strip()
    try:
        conversion_factor = float(pixmm_value)
        if conversion_factor <= 0:
            raise ValueError
    except (ValueError, TypeError):
        comment_label = tk.Label(root, text=" スケーリングボタンでスケール(画像の寸法)を設定してください ",
                                 fg="white", bg="#c942a5", font=("Meiryo ui", 16, "bold"))
        comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        root.after(2000, comment_label.destroy)
        return
    
    inv_scale = 1 / scale  # 逆スケール変換
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    img_width, img_height = (int(image_with_metadata.size[0] * scale),
                             int(image_with_metadata.size[1] * scale))
    offset_x = int((canvas_width - img_width) / 2)
    offset_y = int((canvas_height - img_height) / 2)

    gray_image = cv2.cvtColor(cv_image_2, cv2.COLOR_RGB2GRAY)

    if mode == "rect":
        start_x2 = int(start_x - offset_x)
        start_y2 = int(start_y - offset_y)
        end_x2 = int(end_x - offset_x)
        end_y2 = int(end_y - offset_y)

        x1 = max(0, min(start_x2, end_x2))
        y1 = max(0, min(start_y2, end_y2))
        x2 = min(img_width, max(start_x2, end_x2))
        y2 = min(img_height, max(start_y2, end_y2))

        start_x3 = max(0, int(x1 * inv_scale))
        start_y3 = max(0, int(y1 * inv_scale))
        end_x3 = min(image_org_w, int(x2 * inv_scale))
        end_y3 = min(image_org_h, int(y2 * inv_scale))

        if end_x3 <= start_x3 or end_y3 <= start_y3:
            comment_label = tk.Label(root, text=" 選択範囲を作成してください ",
                                     fg="white", bg="#c942a5", font=("Meiryo ui", 16, "bold"))
            comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            root.after(2000, comment_label.destroy)
            return

        gray_region = gray_image[start_y3:end_y3, start_x3:end_x3]
        mask_region = np.ones(gray_region.shape, dtype=bool)

    elif mode == "polygon":
        scaled_polygon_points = [
            (int((x - offset_x) * inv_scale), int((y - offset_y) * inv_scale))
            for x, y in polygon_points
        ]
        mask_full = np.zeros((image_org_h, image_org_w), dtype=np.uint8)
        cv2.fillPoly(mask_full, [np.array(scaled_polygon_points, dtype=np.int32)], 255)
        ys, xs = np.where(mask_full > 0)
        if xs.size == 0 or ys.size == 0:
            comment_label = tk.Label(root, text=" 選択範囲を作成してください ",
                                     fg="white", bg="#c942a5", font=("Meiryo ui", 16, "bold"))
            comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            root.after(2000, comment_label.destroy)
            return
        min_x, max_x = int(xs.min()), int(xs.max()) + 1
        min_y, max_y = int(ys.min()), int(ys.max()) + 1
        gray_region = gray_image[min_y:max_y, min_x:max_x]
        mask_region = mask_full[min_y:max_y, min_x:max_x] > 0

    elif mode == "circle":
        cx = int((center_x - offset_x) * inv_scale)
        cy = int((center_y - offset_y) * inv_scale)
        rx = max(1, int(radius_x * inv_scale))
        ry = max(1, int(radius_y * inv_scale))
        mask_full = np.zeros((image_org_h, image_org_w), dtype=np.uint8)
        cv2.ellipse(mask_full, (cx, cy), (rx, ry), 0, 0, 360, 255, -1)
        ys, xs = np.where(mask_full > 0)
        if xs.size == 0 or ys.size == 0:
            comment_label = tk.Label(root, text=" 選択範囲を作成してください ",
                                     fg="white", bg="#c942a5", font=("Meiryo ui", 16, "bold"))
            comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            root.after(2000, comment_label.destroy)
            return
        min_x, max_x = int(xs.min()), int(xs.max()) + 1
        min_y, max_y = int(ys.min()), int(ys.max()) + 1
        gray_region = gray_image[min_y:max_y, min_x:max_x]
        mask_region = mask_full[min_y:max_y, min_x:max_x] > 0
    else:
        comment_label = tk.Label(root, text=" 選択範囲を作成してください ",
                                 fg="white", bg="#c942a5", font=("Meiryo ui", 16, "bold"))
        comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        root.after(2000, comment_label.destroy)
        return


    # csv保存時の数値設定
    # 変換後のデータを初期化（空欄にする）
    converted_region = np.full_like(gray_region, None, dtype=object)
    
    # 変換処理
    for y in range(gray_region.shape[0]):
        for x in range(gray_region.shape[1]):
            if not mask_region[y, x]:
                converted_region[y, x] = None
                continue
            brightness = gray_region[y, x]
            converted_brightness = c2p(brightness)
            if converted_brightness >= press_Min and converted_brightness <= press_Max:
                converted_region[y, x] = np.round(converted_brightness, 9)  # 小数点以下9桁に丸める
            elif converted_brightness > press_Max:
                converted_region[y, x] =  999
            elif converted_brightness < press_Min and converted_brightness > white_Press:
                converted_region[y, x] =  -999
            else:
                converted_region[y, x] = None  # 空欄を表すためにNoneを設定
        
    height, width = converted_region.shape
    
    
    # 現在の日時を取得し、"yyyymmdd_hhmmss" 形式にフォーマット
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    
    initialfile = f"1cell：{conversion_factor}mm___{current_time}.xlsx"  # ここでデフォルトのファイル名を設定 26/04/16 xlsxファイル名
    
    # 拡張子を分離
    filename, ext = os.path.splitext(initialfile)
    # 拡張子以外の部分の . を全角の ． に変換
    filename = filename.replace(".", "．")
    # 変換後のファイル名を組み立てる
    initialfile = filename + ext
    
    #26/04/16 csv出力からxlsxファイルへ変更
    # # Prompt the user to select a file location to save the CSV
    # file_path = filedialog.asksaveasfilename(
    #     defaultextension=".csv",
    #     filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
    #     initialfile = initialfile
    # )
    
    
    # if not file_path:
    #     return  # User canceled the save dialog

    # with open(file_path, mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #     for row in converted_region:
    #         writer.writerow(row)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile=initialfile
    )
    
    if not file_path:
        return
    
    # ===============================
    # Excel (xlsx) 出力処理
    # ===============================
    wb = Workbook()
    ws = wb.active
    ws.title = "data"
    
    row_count = 0
    col_count = 0
    
    # converted_region をそのまま Excel に書き込む
    for r, row in enumerate(converted_region, start=1):
        row_count = r
        for c, value in enumerate(row, start=1):
            col_count = max(col_count, c)
    
            # None は空欄に
            if value is None:
                ws.cell(row=r, column=c, value=None)
            else:
                ws.cell(row=r, column=c, value=value)
    
    # ===============================
    # セルを正方形にする設定
    # ===============================
    cell_width = 3.0                 # 列幅（必要に応じて微調整）
    cell_height = cell_width * 7.5   # 行高さ（経験則）
    
    # 列幅
    for c in range(1, col_count + 1):
        ws.column_dimensions[get_column_letter(c)].width = cell_width
    
    # 行高さ
    for r in range(1, row_count + 1):
        ws.row_dimensions[r].height = cell_height

    # ===============================
    # 条件付き書式（緑・黄・赤カラースケール）
    # ===============================
    if row_count > 0 and col_count > 0:
        end_col = get_column_letter(col_count)
        data_range = f"A1:{end_col}{row_count}"
        color_scale_rule = ColorScaleRule(
            start_type="min",
            start_color="00B050",  # 緑
            mid_type="percentile",
            mid_value=50,
            mid_color="FFFF00",    # 黄
            end_type="max",
            end_color="FF0000"     # 赤
        )
        ws.conditional_formatting.add(data_range, color_scale_rule)

    # ===============================
    # 初期ズームを出力範囲に合わせて自動調整
    # （100%時に 16行 x 56列 が見える実測基準）
    # ===============================
    if row_count > 0 and col_count > 0:
        def calculate_excel_zoom_scale(target_rows, target_cols):
            # 100%表示時の実測値（基準）
            baseline_visible_rows = 16.0
            baseline_visible_cols = 56.0
            fit_margin = 0.95

            # 安全クランプ範囲
            min_zoom = 10.0
            max_zoom = 400.0

            zoom_h = 100.0 * baseline_visible_rows / max(1.0, float(target_rows))
            zoom_w = 100.0 * baseline_visible_cols / max(1.0, float(target_cols))
            raw_zoom = min(zoom_w, zoom_h) * fit_margin
            return int(max(min_zoom, min(max_zoom, raw_zoom)))

        ws.sheet_view.zoomScale = calculate_excel_zoom_scale(row_count, col_count)
    
    try:
        wb.save(file_path)
        comment_label = tk.Label(
            root,
            text=" Excelファイルを出力しました ",
            fg="white",
            bg="#c942a5",
            font=("Meiryo ui", 16, "bold")
        )
        comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        root.after(2000, comment_label.destroy)
    except Exception:
        comment_label = tk.Label(
            root,
            text=" Excelファイルの出力に失敗しました ",
            fg="white",
            bg="#c942a5",
            font=("Meiryo ui", 16, "bold")
        )
        comment_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        root.after(2000, comment_label.destroy)

#ボタン設置
def on_enter_xl(event):
    button_xl.config(image=icon10)
def on_leave_xl(event):
    button_xl.config(image=icon9)

# 画像の読み込みとリサイズ
icon9 = tk.PhotoImage(file=os.path.join(ima_path, "xl_off.png"))  # 画像のリサイズ
icon10 = tk.PhotoImage(file=os.path.join(ima_path, "xl_on.png"))  # 画像のリサイズ

# ボタン作成
button_xl = ttk.Button(
    button_frame,
    image=icon9,
    text='選択範囲Excel出力',
    compound=tk.LEFT,
    command=save_brightness_to_xlsx, #関数名変更
    padding=[7, 0, 5, 0]
)

label_syuturyoku = ttk.Label(button_frame, text="出力：", style="Custom.TLabel")
label_syuturyoku.grid(row=31, column=0, columnspan=4, padx=(5,0), pady=(8,0), sticky=tk.W)

button_xl.image = icon9
button_xl.grid(row=32, column=0, columnspan=4, padx=(8, 0), pady=(0, 0), sticky=tk.W)
button_xl.bind("<Enter>", on_enter_xl)
button_xl.bind("<Leave>", on_leave_xl)


# metaデータコピー　ボタン --------------------------------------------------------------------------------------------

def metaコピ():
    src_path = filedialog.askopenfilename(title="解析条件のコピー元PNGを選択してください", filetypes=[("PNG files", "*.png")])
    if not src_path:
        return
    
    # ② 画像を開いてメタデータを取得
    with Image.open(src_path) as src_img:
        if not isinstance(src_img.info, dict):
            messagebox.showwarning("エラー", "コピー元PNGのメタデータを読み取れませんでした。")
            return
        metadata = src_img.info.copy()  # メタデータをコピー
    
    # ③ 複数の画像を選択
    target_paths = filedialog.askopenfilenames(title="解析条件のコピー先PNGを選択してください（複数可）", filetypes=[("PNG files", "*.png")])
    if not target_paths:
        return
    
    # ④ 各画像に対してメタデータを上書き保存
    for path in target_paths:
        with Image.open(path) as im:
            pnginfo = PngImagePlugin.PngInfo()
            for k, v in metadata.items():
                if isinstance(v, str):
                    pnginfo.add_text(k, v)
    
            save_path = path  # 上書き保存
            im.save(save_path, pnginfo=pnginfo)
    
    
# ボタン設置
def on_enter_metacopy(event):
    button_metacopy.config(image=icon12)
def on_leave_metacopy(event):
    button_metacopy.config(image=icon11)

# 画像の読み込みとリサイズ
icon11 = tk.PhotoImage(file=os.path.join(ima_path, "metacopy_off.png"))  # 画像のリサイズ
icon12 = tk.PhotoImage(file=os.path.join(ima_path, "metacopy_on.png"))  # 画像のリサイズ

# ボタン作成
button_metacopy = ttk.Button(
    button_frame,
    image=icon11,
    text='解析条件をコピー',
    compound=tk.LEFT,
    command=metaコピ,
    padding=[7, 0, 22, 0]
)

button_metacopy.image = icon11
button_metacopy.grid(row=19, column=0, columnspan=4, padx=(8, 0), pady=(0, 0), sticky=tk.W)
button_metacopy.bind("<Enter>", on_enter_metacopy)
button_metacopy.bind("<Leave>", on_leave_metacopy)
update_entries_and_buttons()

# 画面リセット ボタン --------------------------------------------------------------------------------------------

def on_enter_reset_window(event):
    button_reset_window.config(image=icon16)

def on_leave_reset_window(event):
    button_reset_window.config(image=icon15)

icon15 = tk.PhotoImage(file=os.path.join(ima_path, "reset_window.png"))
icon16 = tk.PhotoImage(file=os.path.join(ima_path, "reset_window.png"))

button_reset_window = ttk.Button(
    button_frame,
    image=icon15,
    text='画面リセット',
    compound=tk.LEFT,
    command=confirm_reset_window,
    padding=[7, 0, 22, 0]
)

label_clear_input = ttk.Label(button_frame, text="入力内容クリア：", style="Custom.TLabel")
label_clear_input.grid(row=33, column=0, columnspan=4, padx=(5,0), pady=(10,0), sticky=tk.W)

button_reset_window.image = icon15
button_reset_window.grid(row=34, column=0, columnspan=4, padx=(8, 0), pady=(0, 0), sticky=tk.W)
button_reset_window.bind("<Enter>", on_enter_reset_window)
button_reset_window.bind("<Leave>", on_leave_reset_window)

def show_contact_info():
    global contact_info_window

    if contact_info_window is not None and contact_info_window.winfo_exists():
        contact_info_window.lift()
        contact_info_window.focus_force()
        return

    app_mail = "masashi_nagasaka_zd@mail.toyota.co.jp"
    consultation_mail = "kota_suzuki_ab@mail.toyota.co.jp"

    contact_info_window = tk.Toplevel(root)
    contact_info_window.title("問い合わせ先")
    contact_info_window.configure(bg="#f4f7fb")
    contact_info_window.resizable(False, False)
    contact_info_window.transient(root)

    dialog_width = int(760 * (screen_height / 1080))
    dialog_height = int(470 * (screen_height / 1080))
    window_x = root.winfo_rootx() + max(0, (root.winfo_width() - dialog_width) // 2)
    window_y = root.winfo_rooty() + max(0, (root.winfo_height() - dialog_height) // 2)
    contact_info_window.geometry(f"{dialog_width}x{dialog_height}+{window_x}+{window_y}")

    def close_contact_window():
        global contact_info_window
        if contact_info_window is not None and contact_info_window.winfo_exists():
            contact_info_window.destroy()
        contact_info_window = None

    def copy_mail_to_clipboard(mail_text):
        root.clipboard_clear()
        root.clipboard_append(mail_text)
        root.update()
        messagebox.showinfo("コピー完了", f"{mail_text}\nをコピーしました。", parent=contact_info_window)

    header_label = tk.Label(
        contact_info_window,
        text="問い合わせ先",
        bg="#1f3a5f",
        fg="#ffffff",
        font=("Meiryo ui", 14, "bold"),
        anchor="w",
        padx=12,
    )
    header_label.pack(fill=tk.X, pady=(0, 10))

    body_frame = tk.Frame(contact_info_window, bg="#f4f7fb")
    body_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 8))

    content_frame = tk.Frame(body_frame, bg="#ffffff", relief="solid", borderwidth=1)
    content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

    inner_frame = tk.Frame(content_frame, bg="#ffffff")
    inner_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    title_label = tk.Label(
        inner_frame,
        text="■アプリ問い合わせ先",
        bg="#ffffff",
        fg="#1f2d3d",
        font=("Meiryo ui", 11, "bold"),
        anchor="w",
    )
    title_label.pack(fill=tk.X)

    subtitle_label = tk.Label(
        inner_frame,
        text="メールまたはTeamsにてご連絡下さい。",
        bg="#ffffff",
        fg="#1f2d3d",
        font=("Meiryo ui", 11),
        anchor="w",
    )
    subtitle_label.pack(fill=tk.X, pady=(2, 10))

    app_block = tk.Frame(inner_frame, bg="#ffffff")
    app_block.pack(fill=tk.X, pady=(0, 10))

    app_dept_label = tk.Label(
        app_block,
        text="計測・デジタル基盤改革部",
        bg="#ffffff",
        fg="#1f2d3d",
        font=("Meiryo ui", 11),
        anchor="w",
    )
    app_dept_label.grid(row=0, column=0, columnspan=2, sticky="w")

    app_kind_label = tk.Label(
        app_block,
        text="アプリについて",
        bg="#ffffff",
        fg="#1f2d3d",
        font=("Meiryo ui", 11),
        anchor="w",
    )
    app_kind_label.grid(row=1, column=0, columnspan=2, sticky="w")

    app_person_label = tk.Label(
        app_block,
        text="　電動化デジタル開発室 Nagasaka, Masashi/長坂 政史",
        bg="#ffffff",
        fg="#1f2d3d",
        font=("Meiryo ui", 11),
        anchor="w",
    )
    app_person_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 2))

    app_mail_label = tk.Label(
        app_block,
        text=f"　mail：{app_mail}",
        bg="#ffffff",
        fg="#1f2d3d",
        font=("Meiryo ui", 11),
        anchor="w",
    )
    app_mail_label.grid(row=3, column=0, sticky="w")
    app_copy_button = ttk.Button(
        app_block,
        text="コピー",
        width=8,
        command=lambda: copy_mail_to_clipboard(app_mail),
    )
    app_copy_button.grid(row=3, column=1, sticky="w", padx=(8, 0))

    consultation_block = tk.Frame(inner_frame, bg="#ffffff")
    consultation_block.pack(fill=tk.X)

    consultation_title_label = tk.Label(
        consultation_block,
        text="計測相談・依頼",
        bg="#ffffff",
        fg="#1f2d3d",
        font=("Meiryo ui", 11),
        anchor="w",
    )
    consultation_title_label.grid(row=0, column=0, columnspan=2, sticky="w")

    consultation_person_label = tk.Label(
        consultation_block,
        text="　計測・デジタル課 Suzuki, Kota/鈴木 宏太",
        bg="#ffffff",
        fg="#1f2d3d",
        font=("Meiryo ui", 11),
        anchor="w",
    )
    consultation_person_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 2))

    consultation_mail_label = tk.Label(
        consultation_block,
        text=f"　mail：{consultation_mail}",
        bg="#ffffff",
        fg="#1f2d3d",
        font=("Meiryo ui", 11),
        anchor="w",
    )
    consultation_mail_label.grid(row=2, column=0, sticky="w")
    consultation_copy_button = ttk.Button(
        consultation_block,
        text="コピー",
        width=8,
        command=lambda: copy_mail_to_clipboard(consultation_mail),
    )
    consultation_copy_button.grid(row=2, column=1, sticky="w", padx=(8, 0))

    close_button = ttk.Button(body_frame, text="閉じる", width=10, command=close_contact_window)
    close_button.pack(anchor="e", pady=(14, 0))

    contact_info_window.protocol("WM_DELETE_WINDOW", close_contact_window)
    contact_info_window.focus_force()


label_contact = ttk.Label(button_frame, text="お問い合わせ：", style="Custom.TLabel")
label_contact.grid(row=35, column=0, columnspan=4, padx=(5, 0), pady=(10, 0), sticky=tk.W)

button_contact = ttk.Button(button_frame, text="問い合わせ先", command=show_contact_info)
button_contact.grid(row=36, column=0, columnspan=4, padx=(8, 0), pady=(0, 0), sticky=tk.W)

# 「解析条件をコピー」は自然幅のまま維持し、
# 「画面リセット」は実表示幅で合わせる。
# さらに「問い合わせ先」は「画面リセット」と同じ実表示幅に合わせる。
def sync_reset_button_width_to_metacopy():
    root.update_idletasks()

    metacopy_width = button_metacopy.winfo_reqwidth()
    reset_width = button_reset_window.winfo_reqwidth()

    left_pad = 7
    top_pad = 0
    bottom_pad = 0
    base_right_pad = 22
    extra_right_pad = max(0, metacopy_width - reset_width)

    button_reset_window.configure(
        padding=[left_pad, top_pad, base_right_pad + extra_right_pad, bottom_pad]
    )

    root.update_idletasks()
    reset_aligned_width = button_reset_window.winfo_reqwidth()
    contact_width = button_contact.winfo_reqwidth()
    contact_extra_right_pad = max(0, reset_aligned_width - contact_width)
    contact_extra_left_pad = contact_extra_right_pad // 2
    contact_extra_right_pad = contact_extra_right_pad - contact_extra_left_pad
    button_contact.configure(padding=[contact_extra_left_pad, 0, contact_extra_right_pad, 0])


root.after_idle(sync_reset_button_width_to_metacopy)


# ボタンフレーム******************************************************************************************************************************************************************

canvas.bind("<ButtonPress-1>", on_mouse_down)
canvas.bind("<B1-Motion>", on_mouse_drag)
canvas.bind("<ButtonRelease-1>", on_mouse_up)

canvas.bind("<Button-3>", right_click)

rect = None
start_x = start_y = None
current_value = None
marks = []

dragging_handle = None
center_x = center_y = radius = 0
circle_id = None
oval_handles = [None] * 4

radius_x = radius_y = 0
circle_click_point = None
circle_dragged = False
polygon_click_point = None
polygon_dragged = False

mode = "rect"
rect_selected = True
clear_detected_value_entries()
set_mode_rect("99")

canvas.bind("<Configure>", resize_image)


def on_app_close():
    cleanup_temp_pngs()
    schedule_cleanup_tmp_dir_after_exit()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_app_close)

root.mainloop()
