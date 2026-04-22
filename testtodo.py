# Updated Streamlit Weekly Planning Dashboard
# Added:
# 1) 待讀書單（不隨週次變動，可新增/刪除）
# 2) 睡眠紀錄表
# 3) Habit Tracker
#
# 說明：
# - 讀書單、睡眠、habit 都獨立存成自己的 csv，不會跟 weekly task 一起被週次切換影響
# - 我把它們做成新分頁，版面比較不擠，也比較好維護

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import calendar
from pathlib import Path
from textwrap import dedent
import plotly.graph_objects as go

st.set_page_config(page_title="Weekly Planning Dashboard", layout="wide")

# =========================
# Theme
# =========================
PINK_BG = "#F8E9ED"
PINK_HEADER = "#E4C2CB"
PINK_DEEP = "#D89CAC"
CREAM = "#F7F1DF"
BLUE = "#DCE6F4"
LAVENDER = "#EEE7F7"
TEXT = "#4F4447"
LINE = "#E8D8DD"
GREEN = "#DDEED8"
YELLOW = "#F9E8B4"
ROSE = "#F9D9DF"
WHITE = "#FFFFFF"
SOFT_BG = "#FCFAF9"

STATUS_BG = {
    "已完成": GREEN,
    "進行中": YELLOW,
    "未完成": ROSE,
}
STATUS_TEXT = {
    "已完成": "#5A8156",
    "進行中": "#9B7417",
    "未完成": "#B56E7B",
}
CATEGORY_BAR = {
    "學習成長": "#B8A2F5",
    "日常生活": "#9EBCE5",
    "自我照顧": "#A8D7B5",
}
WEEKDAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

DEFAULT_CSV = "tasks.csv"
READING_CSV = "reading_list.csv"
SLEEP_CSV = "sleep_log.csv"
HABIT_CSV = "habit_tracker.csv"
HABIT_LOG_CSV = "habit_log.csv"

APP_TZ = ZoneInfo("Asia/Taipei")

def today_local() -> date:
    return datetime.now(APP_TZ).date()

def now_local() -> datetime:
    return datetime.now(APP_TZ)

# =========================
# CSS
# =========================
st.markdown(
    f"""
    <style>
html, body, [class*="css"] {{
    font-size: 14px;
}}
.stApp {{
    background: {SOFT_BG};
    color: {TEXT};
}}
.main .block-container {{
    max-width: 100%;
    padding-top: 0.6rem;
    padding-bottom: 1.4rem;
    padding-left: 1.2rem;
    padding-right: 1.2rem;
}}
.top-wrap {{
    background: {PINK_HEADER};
    border-radius: 18px;
    padding: 18px 22px;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.top-title {{
    font-size: 2rem;
    font-weight: 700;
    color: #3E3437;
    margin-bottom: 2px;
}}
.top-sub {{
    color: #6D6265;
    font-size: 0.68rem;
}}
.shell-card {{
    background: {WHITE};
    border: 1px solid {LINE};
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}}
.card-title {{
    padding: 8px 12px;
    font-size: 0.76rem;
    font-weight: 700;
    border-bottom: 1px solid #E8D8DD;
}}
.card-body {{
    padding: 14px 16px 16px 16px;
}}
.calendar-title {{ background: {CREAM}; }}
.today-title {{ background: {BLUE}; }}
.summary-title {{ background: {LAVENDER}; }}
.calendar-grid {{
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 6px;
    text-align: center;
    align-items: center;
}}
.weekday-label {{
    font-weight: 700;
    color: #5A4F52;
    padding: 3px 0 6px 0;
    font-size: 0.64rem;
}}
.day-num {{
    width: 22px;
    height: 22px;
    margin: 0 auto;
    border-radius: 999px;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #554C4F;
    font-size: 0.68rem;
}}
.day-other {{ color: #BBB4B7; }}
.day-today {{
    background: {PINK_DEEP};
    color: white;
    font-weight: 700;
}}
.small-note {{
    color: #796E71;
    font-size: 0.64rem;
    line-height: 1.45;
}}
.mini-row {{
    display: block;
    padding: 6px 0;
    border-bottom: 1px dashed #EFE5E8;
    font-size: 0.66rem;
}}
.mini-task {{
    line-height: 1.45;
    margin-bottom: 4px;
    word-break: break-word;
}}
.mini-status {{
    display: flex;
    justify-content: flex-start;
}}
.mini-row:last-child {{ border-bottom: none; }}
.badge {{
    display: inline-block;
    border-radius: 999px;
    padding: 2px 6px;
    font-size: 0.54rem;
    font-weight: 700;
    white-space: nowrap;
}}
.stats-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 14px;
}}
.stats-box {{
    background: white;
    border: 1px solid {LINE};
    border-radius: 14px;
    text-align: center;
    padding: 10px 8px;
}}
.stats-label {{
    color: #786D71;
    font-size: 0.58rem;
}}
.stats-num {{
    margin-top: 2px;
    font-size: 0.82rem;
    font-weight: 800;
    color: #453A3D;
}}
.progress-row {{
    display: grid;
    grid-template-columns: 70px 1fr 40px;
    gap: 6px;
    align-items: center;
    margin: 5px 0;
    font-size: 0.64rem;
}}
.bar-bg {{
    height: 10px;
    background: #F1EDF0;
    border-radius: 999px;
    overflow: hidden;
}}
.bar-fill {{
    height: 100%;
    border-radius: 999px;
}}
.day-card {{
    background: white;
    border: 1px solid {LINE};
    border-radius: 18px;
    overflow: hidden;
    height: 100%;
}}
.day-header {{
    background: {PINK_BG};
    padding: 11px 15px;
    border-bottom: 1px solid {LINE};
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.day-header-title {{
    font-size: 0.78rem;
    font-weight: 700;
    color: #403638;
}}
.day-header-date {{
    font-size: 0.6rem;
    color: #6E6467;
    font-weight: 700;
}}
.day-head-row {{
    display: grid;
    grid-template-columns: 1fr 80px;
    gap: 8px;
    padding: 7px 12px 5px 12px;
    font-size: 0.62rem;
    font-weight: 700;
    color: #5E5658;
}}
.day-list {{
    padding: 0 15px 16px 15px;
    min-height: 260px;
}}
.task-row {{
    display: grid;
    grid-template-columns: 1fr 80px;
    gap: 10px;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px dashed #F0E6E9;
    font-size: 0.5rem;
}}
.task-row:last-child {{ border-bottom: none; }}
.task-name {{
    display: flex;
    align-items: center;
    gap: 8px;
}}
.checkbox {{
    width: 10px;
    height: 10px;
    border-radius: 4px;
    border: 1.4px solid #CFC5C8;
    flex: 0 0 auto;
}}
.memo-box {{
    background: #FFFDF8;
    border: 1px dashed #E5C8B8;
    border-radius: 18px;
    padding: 16px 18px 20px 18px;
    min-height: 260px;
}}
.memo-title {{
    font-size: 0.8rem;
    font-weight: 700;
    color: #9A7270;
    margin-bottom: 8px;
}}
.footer-strip {{
    margin-top: 12px;
    background: {LAVENDER};
    border-radius: 14px;
    padding: 8px 12px;
    color: #5F5659;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.64rem;
}}
.today-scroll-wrap {{
    max-height: 320px;
    overflow-y: auto;
    padding-right: 4px;
}}
.today-scroll-wrap::-webkit-scrollbar {{
    width: 6px;
}}
.today-scroll-wrap::-webkit-scrollbar-thumb {{
    background: #D8DDE6;
    border-radius: 999px;
}}
.reading-item {{
    background: #fff;
    border: 1px solid {LINE};
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 10px;
}}
.metric-chip {{
    background: #F7F1FF;
    border: 1px solid #E6DDF7;
    border-radius: 14px;
    padding: 12px;
}}
.sleep-card {{
    background: #fff;
    border: 1px solid {LINE};
    border-radius: 16px;
    padding: 14px;
}}
.habit-box {{
    background: #fff;
    border: 1px solid {LINE};
    border-radius: 16px;
    padding: 14px;
}}
div[data-testid="stButton"] > button {{
    border-radius: 10px;
    min-height: 34px;
    padding: 0 8px;
}}

.task-card-select {{
    font-size: 0.5rem;
}}

.task-card-select h2 {{
    font-size: 0.5rem !important;
    line-height: 1 !important;
    margin-bottom: 0.15rem !important;
}}
.task-card-select div[data-testid="stSelectbox"] {{
    width: 80px !important;
    min-width: 80px !important;
    max-width: 80px !important;
}}

.task-card-select div[data-testid="stSelectbox"] [data-baseweb="select"] {{
    width: 80px !important;
    min-width: 80px !important;
}}

.task-card-select div[data-testid="stSelectbox"] [data-baseweb="select"] > div {{
    min-height: 18px !important;
    height: 18px !important;
    border-radius: 10px !important;
    background: #F3F5F8 !important;
    border: 1px solid #E7EAF0 !important;
    padding-left: 6px !important;
    padding-right: 16px !important;
    display: flex !important;
    align-items: center !important;
}}

.task-card-select div[data-testid="stSelectbox"] [data-baseweb="select"] > div > div {{
    font-size: 0.50rem !important;
    line-height: 1 !important;
}}

.task-card-select div[data-testid="stSelectbox"] [data-baseweb="select"] span {{
    font-size: 0.50rem !important;
    line-height: 1 !important;
}}

.task-card-select div[data-testid="stSelectbox"] svg {{
    width: 6px !important;
    height: 6px !important;
}}

.task-card-select p,
.task-card-select label,
.task-card-select p,
.task-card-select label {{
    font-size: 0.72rem !important;
}}

div[data-testid="stButton"] > button {{
    border-radius: 8px;
    min-height: 18px;
    padding: 0 4px;
    font-size: 0.5rem;
}}
    </style>
    """,
    unsafe_allow_html=True,
)


