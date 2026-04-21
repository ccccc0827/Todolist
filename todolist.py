import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import calendar
from pathlib import Path

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

# =========================
# CSS
# =========================
st.markdown(
    f"""
    <style>
    .stApp {{
        background: {SOFT_BG};
        color: {TEXT};
    }}
    .main .block-container {{
        max-width: 1450px;
        padding-top: 1rem;
        padding-bottom: 2rem;
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
        font-size: 1.9rem;
        font-weight: 700;
        color: #3E3437;
        margin-bottom: 4px;
    }}
    .top-sub {{
        color: #6D6265;
        font-size: 0.95rem;
    }}
    .shell-card {{
        background: {WHITE};
        border: 1px solid {LINE};
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }}
    .card-title {{
        padding: 12px 16px;
        font-size: 1.03rem;
        font-weight: 700;
        border-bottom: 1px solid {LINE};
        color: #453A3D;
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
        padding: 4px 0 6px 0;
    }}
    .day-num {{
        width: 32px;
        height: 32px;
        margin: 0 auto;
        border-radius: 999px;
        display: flex;
        justify-content: center;
        align-items: center;
        color: #554C4F;
        font-size: 0.94rem;
    }}
    .day-other {{ color: #BBB4B7; }}
    .day-today {{
        background: {PINK_DEEP};
        color: white;
        font-weight: 700;
    }}
    .small-note {{
        color: #796E71;
        font-size: 0.9rem;
        line-height: 1.6;
    }}
    .mini-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 7px 0;
        border-bottom: 1px dashed #EFE5E8;
        font-size: 0.95rem;
    }}
    .mini-row:last-child {{ border-bottom: none; }}
    .badge {{
        display: inline-block;
        border-radius: 999px;
        padding: 4px 10px;
        font-size: 0.83rem;
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
        font-size: 0.84rem;
    }}
    .stats-num {{
        margin-top: 4px;
        font-size: 1.5rem;
        font-weight: 800;
        color: #453A3D;
    }}
    .progress-row {{
        display: grid;
        grid-template-columns: 78px 1fr 46px;
        gap: 10px;
        align-items: center;
        margin: 8px 0;
        font-size: 0.9rem;
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
    .control-strip {{
        background: {PINK_BG};
        border: 1px solid {LINE};
        border-radius: 16px;
        padding: 14px 16px;
        margin-bottom: 14px;
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
        font-size: 1.7rem;
        font-weight: 700;
        color: #403638;
    }}
    .day-header-date {{
        font-size: 0.92rem;
        color: #6E6467;
        font-weight: 700;
    }}
    .day-head-row {{
        display: grid;
        grid-template-columns: 1fr 94px;
        gap: 12px;
        padding: 11px 15px 8px 15px;
        font-size: 0.92rem;
        font-weight: 700;
        color: #5E5658;
    }}
    .day-list {{
        padding: 0 15px 16px 15px;
        min-height: 260px;
    }}
    .task-row {{
        display: grid;
        grid-template-columns: 1fr 94px;
        gap: 12px;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px dashed #F0E6E9;
        font-size: 0.95rem;
    }}
    .task-row:last-child {{ border-bottom: none; }}
    .task-name {{
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .checkbox {{
        width: 14px;
        height: 14px;
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
        font-size: 1.35rem;
        font-weight: 700;
        color: #9A7270;
        margin-bottom: 14px;
    }}
    .footer-strip {{
        margin-top: 18px;
        background: {LAVENDER};
        border-radius: 16px;
        padding: 12px 18px;
        color: #5F5659;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.92rem;
    }}
    div[data-testid="stSelectbox"] > div {{
        border-radius: 12px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# Data helpers
# =========================
DEFAULT_CSV = "tasks.csv"


def create_sample_csv(path: str):
    sample = pd.DataFrame(
        [
            [1, "日文 L35", "學習成長", "未完成", "2026-04-21", "W17", "Mon", ""],
            [2, "神經解剖複習", "學習成長", "進行中", "2026-04-21", "W17", "Mon", ""],
            [3, "英單 30 個", "學習成長", "已完成", "2026-04-21", "W17", "Mon", ""],
            [4, "洗衣服", "日常生活", "已完成", "2026-04-21", "W17", "Mon", ""],
            [5, "整理房間", "日常生活", "未完成", "2026-04-21", "W17", "Mon", ""],
            [6, "散步 30 分鐘", "自我照顧", "進行中", "2026-04-21", "W17", "Mon", ""],
            [7, "日文 L36", "學習成長", "未完成", "2026-04-22", "W17", "Tue", ""],
            [8, "閱讀 30 分鐘", "學習成長", "進行中", "2026-04-22", "W17", "Tue", ""],
            [9, "晚餐備餐", "日常生活", "未完成", "2026-04-22", "W17", "Tue", ""],
            [10, "倒垃圾", "日常生活", "未完成", "2026-04-22", "W17", "Tue", ""],
            [11, "冥想 10 分鐘", "自我照顧", "已完成", "2026-04-22", "W17", "Tue", ""],
            [12, "日文 L37", "學習成長", "未完成", "2026-04-23", "W17", "Wed", ""],
            [13, "英單 30 個", "學習成長", "進行中", "2026-04-23", "W17", "Wed", ""],
            [14, "整理筆記", "學習成長", "進行中", "2026-04-23", "W17", "Wed", ""],
            [15, "超市採買", "日常生活", "未完成", "2026-04-23", "W17", "Wed", ""],
            [16, "運動 20 分鐘", "自我照顧", "未完成", "2026-04-23", "W17", "Wed", ""],
            [17, "日文 L38", "學習成長", "未完成", "2026-04-24", "W17", "Thu", ""],
            [18, "神經生理複習", "學習成長", "進行中", "2026-04-24", "W17", "Thu", ""],
            [19, "閱讀 30 分鐘", "學習成長", "未完成", "2026-04-24", "W17", "Thu", ""],
            [20, "衣物整理", "日常生活", "未完成", "2026-04-24", "W17", "Thu", ""],
            [21, "伸展 15 分鐘", "自我照顧", "進行中", "2026-04-24", "W17", "Thu", ""],
            [22, "日文 L39", "學習成長", "未完成", "2026-04-25", "W17", "Fri", ""],
            [23, "英單 30 個", "學習成長", "進行中", "2026-04-25", "W17", "Fri", ""],
            [24, "專題報告", "學習成長", "未完成", "2026-04-25", "W17", "Fri", ""],
            [25, "打掃客廳", "日常生活", "未完成", "2026-04-25", "W17", "Fri", ""],
            [26, "瑜伽 20 分鐘", "自我照顧", "進行中", "2026-04-25", "W17", "Fri", ""],
            [27, "複習本週內容", "學習成長", "進行中", "2026-04-26", "W17", "Sat", ""],
            [28, "整理書櫃", "日常生活", "未完成", "2026-04-26", "W17", "Sat", ""],
            [29, "採買生活用品", "日常生活", "未完成", "2026-04-26", "W17", "Sat", ""],
            [30, "追劇 1 集", "自我照顧", "已完成", "2026-04-26", "W17", "Sat", ""],
            [31, "早睡 11 點", "自我照顧", "未完成", "2026-04-26", "W17", "Sat", ""],
            [32, "下週計畫", "學習成長", "進行中", "2026-04-27", "W17", "Sun", ""],
            [33, "日文複習總整理", "學習成長", "未完成", "2026-04-27", "W17", "Sun", ""],
            [34, "洗床單", "日常生活", "未完成", "2026-04-27", "W17", "Sun", ""],
            [35, "散步 30 分鐘", "自我照顧", "進行中", "2026-04-27", "W17", "Sun", ""],
            [36, "早睡 11 點", "自我照顧", "未完成", "2026-04-27", "W17", "Sun", ""],
        ],
        columns=["id", "task_name", "category", "status", "date", "week", "weekday", "note"],
    )
    sample.to_csv(path, index=False)


@st.cache_data
def load_data(path: str = DEFAULT_CSV) -> pd.DataFrame:
    if not Path(path).exists():
        create_sample_csv(path)
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def normalize_task_dates(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    dt = pd.to_datetime(frame["date"])

    iso = dt.dt.isocalendar()
    frame["iso_year"] = iso.year.astype(int)
    frame["week"] = "W" + iso.week.astype(str)
    frame["weekday"] = dt.dt.strftime("%a")

    return frame

df = normalize_task_dates(load_data())

# =========================
# Sidebar: simple uploader
# =========================
with st.sidebar:
    st.markdown("### 資料來源")
    uploaded = st.file_uploader("上傳 tasks.csv 覆蓋示例資料", type=["csv"])
    if uploaded is not None:
        up_df = pd.read_csv(uploaded)
        up_df.to_csv(DEFAULT_CSV, index=False)
        st.cache_data.clear()
        st.success("已更新資料，重新整理頁面即可。")
    st.markdown("---")
    st.markdown("**CSV 必備欄位**")
    st.code("id,task_name,category,status,date,week,weekday,note", language="text")

# =========================
# Helpers
# =========================
def get_week_options(year: int):
    last_week = date(year, 12, 28).isocalendar().week
    return [f"W{i}" for i in range(1, last_week + 1)]
    
def get_year_options(frame: pd.DataFrame):
    years = sorted(frame["iso_year"].dropna().unique().tolist())
    current_year = datetime.today().year
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
            <div style="text-align:center; font-size:1.45rem; font-weight:700; margin-bottom:10px;">{year} 年 {month} 月</div>
            <div class="calendar-grid">{''.join(cells)}</div>
            <div style="margin-top:14px; background:{CREAM}; border-radius:12px; padding:10px 12px; color:#6D6466; font-size:0.92rem;">
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
            content = "".join(
                f'<div class="mini-row"><span>☐ {row.task_name}</span>{badge(row.status)}</div>'
                for row in cat_df.itertuples()
            )

        block_html = (
            '<div style="background:rgba(255,255,255,0.45); '
            'border:1px solid #D7E0EF; border-radius:14px; padding:12px;">'
            f'<div style="text-align:center; font-weight:700; margin-bottom:10px;">{cat}</div>'
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
        '<div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px;">'
        f'{"".join(blocks)}'
        '</div>'
        '</div>'
        '</div>'
    )

def render_summary_card(frame: pd.DataFrame, selected_week: str):
    subset = frame[frame["week"] == selected_week]
    total = len(subset)
    done = int((subset["status"] == "已完成").sum())
    doing = int((subset["status"] == "進行中").sum())
    todo = int((subset["status"] == "未完成").sum())

    cat_counts = {
        "學習成長": int((subset["category"] == "學習成長").sum()),
        "日常生活": int((subset["category"] == "日常生活").sum()),
        "自我照顧": int((subset["category"] == "自我照顧").sum()),
    }
    max_count = max(cat_counts.values()) if cat_counts else 1
    rows = []
    for label, value in cat_counts.items():
        width = 0 if max_count == 0 else int(value / max_count * 100)
        rows.append(
            f'''
            <div class="progress-row">
                <div>{label}</div>
                <div class="bar-bg"><div class="bar-fill" style="width:{width}%; background:{CATEGORY_BAR[label]};"></div></div>
                <div style="text-align:right;">{value}</div>
            </div>
            '''
        )
    return f"""
    <div class="shell-card">
        <div class="card-title summary-title">📊 本週任務摘要 ({selected_week})</div>
        <div class="card-body">
            <div class="stats-grid">
                <div class="stats-box"><div class="stats-label">總任務</div><div class="stats-num">{total}</div></div>
                <div class="stats-box"><div class="stats-label" style="color:#5E8A57;">已完成</div><div class="stats-num" style="color:#5E8A57;">{done}</div></div>
                <div class="stats-box"><div class="stats-label" style="color:#A87B16;">進行中</div><div class="stats-num" style="color:#A87B16;">{doing}</div></div>
                <div class="stats-box"><div class="stats-label" style="color:#BE7484;">未完成</div><div class="stats-num" style="color:#BE7484;">{todo}</div></div>
            </div>
            <div style="font-weight:700; color:#685A87; margin: 6px 0 8px 0;">依分類統計</div>
            {''.join(rows)}
            <div style="margin-top:14px; padding:12px; border-radius:12px; background:#F8F5FF;">🌙 本週目標：保持節奏，穩定前進</div>
        </div>
    </div>
    """


def render_day_card(day_name: str, day_date: date | None, frame: pd.DataFrame, selected_week: str):
    subset = frame[(frame["week"] == selected_week) & (frame["weekday"] == day_name)]
    date_str = f"{day_date.month}/{day_date.day}" if day_date else "--/--"

    if subset.empty:
        rows = '<div class="small-note">這一天目前沒有任務，可以留白或新增安排。</div>'
    else:
        rows = "".join(
            f'<div class="task-row">'
            f'<div class="task-name"><span class="checkbox"></span><span>{row.task_name}</span></div>'
            f'<div>{badge(row.status)}</div>'
            f'</div>'
            for row in subset.itertuples()
        )

    return (
        '<div class="day-card">'
        '<div class="day-header">'
        f'<div class="day-header-title">{day_name}.</div>'
        f'<div class="day-header-date">{date_str}</div>'
        '</div>'
        '<div class="day-head-row"><div>任務項目</div><div>狀態</div></div>'
        f'<div class="day-list">{rows}</div>'
        '</div>'
    )
# =========================
# State
# =========================
week_options = get_week_options(df)
if not week_options:
    st.stop()

# default choose current week if exists
current_week = "W" + str(datetime.today().isocalendar().week)
default_index = week_options.index(current_week) if current_week in week_options else 0

if "selected_week" not in st.session_state:
    st.session_state.selected_week = week_options[default_index]

selected_week = st.session_state.selected_week
monday, sunday = get_week_range(df, selected_week)
focus_day = monday
focus_year = monday.year
focus_month = monday.month

# =========================
# Top banner
# =========================
st.markdown(
    f'''
    <div class="top-wrap">
        <div>
            <div class="top-title">Weekly Planning Dashboard ✧</div>
            <div class="top-sub">小小的進步，累積成更好的自己。</div>
        </div>
        <div class="top-sub">{focus_year} / {calendar.month_abbr[focus_month]} &nbsp;&nbsp;|&nbsp;&nbsp; {selected_week} &nbsp;&nbsp;|&nbsp;&nbsp; Today: {date.today().strftime('%b %d (%a)')}</div>
    </div>
    ''',
    unsafe_allow_html=True,
)

# =========================
# Layout
# =========================
left_col, right_col = st.columns([1.05, 2.55], gap="large")

with left_col:
    st.markdown(render_calendar_html(focus_year, focus_month, date.today(), selected_week, monday, sunday), unsafe_allow_html=True)
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    st.markdown(render_today_card(df, date.today()), unsafe_allow_html=True)
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    st.markdown(render_summary_card(df, selected_week), unsafe_allow_html=True)

with right_col:
    c1, c2, c3 = st.columns([1.2, 1.1, 1.4])
    with c1:
        st.markdown('<div class="small-note" style="margin-top:8px;">本週目標：持續進步，累積成更好的自己。</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div style="margin-bottom:4px; font-weight:700; color:#6C6064; text-align:center;">週次選擇</div>', unsafe_allow_html=True)
        chosen = st.selectbox("週次", week_options, index=week_options.index(selected_week), label_visibility="collapsed")
        st.session_state.selected_week = chosen
        selected_week = chosen
        monday, sunday = get_week_range(df, selected_week)
    with c3:
        st.markdown(
            f'<div style="text-align:right; margin-top:10px;"><div style="font-size:1.1rem; font-weight:700; color:#413739;">{monday.year} / {calendar.month_abbr[monday.month]} / 第 {selected_week.replace("W", "")} 週</div><div class="small-note">{monday.month}/{monday.day} ({monday.strftime("%a")}) - {sunday.month}/{sunday.day} ({sunday.strftime("%a")})</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

    week_dates = [monday + timedelta(days=i) for i in range(7)]

    top_days = st.columns(4, gap="medium")
    for idx, day_name in enumerate(["Mon", "Tue", "Wed", "Thu"]):
        with top_days[idx]:
            st.markdown(render_day_card(day_name, week_dates[idx], df, selected_week), unsafe_allow_html=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    bottom_left, bottom_mid, bottom_right, memo_col = st.columns([1, 1, 1, 0.82], gap="medium")
    with bottom_left:
        st.markdown(render_day_card("Fri", week_dates[4], df, selected_week), unsafe_allow_html=True)
    with bottom_mid:
        st.markdown(render_day_card("Sat", week_dates[5], df, selected_week), unsafe_allow_html=True)
    with bottom_right:
        st.markdown(render_day_card("Sun", week_dates[6], df, selected_week), unsafe_allow_html=True)
    with memo_col:
        st.markdown(
            '''
            <div class="memo-box">
                <div class="memo-title">本週備註 ♡</div>
                <div class="small-note">
                    專注在重要的事，<br>
                    不追求完美，<br>
                    但求每天有進步。<br><br>
                    可以把這裡留給：<br>
                    • 本週提醒<br>
                    • 小小反思<br>
                    • 想記住的一句話
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

st.markdown(
    '''
    <div class="footer-strip">
        <div>快速切換：任務總表　｜　月統計　｜　年計畫　｜　設定</div>
        <div>週次切換後，右側與統計會同步更新</div>
    </div>
    ''',
    unsafe_allow_html=True,
)

with st.expander("查看目前使用的資料表"):
    st.dataframe(df, use_container_width=True)