def status_pill_html(status: str) -> str:
    bg_map = {
        "未完成": "#F9D9DF",
        "進行中": "#F9E8B4",
        "已完成": "#DDEED8",
    }
    text_map = {
        "未完成": "#B56E7B",
        "進行中": "#9B7417",
        "已完成": "#5A8156",
    }
    bg = bg_map.get(status, "#EEEEEE")
    color = text_map.get(status, "#666666")
    return (
        f'<div style="display:inline-block; padding:5px 12px; border-radius:999px; '
        f'background:{bg}; color:{color}; font-size:0.6rem; font-weight:700; '
        f'text-align:center; white-space:nowrap;">{status}</div>'
    )


# =========================
# Data helpers
# =========================
def create_sample_csv(path: str):
    sample = pd.DataFrame(
        [
            [1, "日文 L35", "學習成長", "未完成", "2026-04-21", "2026-04-22", "W17", "Mon", "", False]
        ],
        columns=["id", "task_name", "category", "status", "date", "deadline", "week", "weekday", "note", "carry_over"],
    )
    sample.to_csv(path, index=False)


def create_reading_csv(path: str):
    sample = pd.DataFrame(
        [
            [1, "城與不確定的牆", "村上春樹", "閱讀中", "小說", "想慢慢讀", "2026-04-20"],
            [2, "一間自己的房間", "Virginia Woolf", "未開始", "散文", "", "2026-04-20"],
        ],
        columns=["id", "title", "author", "status", "category", "note", "created_at"],
    )
    sample.to_csv(path, index=False)


def create_sleep_csv(path: str):
    sample = pd.DataFrame(
        [
            ["2026-04-20", "01:30", "09:30", 8.0, 4, "普通"],
            ["2026-04-21", "01:10", "09:00", 7.8, 5, "睡得不錯"],
        ],
        columns=["date", "sleep_time", "wake_time", "hours", "quality", "note"],
    )
    sample.to_csv(path, index=False)


def create_habit_csv(path: str):
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    sample = pd.DataFrame(
        [
            [1, "讀書 3 小時", *([False] * 7)],
            [2, "閱讀 30 分鐘", *([False] * 7)],
            [3, "23:30 前上床", *([False] * 7)],
            [4, "運動 20 分鐘", *([False] * 7)],
        ],
        columns=["id", "habit_name", *days],
    )
    sample.to_csv(path, index=False)
    
def create_habit_log_csv(path: str):
    sample = pd.DataFrame(
        columns=["habit_id", "date", "done"]
    )
    sample.to_csv(path, index=False)


@st.cache_data
def load_habit_log_data(path: str = HABIT_LOG_CSV) -> pd.DataFrame:
    if not Path(path).exists():
        create_habit_log_csv(path)
    df = pd.read_csv(path)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def save_habit_log_data(df: pd.DataFrame, path: str = HABIT_LOG_CSV):
    df.to_csv(path, index=False)
    st.cache_data.clear()

@st.cache_data
def load_data(path: str = DEFAULT_CSV) -> pd.DataFrame:
    if not Path(path).exists():
        create_sample_csv(path)
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"]).dt.date

    if "deadline" in df.columns:
        df["deadline"] = pd.to_datetime(df["deadline"], errors="coerce").dt.date
    else:
        df["deadline"] = pd.NaT
    
    if "carry_over" not in df.columns:
        df["carry_over"] = False
    return df


@st.cache_data
def load_reading_data(path: str = READING_CSV) -> pd.DataFrame:
    if not Path(path).exists():
        create_reading_csv(path)
    df = pd.read_csv(path)
    df["created_at"] = pd.to_datetime(df["created_at"]).dt.date
    return df


@st.cache_data
def load_sleep_data(path: str = SLEEP_CSV) -> pd.DataFrame:
    if not Path(path).exists():
        create_sleep_csv(path)
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df.sort_values("date", ascending=False)
def prepare_sleep_gantt_data(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()

    df = frame.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month_key"] = df["date"].dt.strftime("%Y-%m")
    df["date_label"] = df["date"].dt.strftime("%m/%d")

    def to_anchor_datetime(time_str: str):
        t = datetime.strptime(str(time_str), "%H:%M")
        anchor = datetime(2000, 1, 1, t.hour, t.minute)

        # 凌晨時間視為隔天
        if t.hour < 12:
            anchor += timedelta(days=1)

        return anchor

    df["gantt_start"] = df["sleep_time"].apply(to_anchor_datetime)
    df["gantt_end"] = df["wake_time"].apply(to_anchor_datetime)

    df.loc[df["gantt_end"] <= df["gantt_start"], "gantt_end"] += pd.Timedelta(days=1)

    return df.sort_values("date")

@st.cache_data
def load_habit_data(path: str = HABIT_CSV) -> pd.DataFrame:
    if not Path(path).exists():
        create_habit_csv(path)
    return pd.read_csv(path)


def normalize_task_dates(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    dt = pd.to_datetime(frame["date"])
    iso = dt.dt.isocalendar()
    frame["iso_year"] = iso.year.astype(int)
    frame["week"] = "W" + iso.week.astype(str)
    frame["weekday"] = dt.dt.strftime("%a")
    return frame

def get_deadline_label(deadline, status):
    if pd.isna(deadline):
        return ""
    today = today_local()

    if status == "已完成":
        return f"⏰ Deadline: {deadline.month}/{deadline.day}"

    if deadline < today:
        return f"🔴 已逾期 {deadline.month}/{deadline.day}"
    elif deadline == today:
        return f"🟠 今天截止 {deadline.month}/{deadline.day}"
    elif (deadline - today).days == 1:
        return f"🟡 明天截止 {deadline.month}/{deadline.day}"
    else:
        return f"⏰ Deadline: {deadline.month}/{deadline.day}"
        
# =========================
# Generic save helpers
# =========================
def save_task_data(df: pd.DataFrame, path: str = DEFAULT_CSV):
    df_to_save = df.copy()
    if "iso_year" in df_to_save.columns:
        df_to_save = df_to_save.drop(columns=["iso_year"])
    df_to_save.to_csv(path, index=False)
    st.cache_data.clear()


def save_reading_data(df: pd.DataFrame, path: str = READING_CSV):
    df.to_csv(path, index=False)
    st.cache_data.clear()


def save_sleep_data(df: pd.DataFrame, path: str = SLEEP_CSV):
    df.to_csv(path, index=False)
    st.cache_data.clear()


def save_habit_data(df: pd.DataFrame, path: str = HABIT_CSV):
    df.to_csv(path, index=False)
    st.cache_data.clear()


# =========================
# Task functions
# =========================
def update_task_status(task_id: int, new_status: str, path: str = DEFAULT_CSV):
    current_df = load_data(path).copy()
    current_df.loc[current_df["id"] == task_id, "status"] = new_status
    current_df = normalize_task_dates(current_df)
    save_task_data(current_df, path)


def add_task(
    task_name: str,
    category: str,
    status: str,
    task_date: date,
    deadline: date | None = None,
    note: str = "",
    carry_over: bool = False,
    path: str = DEFAULT_CSV
):
    current_df = load_data(path).copy()
    new_id = 1 if current_df.empty else int(current_df["id"].max()) + 1
    new_row = pd.DataFrame([{
        "id": new_id,
        "task_name": task_name.strip(),
        "category": category,
        "status": status,
        "date": task_date,
        "week": "",
        "weekday": "",
        "note": note.strip(),
        "deadline": deadline,
        "carry_over": carry_over,
    }])
    updated_df = pd.concat([current_df, new_row], ignore_index=True)
    updated_df = normalize_task_dates(updated_df)
    save_task_data(updated_df, path)


def delete_task(task_id: int, path: str = DEFAULT_CSV):
    current_df = load_data(path).copy()
    current_df = current_df[current_df["id"] != task_id].copy()
    current_df = normalize_task_dates(current_df)
    save_task_data(current_df, path)

def update_task(task_id: int, updates: dict, path: str = DEFAULT_CSV):
    current_df = load_data(path).copy()

    matched_index = current_df.index[current_df["id"] == task_id]
    if len(matched_index) == 0:
        return

    idx = matched_index[0]

    for col, value in updates.items():
        if col in ["date", "deadline"] and value is not None:
            current_df.at[idx, col] = pd.to_datetime(value).date()
        else:
            current_df.at[idx, col] = value

    current_df = normalize_task_dates(current_df)
    save_task_data(current_df, path)
    
def carry_task_to_next_day(task_id: int, path: str = DEFAULT_CSV):
    current_df = load_data(path).copy()
    task_row = current_df[current_df["id"] == task_id]

    if task_row.empty:
        return

    row = task_row.iloc[0]
    next_date = row["date"] + timedelta(days=1)

    current_df.loc[current_df["id"] == task_id, "carry_over"] = True

    new_id = int(current_df["id"].max()) + 1
    new_row = pd.DataFrame([{
        "id": new_id,
        "task_name": row["task_name"],
        "category": row["category"],
        "status": "未完成",
        "date": next_date,
        "deadline": row["deadline"],
        "week": "",
        "weekday": "",
        "note": row["note"],
        "carry_over": False,
    }])

    updated_df = pd.concat([current_df, new_row], ignore_index=True)
    updated_df = normalize_task_dates(updated_df)
    save_task_data(updated_df, path)
# =========================
# Reading list functions
# =========================
def add_book(title: str, author: str, status: str, category: str, note: str):
    current_df = load_reading_data().copy()
    new_id = 1 if current_df.empty else int(current_df["id"].max()) + 1
    new_row = pd.DataFrame([{
        "id": new_id,
        "title": title.strip(),
        "author": author.strip(),
        "status": status,
        "category": category,
        "note": note.strip(),
        "created_at": today_local(),
    }])
    updated_df = pd.concat([current_df, new_row], ignore_index=True)
    save_reading_data(updated_df)


def delete_book(book_id: int):
    current_df = load_reading_data().copy()
    current_df = current_df[current_df["id"] != book_id].copy()
    save_reading_data(current_df)


def update_book_status(book_id: int, new_status: str):
    current_df = load_reading_data().copy()
    current_df.loc[current_df["id"] == book_id, "status"] = new_status
    save_reading_data(current_df)


# =========================
# Sleep functions
# =========================
def add_sleep_log(log_date: date, sleep_time: str, wake_time: str, quality: int, note: str):
    current_df = load_sleep_data().copy()
    sleep_dt = datetime.combine(log_date, datetime.strptime(sleep_time, "%H:%M").time())
    wake_dt = datetime.combine(log_date, datetime.strptime(wake_time, "%H:%M").time())
    if wake_dt <= sleep_dt:
        wake_dt += timedelta(days=1)
    hours = round((wake_dt - sleep_dt).total_seconds() / 3600, 1)

    new_row = pd.DataFrame([{
        "date": log_date,
        "sleep_time": sleep_time,
        "wake_time": wake_time,
        "hours": hours,
        "quality": quality,
        "note": note.strip(),
    }])
    current_df = current_df[current_df["date"] != log_date]
    updated_df = pd.concat([current_df, new_row], ignore_index=True)
    updated_df = updated_df.sort_values("date", ascending=False)
    save_sleep_data(updated_df)


def delete_sleep_log(log_date: date):
    current_df = load_sleep_data().copy()
    current_df = current_df[current_df["date"] != log_date].copy()
    save_sleep_data(current_df)


# =========================
# Habit functions
# =========================
def add_habit(habit_name: str):
    current_df = load_habit_data().copy()
    new_id = 1 if current_df.empty else int(current_df["id"].max()) + 1
    new_row = pd.DataFrame([{
        "id": new_id,
        "habit_name": habit_name.strip(),
        "Mon": False,
        "Tue": False,
        "Wed": False,
        "Thu": False,
        "Fri": False,
        "Sat": False,
        "Sun": False,
    }])
    updated_df = pd.concat([current_df, new_row], ignore_index=True)
    save_habit_data(updated_df)


def delete_habit(habit_id: int):
    current_df = load_habit_data().copy()
    current_df = current_df[current_df["id"] != habit_id].copy()
    save_habit_data(current_df)


def update_habit_day(habit_id: int, day_name: str, value: bool):
    current_df = load_habit_data().copy()
    current_df.loc[current_df["id"] == habit_id, day_name] = bool(value)
    save_habit_data(current_df)

def update_habit_log(habit_id: int, log_date: date, value: bool):
    current_df = load_habit_log_data().copy()

    if not current_df.empty:
        current_df["date"] = pd.to_datetime(current_df["date"]).dt.date
        current_df = current_df[
            ~(
                (current_df["habit_id"] == habit_id)
                & (current_df["date"] == log_date)
            )
        ].copy()

    new_row = pd.DataFrame([{
        "habit_id": habit_id,
        "date": log_date,
        "done": bool(value),
    }])

    updated_df = pd.concat([current_df, new_row], ignore_index=True)
    save_habit_log_data(updated_df)

# =========================
# UI helpers
# =========================
def get_week_options(year: int):
    last_week = date(year, 12, 28).isocalendar().week
    return [f"W{i}" for i in range(1, last_week + 1)]


def get_year_options(frame: pd.DataFrame):
    years = sorted(frame["iso_year"].dropna().unique().tolist())
    current_year = now_local().year
    if current_year not in years:
        years.append(current_year)
        years.sort()
    return years


def get_week_range(selected_year: int, selected_week: str):
    week_num = int(selected_week.replace("W", ""))
    monday = datetime.fromisocalendar(selected_year, week_num, 1).date()
    sunday = datetime.fromisocalendar(selected_year, week_num, 7).date()
    return monday, sunday


def badge(status: str) -> str:
    bg = STATUS_BG.get(status, "#EFEFEF")
    color = STATUS_TEXT.get(status, "#666666")
    return f'<span class="badge" style="background:{bg}; color:{color};">{status}</span>'


def render_calendar_html(year: int, month: int, today_value: date, selected_week: str, monday: date, sunday: date):
    cal = calendar.Calendar(firstweekday=0)
    cells = []
    for wd in WEEKDAY_ORDER:
        cells.append(f'<div class="weekday-label">{wd}</div>')
    for d in cal.itermonthdates(year, month):
        cls = "day-num"
        if d.month != month:
            cls += " day-other"
        if d == today_value:
            cls += " day-today"
        cells.append(f'<div class="{cls}">{d.day}</div>')
    return f"""
    <div class="shell-card">
    <div class="card-title calendar-title">📅 月曆</div>
    <div class="card-body">
            <div style="text-align:center; font-size:1rem; font-weight:700; margin-bottom:8px;">{year} 年 {month} 月</div>
            <div class="calendar-grid">{''.join(cells)}</div>
            <div style="margin-top:12px; background:{CREAM}; border-radius:12px; padding:10px 12px; color:#6D6466; font-size:0.8rem;">
                ⭐ {selected_week}: {monday.month}/{monday.day} ({monday.strftime('%a')}) ~ {sunday.month}/{sunday.day} ({sunday.strftime('%a')})
            </div>
    </div>
    </div>
    """


def render_today_card(frame: pd.DataFrame, today_value: date):
    subset = frame[frame["date"] == today_value]
    categories = ["學習成長", "日常生活", "自我照顧"]
    blocks = []

    for cat in categories:
        cat_df = subset[subset["category"] == cat].head(5)
        if cat_df.empty:
            content = '<div class="small-note">今天這一類目前沒有任務。</div>'
        else:
            rows = []
            for row in cat_df.itertuples():
                row_html = (
                    '<div class="mini-row">'
                    f'<div class="mini-task">☐ {row.task_name}</div>'
                    f'<div class="mini-status">{badge(row.status)}</div>'
                    '</div>'
                )
                rows.append(row_html)
            content = "".join(rows)

        block_html = (
            '<div style="background:rgba(255,255,255,0.45); border:1px solid #D7E0EF; border-radius:14px; padding:12px;">'
            f'<div style="text-align:center; font-weight:700; font-size:0.66rem; margin-bottom:6px;">{cat}</div>'
            f'{content}'
            '</div>'
        )
        blocks.append(block_html)

    return (
        '<div class="shell-card">'
        '<div class="card-title today-title">'
        f'📝 今日任務 ({today_value.month}/{today_value.day} {today_value.strftime("%a")})'
        '</div>'
        '<div class="card-body">'
        '<div class="today-scroll-wrap">'
        '<div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px;">'
        f'{"".join(blocks)}'
        '</div></div></div></div>'
    )


def render_summary_card(frame: pd.DataFrame, selected_week: str):
    subset = frame[frame["week"] == selected_week]
    total = len(subset)
    done = int((subset["status"] == "已完成").sum())
    doing = int((subset["status"] == "進行中").sum())
    todo = int((subset["status"] == "未完成").sum())

    categories = ["學習成長", "日常生活", "自我照顧"]
    rows = []

    for label in categories:
        cat_df = subset[subset["category"] == label]
        total_cat = len(cat_df)
        done_cat = int((cat_df["status"] == "已完成").sum())
        rate = 0 if total_cat == 0 else round(done_cat / total_cat * 100)
        rows.append(
            '<div class="progress-row">'
            f'<div>{label}</div>'
            f'<div class="bar-bg"><div class="bar-fill" style="width:{rate}%; background:{CATEGORY_BAR[label]};"></div></div>'
            f'<div style="text-align:right;">{rate}%</div>'
            '</div>'
        )

    return (
        '<div class="shell-card">'
        f'<div class="card-title summary-title">📊 本週任務摘要 ({selected_week})</div>'
        '<div class="card-body">'
        '<div class="stats-grid">'
        f'<div class="stats-box"><div class="stats-label">總任務</div><div class="stats-num">{total}</div></div>'
        f'<div class="stats-box"><div class="stats-label" style="color:#5E8A57;">已完成</div><div class="stats-num" style="color:#5E8A57;">{done}</div></div>'
        f'<div class="stats-box"><div class="stats-label" style="color:#A87B16;">進行中</div><div class="stats-num" style="color:#A87B16;">{doing}</div></div>'
        f'<div class="stats-box"><div class="stats-label" style="color:#BE7484;">未完成</div><div class="stats-num" style="color:#BE7484;">{todo}</div></div>'
        '</div>'
        '<div style="font-weight:700; color:#685A87; margin: 6px 0 8px 0;">各分類達成率</div>'
        f'{"".join(rows)}'
        '<div style="margin-top:14px; padding:12px; border-radius:12px; background:#F8F5FF;">🌙 本週目標：保持節奏，穩定前進</div>'
        '</div></div>'
    )


def render_day_panel(day_name: str, day_date: date, frame: pd.DataFrame, selected_week: str):
    subset = frame[(frame["week"] == selected_week) & (frame["weekday"] == day_name)].copy()

    st.markdown('<div class="task-card-select">', unsafe_allow_html=True)
    with st.container(border=True):
        top_left, top_right = st.columns([2, 1])
        with top_left:
            st.markdown(f"## {day_name}.")
        with top_right:
            st.markdown(f"**{day_date.month}/{day_date.day}**")

        st.markdown("**任務項目　　　　狀態**")

        if subset.empty:
            st.info("")
        else:
            for row in subset.itertuples():
                c1, c2, c3, c4, c5 = st.columns([0.5, 0.7, 0.12, 0.12, 0.12], gap="small")
                with c1:
                    if bool(row.carry_over):
                        st.markdown(
                            f"<span style='font-size:0.9rem; color:#B56E7B; text-decoration: line-through; text-decoration-color:#D9534F; text-decoration-thickness:2px;'>{row.task_name}</span>",
                            unsafe_allow_html=True
                        )
                        st.caption("已延到下一天")
                    else:
                        st.markdown(
                            f"<div style='font-size:0.9rem; font-weight:600; line-height:1.3;'>{row.task_name}</div>",
                            unsafe_allow_html=True
                        )
                
                    if pd.notna(row.deadline):
                        st.caption(get_deadline_label(row.deadline, row.status))
                with c2:
                    new_status = st.selectbox(
                        "狀態",
                        ["未完成", "進行中", "已完成"],
                        index=["未完成", "進行中", "已完成"].index(row.status),
                        key=f"status_{row.id}",
                        label_visibility="collapsed"
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                
                    if new_status != row.status:
                        update_task_status(row.id, new_status)
                        st.rerun()
                with c3:
                    if st.button("↷", key=f"carry_{row.id}", use_container_width=True):
                        carry_task_to_next_day(row.id)
                        st.rerun()
                with c4:
                    if st.button("✏️", key=f"edit_{row.id}", use_container_width=True):
                        st.session_state[f"editing_task_{row.id}"] = True
                with c5:
                    if st.button("🗑️", key=f"delete_{row.id}", use_container_width=True):
                        delete_task(row.id)
                        st.rerun()
                if st.session_state.get(f"editing_task_{row.id}", False):
                    with st.container():
                        with st.form(f"edit_form_{row.id}"):
                            new_name = st.text_input("任務名稱", value=row.task_name)
                            new_category = st.selectbox(
                                "分類",
                                ["學習成長", "日常生活", "自我照顧"],
                                index=["學習成長", "日常生活", "自我照顧"].index(row.category)
                            )
                            new_date = st.date_input("安排日期", value=row.date, key=f"edit_date_{row.id}")
                            new_deadline = st.date_input(
                                "Deadline",
                                value=row.deadline if pd.notna(row.deadline) else row.date,
                                key=f"edit_deadline_{row.id}",
                            )
                            new_note = st.text_area("備註", value=row.note if pd.notna(row.note) else "")
                            col_save, col_cancel = st.columns(2)
                            save_clicked = col_save.form_submit_button("儲存修改")
                            cancel_clicked = col_cancel.form_submit_button("取消")
                
                            if save_clicked:
                                update_task(row.id, {
                                    "task_name": new_name.strip(),
                                    "category": new_category,
                                    "date": new_date,
                                    "deadline": new_deadline,
                                    "note": new_note.strip(),
                                })
                                st.session_state[f"editing_task_{row.id}"] = False
                                st.rerun()
                
                            if cancel_clicked:
                                st.session_state[f"editing_task_{row.id}"] = False
                                st.rerun()

        with st.expander(f"➕ 新增 {day_name} 任務"):
            with st.form(f"form_{day_name}_{day_date}"):
                task_name = st.text_input("任務名稱", key=f"new_task_{day_name}_{day_date}")
                category = st.selectbox("分類", ["學習成長", "日常生活", "自我照顧"], key=f"cat_{day_name}_{day_date}")
                status = st.selectbox("初始狀態", ["未完成", "進行中", "已完成"], key=f"init_status_{day_name}_{day_date}")
                note = st.text_area("備註", key=f"note_{day_name}_{day_date}")
                submitted = st.form_submit_button("新增任務")
                deadline = st.date_input(
                    "Deadline",
                    value=day_date,
                    key=f"deadline_{day_name}_{day_date}"
                )
                if submitted:
                    if task_name.strip():
                        add_task(task_name, category, status, day_date, deadline, note)
                        st.success("已新增任務")
                        st.rerun()
                    else:
                        st.warning("請輸入任務名稱")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# Load data
# =========================
df = normalize_task_dates(load_data())
reading_df = load_reading_data()
sleep_df = load_sleep_data()
habit_df = load_habit_data()


# =========================
# Sidebar
# =========================
with st.sidebar:
    st.markdown("### 資料來源")
    uploaded = st.file_uploader("上傳 tasks.csv", type=["csv"], key="task_csv_uploader")
    if uploaded is not None:
        up_df = pd.read_csv(uploaded)
        up_df.to_csv(DEFAULT_CSV, index=False)
        st.cache_data.clear()
        st.success("已更新資料，重新整理頁面即可。")
        st.rerun()

    st.markdown("---")
    st.markdown("### 新增任務")
    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input("任務名稱")
        category = st.selectbox("分類", ["學習成長", "日常生活", "自我照顧"])
        status = st.selectbox("狀態", ["未完成", "進行中", "已完成"])
        task_date = st.date_input("日期", value=today_local())
        deadline = st.date_input("Deadline", value=task_date)
        note = st.text_area("備註", height=80)
        submitted = st.form_submit_button("新增任務")
        if submitted:
            if not task_name.strip():
                st.warning("請先輸入任務名稱")
            else:
                add_task(task_name, category, status, task_date, deadline, note)
                st.success("任務已新增")
                st.rerun()

    st.markdown("---")
    st.markdown("**CSV 欄位**")
    st.code("id,task_name,category,status,date,deadline,week,weekday,note,carry_over", language="text")


# =========================
# State
# =========================
year_options = get_year_options(df)
default_year = now_local().year if now_local().year in year_options else year_options[0]

if "selected_year" not in st.session_state:
    st.session_state.selected_year = default_year
if "selected_week" not in st.session_state:
    st.session_state.selected_week = "W" + str(now_local().isocalendar().week)

selected_year = st.session_state.selected_year
week_options = get_week_options(selected_year)
if st.session_state.selected_week not in week_options:
    st.session_state.selected_week = week_options[0]

selected_week = st.session_state.selected_week
monday, sunday = get_week_range(selected_year, selected_week)
focus_year = monday.year
focus_month = monday.month


# =========================
# Tabs
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Dashboard",
    "Task Manager",
    "Weekly Planner",
    "Reading List",
    "Sleep & Habits",
])


# =========================
# Dashboard
# =========================
with tab1:
    st.markdown(
        f'''
        <div class="top-wrap">
            <div>
                <div class="top-title">Weekly Planning Dashboard ✧</div>
                <div class="top-sub">小小的進步，累積成更好的自己。</div>
            </div>
            <div class="top-sub">{focus_year} / {calendar.month_abbr[focus_month]} &nbsp;&nbsp;|&nbsp;&nbsp; {selected_week} &nbsp;&nbsp;|&nbsp;&nbsp; Today: {today_local().strftime('%b %d (%a)')}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([0.95, 3.5], gap="small")

    with left_col:
        st.markdown(render_calendar_html(focus_year, focus_month, today_local(), selected_week, monday, sunday), unsafe_allow_html=True)
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        st.markdown(render_today_card(df, today_local()), unsafe_allow_html=True)
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        st.markdown(render_summary_card(df, selected_week), unsafe_allow_html=True)

    with right_col:
        c1, c2, c3, c4 = st.columns([0.55, 1.05, 1.05, 1.25])

        with c1:
            st.markdown('<div class="small-note" style="margin-top:8px;">本週目標：持續進步，累積成更好的自己。</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div style="margin-bottom:4px; font-weight:700; color:#6C6064; text-align:center;">年份</div>', unsafe_allow_html=True)
            st.session_state.selected_year = st.selectbox("年份", year_options, index=year_options.index(st.session_state.selected_year), label_visibility="collapsed", key="dashboard_year")
        with c3:
            current_week_options = get_week_options(st.session_state.selected_year)
            if st.session_state.selected_week not in current_week_options:
                st.session_state.selected_week = current_week_options[0]
            st.markdown('<div style="margin-bottom:4px; font-weight:700; color:#6C6064; text-align:center;">週次</div>', unsafe_allow_html=True)
            st.session_state.selected_week = st.selectbox("週次", current_week_options, index=current_week_options.index(st.session_state.selected_week), label_visibility="collapsed", key="dashboard_week")

        selected_year = st.session_state.selected_year
        selected_week = st.session_state.selected_week
        monday, sunday = get_week_range(selected_year, selected_week)

        with c4:
            st.markdown(
                f'<div style="text-align:right; margin-top:10px;">'
                f'<div style="font-size:1.0rem; font-weight:700; color:#413739;">{monday.year} / {calendar.month_abbr[monday.month]} / 第 {selected_week.replace("W", "")} 週</div>'
                f'<div class="small-note">{monday.month}/{monday.day} ({monday.strftime("%a")}) - {sunday.month}/{sunday.day} ({sunday.strftime("%a")})</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        week_dates = [monday + timedelta(days=i) for i in range(7)]

        top_days = st.columns(4, gap="small")
        for idx, day_name in enumerate(["Mon", "Tue", "Wed", "Thu"]):
            with top_days[idx]:
                render_day_panel(day_name, week_dates[idx], df, selected_week)

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
        bottom_left, bottom_mid, bottom_right, memo_col = st.columns([1, 1, 1, 0.78], gap="small")

        with bottom_left:
            render_day_panel("Fri", week_dates[4], df, selected_week)
        with bottom_mid:
            render_day_panel("Sat", week_dates[5], df, selected_week)
        with bottom_right:
            render_day_panel("Sun", week_dates[6], df, selected_week)

        with memo_col:
            if reading_df.empty:
                reading_preview_html = dedent("""
                <div class="small-note">
                    目前還沒有書單，可以到 Reading List 分頁新增一本最近想讀的書 ✨
                </div>
                """)
            else:
                preview_df = reading_df[reading_df["status"] != "已讀完"].sort_values("created_at", ascending=False).head(5)
                preview_blocks = []
        
                for idx, row in enumerate(preview_df.itertuples()):
                    border_style = "border-bottom:1px dashed #EFE5E8;" if idx < len(preview_df) - 1 else ""
        
                    preview_blocks.append(dedent(f"""
                    <div style="padding:8px 0; {border_style}">
                        <div style="font-size:0.72rem; font-weight:700; color:#5B4A4F; line-height:1.4; word-break:break-word;">
                            {row.title}
                        </div>
                        <div class="small-note">{row.author}｜{row.status}</div>
                    </div>
                    """))
        
                reading_preview_html = "".join(preview_blocks)
        
            memo_html = dedent(f"""
            <div class="memo-box">
                <div class="memo-title">待讀書單 ♡</div>
                {reading_preview_html}
            """)
        
            st.markdown(memo_html, unsafe_allow_html=True)
    st.markdown('''
        <div class="footer-strip">
            <div>快速切換：任務總表 ｜ 閱讀清單 ｜ 睡眠紀錄 ｜ Habit Tracker</div>
            <div>週次切換後，右側與統計會同步更新</div>
        </div>
        ''', unsafe_allow_html=True)


# =========================
# Task manager
# =========================
with tab2:
    st.subheader("Task Manager")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        category_filter = st.selectbox("分類篩選", ["全部", "學習成長", "日常生活", "自我照顧"], key="tab2_category")
    with filter_col2:
        status_filter = st.selectbox("狀態篩選", ["全部", "未完成", "進行中", "已完成"], key="tab2_status")

    edit_df = df.copy()
    if category_filter != "全部":
        edit_df = edit_df[edit_df["category"] == category_filter]
    if status_filter != "全部":
        edit_df = edit_df[edit_df["status"] == status_filter]

    show_df = edit_df.copy()
    show_df["刪除"] = False
    edited = st.data_editor(
        show_df,
        use_container_width=True,
        hide_index=True,
        disabled=["id", "task_name", "category", "status", "date", "week", "weekday", "note", "iso_year"],
    )

    delete_ids = edited.loc[edited["刪除"] == True, "id"].tolist()
    if delete_ids and st.button("刪除選取任務"):
        current_df = load_data(DEFAULT_CSV).copy()
        current_df = current_df[~current_df["id"].isin(delete_ids)].copy()
        current_df = normalize_task_dates(current_df)
        save_task_data(current_df, DEFAULT_CSV)
        st.success("已刪除選取任務")
        st.rerun()


# =========================
# Weekly planner
# =========================
with tab3:
    st.subheader("新增本週任務")
    with st.form("weekly_add_form", clear_on_submit=True):
        task_name = st.text_input("任務名稱")
        category = st.selectbox("分類", ["學習成長", "日常生活", "自我照顧"], key="tab3_category")
        status = st.selectbox("狀態", ["未完成", "進行中", "已完成"], key="tab3_status")
        task_date = st.date_input("日期", value=monday)
        note = st.text_area("備註")
        submitted = st.form_submit_button("新增")
        if submitted:
            if task_name.strip():
                add_task(task_name, category, status, task_date, note)
                st.success("任務已新增")
                st.rerun()
            else:
                st.warning("請輸入任務名稱")


# =========================
# Reading list
# =========================
with tab4:
    st.subheader("待讀書單")
    left, right = st.columns([1.05, 1.45], gap="large")

    with left:
        with st.form("add_book_form", clear_on_submit=True):
            title = st.text_input("書名")
            author = st.text_input("作者")
            book_status = st.selectbox("狀態", ["未開始", "閱讀中", "已讀完"])
            book_category = st.selectbox("類型", ["小說", "散文", "心理", "科普", "日文", "英文", "其他"])
            note = st.text_area("備註")
            submitted = st.form_submit_button("新增書單")
            if submitted:
                if title.strip():
                    add_book(title, author, book_status, book_category, note)
                    st.success("已加入待讀書單")
                    st.rerun()
                else:
                    st.warning("請輸入書名")

        total_books = len(reading_df)
        reading_now = int((reading_df["status"] == "閱讀中").sum())
        finished_books = int((reading_df["status"] == "已讀完").sum())

        c1, c2, c3 = st.columns(3)
        c1.metric("總書數", total_books)
        c2.metric("閱讀中", reading_now)
        c3.metric("已讀完", finished_books)

    with right:
        if reading_df.empty:
            st.info("目前還沒有書單，可以先新增一本最近想讀的書 ✨")
        else:
            for row in reading_df.sort_values("created_at", ascending=False).itertuples():
                with st.container(border=True):
                    col1, col2, col3 = st.columns([1.5, 0.8, 0.28])
                    with col1:
                        st.markdown(f"**{row.title}**")
                        st.caption(f"作者：{row.author}　｜　類型：{row.category}")
                        if str(row.note).strip():
                            st.write(row.note)
                    with col2:
                        new_status = st.selectbox(
                            "書籍狀態",
                            ["未開始", "閱讀中", "已讀完"],
                            index=["未開始", "閱讀中", "已讀完"].index(row.status),
                            key=f"book_status_{row.id}",
                            label_visibility="collapsed"
                        )
                        if new_status != row.status:
                            update_book_status(row.id, new_status)
                            st.rerun()
                    with col3:
                        if st.button("🗑️", key=f"delete_book_{row.id}", use_container_width=True):
                            delete_book(row.id)
                            st.rerun()


# =========================
# Sleep & Habits
# =========================
with tab5:
    st.subheader("Sleep & Habits")
    sleep_tab, habit_tab = st.tabs(["睡眠紀錄表", "Habit Tracker"])

    with sleep_tab:
        st.markdown("#### 月統計睡眠圖")

        sleep_gantt_df = prepare_sleep_gantt_data(sleep_df)
    
        current_year = today_local().year
        month_options = [f"{current_year}-{m:02d}" for m in range(1, 13)]
    
        if not sleep_df.empty:
            latest_data_month = pd.to_datetime(sleep_df["date"]).max().strftime("%Y-%m")
            default_month_index = month_options.index(latest_data_month) if latest_data_month in month_options else 0
        else:
            current_month = today_local().strftime("%Y-%m")
            default_month_index = month_options.index(current_month)
    
        selected_sleep_month = st.selectbox(
            "選擇月份",
            month_options,
            index=default_month_index,
            format_func=lambda x: x.replace("-", "/"),
            key="sleep_month_selector"
        )
    
        sleep_df_for_stats = sleep_df.copy()
        if not sleep_df_for_stats.empty:
            sleep_df_for_stats["date"] = pd.to_datetime(sleep_df_for_stats["date"])
            sleep_df_for_stats["month_key"] = sleep_df_for_stats["date"].dt.strftime("%Y-%m")
            selected_month_sleep_df = sleep_df_for_stats[
                sleep_df_for_stats["month_key"] == selected_sleep_month
            ].copy()
        else:
            selected_month_sleep_df = pd.DataFrame()
    
        selected_month_start = pd.to_datetime(f"{selected_sleep_month}-01")
        next_month_start = selected_month_start + pd.offsets.MonthBegin(1)
        month_end = next_month_start - pd.Timedelta(days=1)
    
        all_days = pd.DataFrame({
            "date": pd.date_range(selected_month_start, month_end, freq="D")
        })
        all_days["date_label"] = all_days["date"].dt.strftime("%m/%d")
        all_days["day_num"] = all_days["date"].dt.strftime("%d")
        all_days["month_key"] = all_days["date"].dt.strftime("%Y-%m")
    
        month_df = all_days.merge(
            sleep_gantt_df,
            on=["date", "date_label", "month_key"],
            how="left"
        )
    
        plot_df = month_df.dropna(subset=["gantt_start", "gantt_end"]).copy()
        y_order = month_df["day_num"].tolist()[::-1]
    
        fig = go.Figure()
    
        fig.add_trace(go.Scatter(
            x=[datetime(2000, 1, 1, 18, 0)] * len(y_order),
            y=y_order,
            mode="markers",
            marker=dict(size=1, color="rgba(0,0,0,0)"),
            hoverinfo="skip",
            showlegend=False
        ))
    
        for row in plot_df.itertuples():
            duration_ms = (row.gantt_end - row.gantt_start).total_seconds() * 1000
    
            fig.add_trace(go.Bar(
                x=[duration_ms],
                y=[row.day_num],
                base=[row.gantt_start],
                orientation="h",
                width=0.28,
                marker=dict(
                    color="#E6CDD6",
                    line=dict(color="#D7B8C4", width=1)
                ),
                hovertemplate=(
                    f"{row.date_label}<br>"
                    f"入睡：{row.sleep_time}<br>"
                    f"起床：{row.wake_time}<br>"
                    f"時數：{row.hours} 小時<br>"
                    f"品質：{row.quality}/5"
                    "<extra></extra>"
                ),
                showlegend=False
            ))
    
        fig.update_yaxes(
            type="category",
            categoryorder="array",
            categoryarray=y_order,
            title=None,
            tickmode="array",
            tickvals=y_order,
            ticktext=y_order,
            tickfont=dict(size=11, color="#7A6D72")
        )
    
        fig.update_xaxes(
            title="時間",
            tickformat="%H:%M",
            range=[datetime(2000, 1, 1, 18, 0), datetime(2000, 1, 2, 12, 0)],
            tickfont=dict(size=11, color="#8A8084"),
            title_font=dict(size=13, color="#7A6D72"),
            gridcolor="#F0E6E9"
        )
    
        fig.update_layout(
            height=max(520, len(month_df) * 22 + 80),
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="#FCFAF9",
            plot_bgcolor="#FFFDF8",
            bargap=0.55,
        )
    
        st.plotly_chart(fig, use_container_width=True)
    
        st.markdown("---")
    
        left, right = st.columns([1.0, 1.4], gap="large")
    
        with left:
            with st.form("sleep_form", clear_on_submit=True):
                log_date = st.date_input("日期", value=today_local(), key="sleep_date")
                sleep_time = st.text_input("入睡時間（HH:MM）", value="01:00")
                wake_time = st.text_input("起床時間（HH:MM）", value="09:00")
                quality = st.slider("睡眠品質", 1, 5, 3)
                note = st.text_area("備註")
                submitted = st.form_submit_button("儲存睡眠紀錄")
                if submitted:
                    try:
                        datetime.strptime(sleep_time, "%H:%M")
                        datetime.strptime(wake_time, "%H:%M")
                        add_sleep_log(log_date, sleep_time, wake_time, quality, note)
                        st.success("已儲存睡眠紀錄")
                        st.rerun()
                    except ValueError:
                        st.error("時間格式請輸入 HH:MM，例如 01:30")
    
            c1, c2 = st.columns(2)
            if not selected_month_sleep_df.empty:
                avg_hours = round(float(selected_month_sleep_df["hours"].mean()), 1)
                avg_quality = round(float(selected_month_sleep_df["quality"].mean()), 1)
            else:
                avg_hours = 0.0
                avg_quality = 0.0
    
            c1.metric("月平均睡眠時數", f"{avg_hours} h")
            c2.metric("月平均睡眠品質", f"{avg_quality} / 5")
    
        with right:
            st.markdown("#### 最近睡眠紀錄")
            if sleep_df.empty:
                st.info("目前還沒有睡眠紀錄。")
            else:
                for row in sleep_df.sort_values("date", ascending=False).head(14).itertuples():
                    with st.container(border=True):
                        c1, c2 = st.columns([1.25, 0.2])
                        with c1:
                            st.markdown(f"**{row.date}**")
                            st.write(f"{row.sleep_time} → {row.wake_time}　｜　{row.hours} 小時")
                            st.caption(f"品質：{row.quality}/5")
                            if pd.notna(row.note) and str(row.note).strip():
                                st.write(row.note)
                        with c2:
                            if st.button("🗑️", key=f"del_sleep_{row.date}"):
                                delete_sleep_log(row.date)
                                st.rerun()
    
            st.markdown("#### 睡眠明細表")
            st.dataframe(sleep_df.sort_values("date", ascending=False), use_container_width=True, hide_index=True)
    with habit_tab:
        habit_log_df = load_habit_log_data()
        current_year = today_local().year
        month_options = [f"{current_year}-{m:02d}" for m in range(1, 13)]
        current_month = today_local().strftime("%Y-%m")
        default_month_index = month_options.index(current_month)
        selected_habit_month = st.selectbox(
            "選擇 Habit 月份",
            month_options,
            index=default_month_index,
            format_func=lambda x: x.replace("-", "/"),
            key="habit_month_selector"
        )
        
        selected_month_start = pd.to_datetime(f"{selected_habit_month}-01")
        next_month_start = selected_month_start + pd.offsets.MonthBegin(1)
        month_end = next_month_start - pd.Timedelta(days=1)
        month_days = pd.date_range(selected_month_start, month_end, freq="D")
        
        left, right = st.columns([0.9, 1.6], gap="large")
    
        with left:
            with st.form("add_habit_form", clear_on_submit=True):
                habit_name = st.text_input("習慣名稱")
                submitted = st.form_submit_button("新增習慣")
                if submitted:
                    if habit_name.strip():
                        add_habit(habit_name)
                        st.success("已新增習慣")
                        st.rerun()
                    else:
                        st.warning("請輸入習慣名稱")
    
            st.markdown("#### 本月習慣完成次數")
            if habit_df.empty:
                st.info("先新增一個你想追蹤的習慣吧 🌱")
            else:
                for habit in habit_df.itertuples():
                    if habit_log_df.empty:
                        done_count = 0
                    else:
                        tmp = habit_log_df.copy()
                        tmp["date"] = pd.to_datetime(tmp["date"])
                        tmp["month_key"] = tmp["date"].dt.strftime("%Y-%m")
                        done_count = int(
                            (
                                (tmp["habit_id"] == habit.id)
                                & (tmp["month_key"] == selected_habit_month)
                                & (tmp["done"] == True)
                            ).sum()
                        )
    
                    total_days = len(month_days)
                    rate = int(done_count / total_days * 100) if total_days > 0 else 0
    
                    st.markdown(
                        f'''
                        <div class="progress-row">
                            <div>{habit.habit_name}</div>
                            <div class="bar-bg">
                                <div class="bar-fill" style="width:{rate}%; background:#B8A2F5;"></div>
                            </div>
                            <div style="text-align:right;">{done_count}/{total_days}</div>
                        </div>
                        ''',
                        unsafe_allow_html=True,
                    )
    
        with right:
            st.markdown("#### Habit Tracker 月打卡表")
    
            if habit_df.empty:
                st.info("先新增一個你想追蹤的習慣吧 🌱")
            else:
                for habit in habit_df.itertuples():
                    with st.container(border=True):
                        head1, head2 = st.columns([1.3, 0.2])
                        with head1:
                            st.markdown(f"**{habit.habit_name}**")
                        with head2:
                            if st.button("🗑️", key=f"delete_habit_{habit.id}"):
                                delete_habit(habit.id)
                                st.rerun()
    
                        for start_idx in range(0, len(month_days), 7):
                            row_days = month_days[start_idx:start_idx + 7]
                            cols = st.columns(7)
    
                            for idx in range(7):
                                with cols[idx]:
                                    if idx < len(row_days):
                                        day_dt = row_days[idx]
                                        day_date = day_dt.date()
    
                                        checked = False
                                        if not habit_log_df.empty:
                                            matched = habit_log_df[
                                                (habit_log_df["habit_id"] == habit.id)
                                                & (pd.to_datetime(habit_log_df["date"]).dt.date == day_date)
                                            ]
                                            if not matched.empty:
                                                checked = bool(matched.iloc[-1]["done"])
    
                                        val = st.checkbox(
                                            f"{day_dt.strftime('%d')}",
                                            value=checked,
                                            key=f"habit_{habit.id}_{day_date}"
                                        )
                                        if val != checked:
                                            update_habit_log(habit.id, day_date, val)
                                            st.rerun()
                                    else:
                                        st.markdown("&nbsp;", unsafe_allow_html=True)
