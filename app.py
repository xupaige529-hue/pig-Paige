import streamlit as st
import numpy as np
import matplotlib
try:
    matplotlib.use("Agg")
except Exception:
    pass
import matplotlib.pyplot as plt
from matplotlib import font_manager
from math import comb, factorial, sqrt, pi, exp, erf, gamma
import os
import csv
import base64
import urllib.request
from io import BytesIO, StringIO

# ======================================================================
# 1. 中文字体自动处理（解决图表中文显示为方框的问题）
#    优先级：系统已安装字体 -> 项目目录已有字体文件 -> 自动联网下载
# ======================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_FILE_OTF = os.path.join(BASE_DIR, "cjk_font.otf")
FONT_FILE_TTF = os.path.join(BASE_DIR, "cjk_font.ttf")
LOGO_PATH = os.path.join(BASE_DIR, "nenu_logo.jpg")


def _pick_cjk_font():
    """按优先级探测系统已安装的中文字体，找不到返回 None。"""
    preferred = [
        "Microsoft YaHei", "SimHei", "黑体",
        "PingFang SC", "Hiragino Sans GB", "Heiti SC", "STHeiti",
        "Noto Sans CJK SC", "Noto Sans SC", "Source Han Sans SC",
        "WenQuanYi Micro Hei", "WenQuanYi Zen Hei", "Arial Unicode MS",
    ]
    try:
        available = {f.name for f in font_manager.fontManager.ttflist}
    except Exception:
        available = set()
    for name in preferred:
        if name in available:
            return name
    return None


def _register_local_font():
    """注册项目目录中已存在的字体文件（可避免每次联网下载）。"""
    for fp in (FONT_FILE_OTF, FONT_FILE_TTF):
        if os.path.exists(fp):
            try:
                font_manager.fontManager.addfont(fp)
                return font_manager.FontProperties(fname=fp).get_name()
            except Exception:
                continue
    return None


def _download_font():
    """云端服务器通常没有中文字体，自动下载并注册一款（仅首次需要）。"""
    sources = [
        (FONT_FILE_OTF,
         "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf"),
        (FONT_FILE_OTF,
         "https://raw.githubusercontent.com/googlefonts/noto-cjk/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf"),
        (FONT_FILE_TTF,
         "https://raw.githubusercontent.com/StellarCN/scp_zh/master/fonts/SimHei.ttf"),
    ]
    for fp, url in sources:
        try:
            with urllib.request.urlopen(url, timeout=30) as resp, open(fp, "wb") as out:
                out.write(resp.read())
            if os.path.getsize(fp) > 500_000:   # 有效字体文件通常大于 0.5MB
                font_manager.fontManager.addfont(fp)
                return font_manager.FontProperties(fname=fp).get_name()
        except Exception:
            continue
    return None


CJK_FONT = _pick_cjk_font()
if CJK_FONT is None:
    CJK_FONT = _register_local_font()

# ======================================================================
# 2. 页面配置（必须是第一个 Streamlit 命令）
# ======================================================================
st.set_page_config(
    page_title="数智统计实验室",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else None,
    layout="wide",
)

# 需要时才自动下载字体（放在页面配置之后，便于显示进度提示）
if CJK_FONT is None:
    with st.spinner("首次运行：正在自动下载中文字体（约需数秒）…"):
        CJK_FONT = _download_font()

# ======================================================================
# 3. matplotlib 全局样式（含中文字体回退）
# ======================================================================
_FALLBACK = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ([CJK_FONT] if CJK_FONT else []) + _FALLBACK,
    "axes.unicode_minus": False,          # 负号正常显示
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.titlecolor": "#1e293b",
    "axes.labelsize": 10.5,
    "axes.labelcolor": "#334155",
    "axes.edgecolor": "#cbd5e1",
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "xtick.color": "#64748b",
    "ytick.color": "#64748b",
    "legend.fontsize": 9.5,
    "legend.frameon": False,
    "grid.color": "#e2e8f0",
    "grid.linewidth": 0.8,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
})

# numpy 2.x 兼容
_trapz = getattr(np, "trapezoid", None)
if _trapz is None:
    _trapz = np.trapz

# ======================================================================
# 4. 全局样式（CSS）
# ======================================================================
st.markdown(
    """
    <style>
    /* ---------- 全局字体栈：优先中文无衬线 ---------- */
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        font-family: "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB",
                     "Noto Sans SC", "Source Han Sans SC", "WenQuanYi Micro Hei",
                     "Helvetica Neue", Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
    }
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li { font-size: 0.95rem; line-height: 1.75; }
    code, pre, kbd { font-family: "JetBrains Mono", "Cascadia Code", Consolas,
                     "Microsoft YaHei", monospace !important; }

    /* ---------- 布局 ---------- */
    .block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1480px; }

    /* ---------- 标题 ---------- */
    h1, h2, h3 { letter-spacing: .3px; }
    h1 {
        background: linear-gradient(92deg, #6366f1 0%, #38bdf8 55%, #22d3ee 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        color: transparent;
        font-weight: 800;
        margin: 0;
    }

    /* ---------- Hero 头部 ---------- */
    .hero {
        display: flex; align-items: center; gap: 16px;
        padding: 18px 22px; border-radius: 18px;
        background: linear-gradient(120deg, rgba(99,102,241,.10), rgba(56,189,248,.10));
        border: 1px solid rgba(99,102,241,.20);
    }
    .hero img { width: 62px; height: 62px; border-radius: 12px; flex: 0 0 auto;
                object-fit: contain; background: #fff; padding: 3px; }
    .hero-sub { color: #64748b; font-size: .88rem; margin-top: 4px; letter-spacing: .2px; }

    /* ---------- 侧边栏 ---------- */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(128,128,128,.16);
        background: linear-gradient(180deg, rgba(99,102,241,.055), transparent 42%);
    }

    /* ---------- 按钮 ---------- */
    .stButton > button, .stDownloadButton > button {
        border-radius: 10px; font-weight: 600; transition: all .18s ease;
        border: 1px solid rgba(99,102,241,.35);
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(99,102,241,.22);
        border-color: rgba(99,102,241,.6);
    }

    /* ---------- 指标卡 ---------- */
    [data-testid="stMetric"] {
        background: linear-gradient(160deg, rgba(99,102,241,.085), rgba(56,189,248,.045));
        border: 1px solid rgba(99,102,241,.18);
        border-radius: 14px;
        padding: 13px 16px;
    }
    [data-testid="stMetricLabel"] { font-size: .82rem; color: #64748b; }
    [data-testid="stMetricValue"] { font-weight: 700; letter-spacing: .3px; }

    /* ---------- 展开面板 ---------- */
    [data-testid="stExpander"] {
        border-radius: 12px !important;
        border: 1px solid rgba(128,128,128,.18) !important;
        overflow: hidden;
    }
    [data-testid="stExpander"] summary { font-weight: 600; }

    /* ---------- 自定义卡片 ---------- */
    .card {
        border-radius: 14px; padding: 15px 18px; margin-bottom: 12px;
        background: rgba(128,128,128,.06);
        border: 1px solid rgba(128,128,128,.16);
        border-left: 4px solid #6366f1;
        transition: all .18s ease;
    }
    .card:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,0,0,.07); }
    .card h4 { margin: 0 0 6px 0; font-size: .98rem; color: #334155; }
    .card p  { margin: 0; color: #64748b; font-size: .87rem; line-height: 1.6; }

    .step-chip {
        display:inline-block; padding: 2px 10px; border-radius: 999px;
        font-size: .78rem; font-weight: 700; margin-right: 6px;
        background: rgba(99,102,241,.12); color: #6366f1;
    }

    .footer-text { color:#94a3b8; font-size:.83rem; line-height:1.7; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ======================================================================
# 5. 顶部 Hero 区（校徽容错：文件不存在不报错）
# ======================================================================
logo_img_html = ""
if os.path.exists(LOGO_PATH):
    try:
        with open(LOGO_PATH, "rb") as f:
            LOGO_B64 = base64.b64encode(f.read()).decode()
        logo_img_html = (
            f'<img src="data:image/jpeg;base64,{LOGO_B64}" alt="东北师范大学校徽" />'
        )
    except Exception:
        logo_img_html = ""

st.markdown(
    f"""
    <div class="hero">
        {logo_img_html}
        <div>
            <h1 style="font-size:1.95rem;">数智统计实验室</h1>
            <div class="hero-sub">
                AI 赋能统计学交互式教学资源原型 ｜ 概率分布 · 随机抽样 · 中心极限定理 · 置信区间 · 假设检验
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

# ======================================================================
# 6. 通用工具函数
# ======================================================================
def normal_pdf(x, mu, sigma):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))


def normal_cdf(x, mu, sigma):
    return 0.5 * (1.0 + erf((x - mu) / (sigma * np.sqrt(2.0))))


def norm_ppf(q):
    """标准正态分布分位数（二分法近似，无需 scipy）。"""
    lo_, hi_ = -8.0, 8.0
    for _ in range(100):
        mid = 0.5 * (lo_ + hi_)
        if normal_cdf(mid, 0.0, 1.0) < q:
            lo_ = mid
        else:
            hi_ = mid
    return 0.5 * (lo_ + hi_)


def t_pdf(x, df):
    coef = gamma((df + 1) / 2.0) / (np.sqrt(df * pi) * gamma(df / 2.0))
    return coef * (1.0 + x * x / df) ** (-(df + 1) / 2.0)


def chi2_pdf(x, k):
    x = np.asarray(x, dtype=float)
    out = np.zeros_like(x)
    m = x > 0
    xm = x[m]
    out[m] = xm ** (k / 2.0 - 1.0) * np.exp(-xm / 2.0) / (2.0 ** (k / 2.0) * gamma(k / 2.0))
    return out


def prob_interval(pdf_func, a, b, n=2001):
    """连续分布区间概率（数值积分）"""
    if b <= a:
        return 0.0
    xs = np.linspace(a, b, n)
    return float(_trapz(pdf_func(xs), xs))


def fig_to_png_bytes(fig, dpi=170):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    buf.seek(0)
    return buf.getvalue()


def polish_axes(ax, title, xlabel, ylabel, grid_axis="both"):
    ax.set_title(title, pad=11)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis=grid_axis, alpha=0.75, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#cbd5e1")


def render_fig(fig, filename, key, caption=None):
    """统一渲染 + 下载按钮"""
    png = fig_to_png_bytes(fig)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    col1, col2 = st.columns([1, 4])
    with col1:
        st.download_button(
            "下载图表 PNG",
            data=png,
            file_name=filename,
            mime="image/png",
            key=key,
            use_container_width=True,
        )
    if caption:
        with col2:
            st.caption(caption)


def four_steps(predict, experiment, observe, explain):
    with st.expander("教学四步法：预测 → 实验 → 观察 → 解释"):
        st.markdown(f'<span class="step-chip">① 预测</span> {predict}', unsafe_allow_html=True)
        st.markdown(f'<span class="step-chip">② 实验</span> {experiment}', unsafe_allow_html=True)
        st.markdown(f'<span class="step-chip">③ 观察</span> {observe}', unsafe_allow_html=True)
        st.markdown(f'<span class="step-chip">④ 解释</span> {explain}', unsafe_allow_html=True)


def interval_calculator(pdf_func, support_lo, support_hi, key_prefix, color="#f97316"):
    """通用区间概率计算器（连续分布）"""
    st.markdown("##### 区间概率计算器")
    c1, c2 = st.columns(2)
    a = c1.number_input(
        "区间下界 a", value=float(np.round(support_lo, 2)), step=0.1,
        key=f"{key_prefix}_a", format="%.2f",
    )
    b = c2.number_input(
        "区间上界 b", value=float(np.round(support_hi, 2)), step=0.1,
        key=f"{key_prefix}_b", format="%.2f",
    )
    p = prob_interval(pdf_func, a, b)
    c1, c2, c3 = st.columns(3)
    c1.metric("下界 a", f"{a:.2f}")
    c2.metric("上界 b", f"{b:.2f}")
    c3.metric(f"P({a:.2f} ≤ X ≤ {b:.2f})", f"{p:.4f}")
    return a, b, p, color


# ======================================================================
# 7. 抽样模拟（带缓存，降低云端算力开销）
# ======================================================================
POP_SPECS = {
    "指数分布 Exp(1)（强右偏）": {"mu": 1.0, "sigma": 1.0},
    "均匀分布 U(0,1)（对称）": {"mu": 0.5, "sigma": sqrt(1.0 / 12.0)},
    "正态分布 N(2,1)（对称）": {"mu": 2.0, "sigma": 1.0},
    "对数正态 LN(0,0.8)（重尾）": {
        "mu": exp(0.32),
        "sigma": sqrt((exp(0.64) - 1.0) * exp(0.64)),
    },
    "双峰混合分布（0.5N(-1,.4²)+0.5N(1,.4²)）": {"mu": 0.0, "sigma": sqrt(1.16)},
}


@st.cache_data(show_spinner="正在模拟抽样，请稍候…")
def sampling_simulation(pop_key, sample_size, repeats, seed):
    rng = np.random.default_rng(int(seed))
    if pop_key == "指数分布 Exp(1)（强右偏）":
        mat = rng.exponential(scale=1.0, size=(repeats, sample_size))
    elif pop_key == "均匀分布 U(0,1)（对称）":
        mat = rng.uniform(low=0.0, high=1.0, size=(repeats, sample_size))
    elif pop_key == "正态分布 N(2,1)（对称）":
        mat = rng.normal(loc=2.0, scale=1.0, size=(repeats, sample_size))
    elif pop_key == "对数正态 LN(0,0.8)（重尾）":
        mat = rng.lognormal(mean=0.0, sigma=0.8, size=(repeats, sample_size))
    else:  # 双峰混合
        half = repeats // 2
        a = rng.normal(loc=-1.0, scale=0.4, size=(half, sample_size))
        b = rng.normal(loc=1.0, scale=0.4, size=(repeats - half, sample_size))
        mat = np.vstack([a, b])
        rng.shuffle(mat, axis=0)
    return mat.mean(axis=1)


@st.cache_data(show_spinner="正在模拟大数定律…")
def lln_simulation(pop_key, n_max, seed):
    rng = np.random.default_rng(int(seed))
    if pop_key == "指数分布 Exp(1)":
        data = rng.exponential(scale=1.0, size=n_max)
        mu = 1.0
    elif pop_key == "均匀分布 U(0,1)":
        data = rng.uniform(low=0.0, high=1.0, size=n_max)
        mu = 0.5
    elif pop_key == "伯努利分布 B(1, 0.3)":
        data = rng.binomial(1, 0.3, size=n_max)
        mu = 0.3
    else:  # 正态分布 N(2,1)
        data = rng.normal(loc=2.0, scale=1.0, size=n_max)
        mu = 2.0
    running = np.cumsum(data) / np.arange(1, n_max + 1)
    return running, mu


@st.cache_data(show_spinner="正在模拟置信区间…")
def ci_simulation(n, k, conf, seed):
    rng = np.random.default_rng(int(seed))
    z = {"90%": 1.645, "95%": 1.96, "99%": 2.576}[conf]
    means = rng.normal(loc=0.0, scale=1.0, size=(k, n)).mean(axis=1)
    se = 1.0 / sqrt(n)
    lo = means - z * se
    hi = means + z * se
    covered = (lo <= 0.0) & (hi >= 0.0)
    return lo, hi, covered


@st.cache_data(show_spinner="正在生成样本…")
def draw_normal_sample(mu_true, sigma, n, seed):
    rng = np.random.default_rng(int(seed))
    return rng.normal(loc=mu_true, scale=sigma, size=n)


# ======================================================================
# 8. 侧边栏导航
# ======================================================================
MODULES = [
    "学习地图",
    "模块一：概率分布实验室",
    "模块二：抽样与中心极限定理",
    "模块三：自测与分步学习助手",
    "模块四：大数定律演示",
    "模块五：置信区间模拟",
    "模块六：假设检验 z 检验演示",
]

with st.sidebar:
    st.markdown("### 学习导航")
    module = st.radio("选择学习模块", MODULES, label_visibility="collapsed")
    st.divider()
    st.markdown("**教学路径**")
    st.markdown(
        "① 先预测　→　② 再实验\n\n"
        "③ 细观察　→　④ 说原因"
    )
    st.divider()
    with st.expander("使用说明", expanded=False):
        st.write(
            "每个模块都配有「教学四步法」提示，建议先自己想，再拖滑块验证。\n\n"
            "图表可下载为 PNG，模块二还可导出抽样数据 CSV。\n\n"
            "模块三为本地规则判分，不联网、不上传任何内容。"
        )
    if CJK_FONT is None:
        st.warning("未能自动获取中文字体，图表中文可能显示为方框。可将中文字体文件（如 SimHei.ttf）重命名为 cjk_font.ttf 上传到项目目录。")
    else:
        st.caption(f"图表中文字体：{CJK_FONT}")

# ======================================================================
# 9. 模块〇：学习地图
# ======================================================================
if module == "学习地图":
    st.header("学习地图")
    st.write("六个模块串成一条完整的探究路径：**认识分布 → 理解抽样 → 检验理解 → 走向推断**。")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """<div class="card">
            <h4>模块一 · 概率分布实验室</h4>
            <p>调节 μ、σ、n、p、λ 等参数，观察 7 种概率分布的形态变化，并用区间概率计算器验证「曲线下面积 = 概率」。</p>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """<div class="card" style="border-left-color:#38bdf8;">
            <h4>模块二 · 抽样与中心极限定理</h4>
            <p>从指数、对数正态、双峰等总体中反复抽样，观察样本均值分布如何随 n 增大而收敛到正态。</p>
            </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """<div class="card" style="border-left-color:#f97316;">
            <h4>模块三 · 自测与分步助手</h4>
            <p>6 道概念自测题即时判分并给出错题回溯路径，还可生成可复制的 AI 助教追问提示词。</p>
            </div>""",
            unsafe_allow_html=True,
        )

    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(
            """<div class="card" style="border-left-color:#10b981;">
            <h4>模块四 · 大数定律演示</h4>
            <p>样本量越大，样本均值越接近总体均值，直观体会「频率稳定于概率」。</p>
            </div>""",
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            """<div class="card" style="border-left-color:#a855f7;">
            <h4>模块五 · 置信区间模拟</h4>
            <p>重复抽样构造置信区间，验证约 95% 的区间确实包含总体均值。</p>
            </div>""",
            unsafe_allow_html=True,
        )
    with c6:
        st.markdown(
            """<div class="card" style="border-left-color:#ec4899;">
            <h4>模块六 · 假设检验 z 检验</h4>
            <p>已知总体标准差时检验样本均值是否显著偏离原假设，理解 p 值与显著性水平。</p>
            </div>""",
            unsafe_allow_html=True,
        )

    st.divider()
    st.subheader("建议学习顺序")
    st.markdown(
        """
1. **先做预测**：读题干后，先在纸上写下你的判断（这一步最容易忽略，却最关键）。
2. **动手实验**：拖动滑块 / 改变样本量，让图像"回答"你的问题。
3. **记录观察**：关注曲线的**中心位置、宽度、峰值高度、对称性**四个特征。
4. **给出解释**：用参数的含义（μ、σ、n、p、λ）说明你看到的现象。
5. **走向推断**：在模块四至六体会大数定律、置信区间与假设检验如何用于实际判断。
        """
    )

    with st.expander("本实验涉及的核心结论"):
        st.markdown(
            """
- **正态分布**：μ 决定中心位置，σ 决定离散程度；曲线关于 μ 对称，总面积为 1。
- **二项分布**：E(X)=np，Var(X)=np(1−p)；p 越接近 0.5 越对称。
- **泊松分布**：E(X)=Var(X)=λ，描述单位时间/空间内的稀有事件计数。
- **标准误**：SE = σ/√n，样本量变为 4 倍，标准误减半。
- **中心极限定理**：n 足够大时，样本均值近似服从正态分布，与总体是否正态无关（需有限方差）。
- **大数定律**：样本均值依概率收敛于总体均值，样本量越大偏差越小。
- **置信区间**：约 95% 的置信区间包含真实参数；覆盖率会围绕名义水平随机波动。
- **假设检验**：p 值小于 α 时拒绝原假设；「不拒绝」不等于「接受」。
            """
        )

# ======================================================================
# 10. 模块一：概率分布实验室
# ======================================================================
elif module == "模块一：概率分布实验室":
    st.header("模块一｜概率分布实验室")
    st.write("通过调整参数，观察分布形态如何变化。建议**先预测曲线变化，再移动参数验证**。")

    dist = st.selectbox(
        "选择分布",
        [
            "正态分布 N(μ, σ²)",
            "二项分布 B(n, p)",
            "泊松分布 P(λ)",
            "均匀分布 U(a, b)",
            "指数分布 Exp(λ)",
            "t 分布 t(df)",
            "卡方分布 χ²(k)",
        ],
    )

    # ---------------- 正态分布 ----------------
    if dist == "正态分布 N(μ, σ²)":
        c1, c2 = st.columns(2)
        mu = c1.slider("均值 μ（决定中心位置）", -5.0, 5.0, 0.0, 0.5)
        sigma = c2.slider("标准差 σ（决定离散程度）", 0.2, 3.0, 1.0, 0.1)

        lo, hi = mu - 6 * sigma, mu + 6 * sigma
        x = np.linspace(lo, hi, 900)
        y = normal_pdf(x, mu, sigma)
        pdf_func = lambda t: normal_pdf(t, mu, sigma)

        st.markdown("##### 区间概率计算器")
        cc1, cc2 = st.columns(2)
        a = cc1.number_input("区间下界 a", value=float(np.round(mu - sigma, 2)), step=0.1,
                             key="norm_a", format="%.2f")
        b = cc2.number_input("区间上界 b", value=float(np.round(mu + sigma, 2)), step=0.1,
                             key="norm_b", format="%.2f")
        p_area = max(0.0, normal_cdf(b, mu, sigma) - normal_cdf(a, mu, sigma))

        fig, ax = plt.subplots(figsize=(9.8, 4.0))
        ax.plot(x, y, lw=2.6, color="#6366f1", zorder=3, label="概率密度 f(x)")
        ax.fill_between(x, y, color="#6366f1", alpha=0.12, zorder=2)
        mask = (x >= a) & (x <= b)
        if mask.sum() > 1:
            ax.fill_between(x[mask], y[mask], color="#f97316", alpha=0.42,
                            zorder=4, label=f"P({a:.2f} ≤ X ≤ {b:.2f}) = {p_area:.4f}")
        ax.axvline(mu, color="#f97316", ls="--", lw=1.4, zorder=5, label=f"μ = {mu:.2f}")
        ax.axvline(mu - sigma, color="#94a3b8", ls=":", lw=1.2, zorder=5)
        ax.axvline(mu + sigma, color="#94a3b8", ls=":", lw=1.2, zorder=5, label="μ ± σ")
        polish_axes(ax, f"正态分布 N(μ = {mu:.1f}, σ² = {sigma**2:.2f})",
                    "取值 x", "概率密度 f(x)")
        ax.legend(loc="upper right")
        render_fig(fig, "normal_dist.png", "dl_normal",
                   "提示：阴影面积就是区间概率，总面积恒为 1。")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("均值 μ", f"{mu:.2f}")
        c2.metric("标准差 σ", f"{sigma:.2f}")
        c3.metric("方差 σ²", f"{sigma**2:.2f}")
        c4.metric("峰值高度", f"{1/(sigma*np.sqrt(2*np.pi)):.3f}")

        four_steps(
            "先别动滑块——如果 σ 不变、μ 增大，曲线整体会往哪边移动？",
            "拖动 μ 和 σ 的滑块，观察曲线实际变化。",
            "注意曲线中心（μ）、宽度与峰值高度（σ）的变化，以及阴影面积。",
            "μ 决定分布中心；σ 越大数据越分散、曲线越矮胖；曲线下总面积恒为 1。",
        )

        st.markdown("**观察任务**")
        st.write("1. 保持 σ 不变、改变 μ：曲线位置发生什么变化？")
        st.write("2. 保持 μ 不变、增大 σ：曲线的高度和宽度如何变化？")
        st.write("3. 把区间设成 [μ−σ, μ+σ]，概率大约是多少？换成 [μ−2σ, μ+2σ] 呢？")

        with st.expander("查看分步提示"):
            st.write("提示1：均值描述分布的中心位置。")
            st.write("提示2：标准差描述数据围绕均值的离散程度。")
            st.write("提示3：正态曲线关于均值对称，曲线下总面积为 1。")
            st.write("提示4：理论值约为 68.27% 与 95.45%（经验法则）。")

    # ---------------- 二项分布 ----------------
    elif dist == "二项分布 B(n, p)":
        c1, c2 = st.columns(2)
        n = c1.slider("试验次数 n", 1, 50, 10)
        p = c2.slider("单次成功概率 p", 0.05, 0.95, 0.5, 0.05)

        xs = np.arange(n + 1)
        probs = np.array([comb(n, int(k)) * (p ** k) * ((1 - p) ** (n - k)) for k in xs])
        mu_b = n * p
        sd_b = sqrt(n * p * (1 - p)) if 0 < p < 1 else 0.0

        st.markdown("##### 区间概率计算器（离散求和）")
        cc1, cc2 = st.columns(2)
        a = int(cc1.number_input("下界 k₁（整数）", min_value=0, max_value=n,
                                 value=max(0, int(np.floor(mu_b - sd_b))), step=1, key="bin_a"))
        b = int(cc2.number_input("上界 k₂（整数）", min_value=0, max_value=n,
                                 value=min(n, int(np.ceil(mu_b + sd_b))), step=1, key="bin_b"))
        if b < a:
            a, b = b, a
        p_area = float(probs[a:b + 1].sum())

        fig, ax = plt.subplots(figsize=(9.8, 4.0))
        colors = ["#f97316" if a <= k <= b else "#38bdf8" for k in xs]
        ax.bar(xs, probs, width=0.8, color=colors, edgecolor="white", zorder=3)
        if sd_b > 0:
            x_norm = np.linspace(max(0, mu_b - 4 * sd_b), mu_b + 4 * sd_b, 300)
            ax.plot(x_norm, normal_pdf(x_norm, mu_b, sd_b), lw=2.0, color="#6366f1",
                    zorder=4, label=f"正态近似 N({mu_b:.1f}, {sd_b:.1f}²)")
        ax.axvline(mu_b, color="#10b981", ls="--", lw=1.4, zorder=5, label=f"np = {mu_b:.2f}")
        polish_axes(ax, f"二项分布 B(n = {n}, p = {p:.2f})　｜　P({a} ≤ X ≤ {b}) = {p_area:.4f}",
                    "成功次数 k", "P(X = k)", grid_axis="y")
        ax.legend()
        render_fig(fig, "binomial_dist.png", "dl_binom",
                   "橙色柱为所选区间的概率质量。")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("理论均值 np", f"{mu_b:.2f}")
        c2.metric("理论方差 np(1−p)", f"{n * p * (1 - p):.2f}")
        c3.metric("标准差", f"{sd_b:.3f}")
        c4.metric(f"P({a} ≤ X ≤ {b})", f"{p_area:.4f}")

        four_steps(
            "固定 n，把 p 从 0.1 拉到 0.9，概率质量会向哪边移动？",
            "拖动 p 的滑块，观察条形图与橙色正态近似曲线的变化。",
            "峰值出现在 n·p 附近；p 越接近 0.5，图形越对称，正态近似越好。",
            "p > 0.5 时成功更常见，分布右偏（质量向大 k 移动）；p < 0.5 时左偏。",
        )

        st.markdown("**思考任务**：固定 p、逐渐增大 n，条形轮廓与橙色曲线的贴合程度如何变化？")
        with st.expander("查看分步提示"):
            st.write("提示1：二项分布要求 n 次试验独立、每次只有成功/失败、成功概率恒为 p。")
            st.write("提示2：n 增大且 np 与 n(1−p) 都不太小时，二项分布可用正态分布近似。")
            st.write("提示3：连续性修正——离散分布用正态近似时，边界通常要 ±0.5。")

    # ---------------- 泊松分布 ----------------
    elif dist == "泊松分布 P(λ)":
        lam = st.slider("平均发生率 λ", 0.5, 15.0, 3.0, 0.5)
        kmax = int(lam + 6 * sqrt(lam)) + 5
        xs = np.arange(kmax + 1)
        probs = np.array([exp(-lam) * lam ** k / factorial(k) for k in xs])

        st.markdown("##### 区间概率计算器（离散求和）")
        cc1, cc2 = st.columns(2)
        a = int(cc1.number_input("下界 k₁（整数）", min_value=0, max_value=kmax,
                                 value=max(0, int(lam - sqrt(lam))), step=1, key="poi_a"))
        b = int(cc2.number_input("上界 k₂（整数）", min_value=0, max_value=kmax,
                                 value=min(kmax, int(lam + sqrt(lam))), step=1, key="poi_b"))
        if b < a:
            a, b = b, a
        p_area = float(probs[a:b + 1].sum())

        fig, ax = plt.subplots(figsize=(9.8, 4.0))
        colors = ["#f97316" if a <= k <= b else "#a855f7" for k in xs]
        ax.bar(xs, probs, width=0.8, color=colors, edgecolor="white", zorder=3)
        x_norm = np.linspace(max(0, lam - 4 * sqrt(lam)), lam + 4 * sqrt(lam), 300)
        ax.plot(x_norm, normal_pdf(x_norm, lam, sqrt(lam)), lw=2.0, color="#6366f1",
                zorder=4, label=f"正态近似 N({lam:.1f}, {lam:.1f})")
        ax.axvline(lam, color="#10b981", ls="--", lw=1.4, zorder=5, label=f"λ = {lam:.2f}")
        polish_axes(ax, f"泊松分布 P(λ = {lam:.1f})　｜　P({a} ≤ X ≤ {b}) = {p_area:.4f}",
                    "事件发生次数 k", "P(X = k)", grid_axis="y")
        ax.legend()
        render_fig(fig, "poisson_dist.png", "dl_poisson",
                   "橙色柱为所选区间的概率质量。")

        c1, c2, c3 = st.columns(3)
        c1.metric("理论均值 λ", f"{lam:.2f}")
        c2.metric("理论方差 λ", f"{lam:.2f}")
        c3.metric(f"P({a} ≤ X ≤ {b})", f"{p_area:.4f}")

        four_steps(
            "λ 从 1 增大到 10，条形图会变高还是变宽？",
            "拖动 λ 滑块，观察概率质量如何扩散。",
            "分布中心约等于 λ；λ 越大图形越向右移、越接近对称。",
            "泊松分布描述单位时间/空间内的稀有事件计数，其均值与方差都等于 λ。",
        )

        st.markdown("**思考任务**：λ 增大时，分布整体形态（位置与形状）如何变化？")
        with st.expander("查看分步提示"):
            st.write("提示1：泊松分布是二项分布在 n 很大、p 很小时的极限情形。")
            st.write("提示2：均值与方差相等（均为 λ）是泊松分布的重要特征。")
            st.write("提示3：λ ≥ 10 时正态近似通常已经相当好。")

    # ---------------- 均匀分布 ----------------
    elif dist == "均匀分布 U(a, b)":
        c1, c2 = st.columns(2)
        lo_u = c1.slider("下界 a", -5.0, 5.0, 0.0, 0.5)
        hi_u = c2.slider("上界 b", -5.0, 5.0, 1.0, 0.5)
        if hi_u <= lo_u:
            hi_u = lo_u + 0.5
            st.caption("要求 b > a，已自动调整上界。")

        width = hi_u - lo_u
        height = 1.0 / width
        x = np.linspace(lo_u - 0.8 * width, hi_u + 0.8 * width, 800)
        y = np.where((x >= lo_u) & (x <= hi_u), height, 0.0)

        st.markdown("##### 区间概率计算器")
        cc1, cc2 = st.columns(2)
        a = cc1.number_input("区间下界 a", value=float(np.round(lo_u, 2)), step=0.1,
                             key="uni_a", format="%.2f")
        b = cc2.number_input("区间上界 b", value=float(np.round(hi_u, 2)), step=0.1,
                             key="uni_b", format="%.2f")
        left, right = max(a, lo_u), min(b, hi_u)
        p_area = max(0.0, (right - left) / width) if right > left else 0.0

        fig, ax = plt.subplots(figsize=(9.8, 4.0))
        ax.plot(x, y, lw=2.6, color="#10b981", zorder=3, label="概率密度 f(x)")
        ax.fill_between(x, y, color="#10b981", alpha=0.13, zorder=2)
        if right > left:
            m = (x >= left) & (x <= right)
            ax.fill_between(x[m], y[m], color="#f97316", alpha=0.45, zorder=4,
                            label=f"P({a:.2f} ≤ X ≤ {b:.2f}) = {p_area:.4f}")
        ax.axvline((lo_u + hi_u) / 2, color="#6366f1", ls="--", lw=1.4, zorder=5,
                   label=f"均值 = {(lo_u + hi_u) / 2:.2f}")
        polish_axes(ax, f"均匀分布 U({lo_u:.1f}, {hi_u:.1f})", "取值 x", "概率密度 f(x)")
        ax.legend(loc="upper right")
        render_fig(fig, "uniform_dist.png", "dl_uniform",
                   "均匀分布的概率密度在区间内是常数，形状为矩形。")

        c1, c2, c3 = st.columns(3)
        c1.metric("均值 (a+b)/2", f"{(lo_u + hi_u) / 2:.3f}")
        c2.metric("方差 (b−a)²/12", f"{width**2 / 12:.4f}")
        c3.metric("密度高度 1/(b−a)", f"{height:.3f}")

        four_steps(
            "区间宽度扩大一倍，矩形的高度会怎样变化？",
            "拖动 a、b 滑块，同时观察矩形宽度与高度。",
            "矩形面积始终为 1；宽度越大，高度越低。",
            "均匀分布的密度在区间内恒为 1/(b−a)，区间外为 0，因此概率与区间长度成正比。",
        )

    # ---------------- 指数分布 ----------------
    elif dist == "指数分布 Exp(λ)":
        lam = st.slider("速率参数 λ", 0.1, 3.0, 1.0, 0.1)
        xmax = min(20.0, 8.0 / lam)
        x = np.linspace(1e-6, xmax, 900)
        pdf_func = lambda t: lam * np.exp(-lam * np.asarray(t, dtype=float))
        y = pdf_func(x)

        st.markdown("##### 区间概率计算器")
        cc1, cc2 = st.columns(2)
        a = cc1.number_input("区间下界 a", value=0.0, step=0.1, key="exp_a", format="%.2f")
        b = cc2.number_input("区间上界 b", value=float(np.round(1.0 / lam, 2)), step=0.1,
                             key="exp_b", format="%.2f")
        aa, bb = max(0.0, a), max(0.0, b)
        p_area = max(0.0, (1 - exp(-lam * bb)) - (1 - exp(-lam * aa))) if bb > aa else 0.0

        fig, ax = plt.subplots(figsize=(9.8, 4.0))
        ax.plot(x, y, lw=2.6, color="#ec4899", zorder=3, label="概率密度 f(x)")
        ax.fill_between(x, y, color="#ec4899", alpha=0.12, zorder=2)
        m = (x >= aa) & (x <= bb)
        if m.sum() > 1:
            ax.fill_between(x[m], y[m], color="#f97316", alpha=0.45, zorder=4,
                            label=f"P({aa:.2f} ≤ X ≤ {bb:.2f}) = {p_area:.4f}")
        ax.axvline(1.0 / lam, color="#6366f1", ls="--", lw=1.4, zorder=5,
                   label=f"均值 1/λ = {1/lam:.2f}")
        polish_axes(ax, f"指数分布 Exp(λ = {lam:.1f})", "取值 x", "概率密度 f(x)")
        ax.legend(loc="upper right")
        render_fig(fig, "exponential_dist.png", "dl_exp",
                   "指数分布常用于描述等待时间，具有无记忆性。")

        c1, c2, c3 = st.columns(3)
        c1.metric("均值 1/λ", f"{1/lam:.3f}")
        c2.metric("方差 1/λ²", f"{1/lam**2:.4f}")
        c3.metric("标准差 1/λ", f"{1/lam:.3f}")

        four_steps(
            "λ 增大（事件来得更快），曲线会更陡还是更平？",
            "拖动 λ 滑块，观察曲线下降的速度。",
            "λ 越大，曲线衰减越快，尾部越薄，分布越集中在 0 附近。",
            "指数分布的均值和标准差都等于 1/λ，这是它区别于其他分布的显著特征。",
        )

    # ---------------- t 分布 ----------------
    elif dist == "t 分布 t(df)":
        df = st.slider("自由度 df", 1, 30, 5, 1)
        x = np.linspace(-6, 6, 900)
        y = t_pdf(x, df)
        z = normal_pdf(x, 0, 1)

        st.markdown("##### 区间概率计算器")
        cc1, cc2 = st.columns(2)
        a = cc1.number_input("区间下界 a", value=-2.0, step=0.1, key="t_a", format="%.2f")
        b = cc2.number_input("区间上界 b", value=2.0, step=0.1, key="t_b", format="%.2f")
        p_area = prob_interval(lambda t: t_pdf(t, df), a, b)

        fig, ax = plt.subplots(figsize=(9.8, 4.0))
        ax.plot(x, z, lw=1.8, color="#94a3b8", ls="--", zorder=3, label="标准正态 N(0,1)")
        ax.plot(x, y, lw=2.6, color="#6366f1", zorder=4, label=f"t 分布 df = {df}")
        ax.fill_between(x, y, color="#6366f1", alpha=0.12, zorder=2)
        m = (x >= a) & (x <= b)
        if m.sum() > 1:
            ax.fill_between(x[m], y[m], color="#f97316", alpha=0.45, zorder=5,
                            label=f"P({a:.2f} ≤ T ≤ {b:.2f}) = {p_area:.4f}")
        polish_axes(ax, f"t 分布 t(df = {df}) 与标准正态对比",
                    "取值 t", "概率密度 f(t)")
        ax.legend(loc="upper right")
        render_fig(fig, "t_dist.png", "dl_t",
                   "df 越小，t 分布尾部越厚（峰越低、尾越高）。")

        c1, c2, c3 = st.columns(3)
        c1.metric("自由度 df", f"{df}")
        c2.metric("均值（df>1）", "0" if df > 1 else "不存在")
        c3.metric("方差（df>2）", f"{df / (df - 2):.3f}" if df > 2 else "不存在")

        four_steps(
            "df 很小时，t 分布的尾部比正态更厚还是更薄？",
            "拖动 df 滑块，比较蓝色实线与灰色虚线的差异。",
            "df 越小，峰值越低、尾部越厚；df → ∞ 时 t 分布趋于标准正态。",
            "t 分布用于总体标准差未知、且样本量较小时对均值的推断，它比正态分布更保守。",
        )

    # ---------------- 卡方分布 ----------------
    else:
        k = st.slider("自由度 k", 1, 30, 5, 1)
        xmax = k + 6 * sqrt(2 * k) + 2
        x = np.linspace(1e-4, xmax, 900)
        y = chi2_pdf(x, k)

        st.markdown("##### 区间概率计算器")
        cc1, cc2 = st.columns(2)
        a = cc1.number_input("区间下界 a", value=0.0, step=0.5, key="chi_a", format="%.2f")
        b = cc2.number_input("区间上界 b", value=float(k), step=0.5, key="chi_b", format="%.2f")
        p_area = prob_interval(lambda t: chi2_pdf(t, k), max(0.0, a), b)

        fig, ax = plt.subplots(figsize=(9.8, 4.0))
        ax.plot(x, y, lw=2.6, color="#f97316", zorder=3, label=f"χ² 分布 k = {k}")
        ax.fill_between(x, y, color="#f97316", alpha=0.13, zorder=2)
        m = (x >= max(0.0, a)) & (x <= b)
        if m.sum() > 1:
            ax.fill_between(x[m], y[m], color="#6366f1", alpha=0.42, zorder=4,
                            label=f"P({a:.2f} ≤ X ≤ {b:.2f}) = {p_area:.4f}")
        ax.axvline(k, color="#10b981", ls="--", lw=1.4, zorder=5, label=f"均值 = k = {k}")
        polish_axes(ax, f"卡方分布 χ²(k = {k})", "取值 x", "概率密度 f(x)")
        ax.legend(loc="upper right")
        render_fig(fig, "chi2_dist.png", "dl_chi2",
                   "卡方分布取值非负，随 k 增大逐渐右移并趋于对称。")

        c1, c2, c3 = st.columns(3)
        c1.metric("均值 k", f"{k}")
        c2.metric("方差 2k", f"{2 * k}")
        c3.metric("标准差 √(2k)", f"{sqrt(2 * k):.3f}")

        four_steps(
            "k 增大时，卡方分布的峰值向左还是向右移动？形状是否更对称？",
            "拖动 k 滑块，观察曲线整体形态的变化。",
            "k 越大，曲线越向右移、越对称，也逐渐接近正态形态。",
            "k 个独立标准正态变量的平方和服从 χ²(k)，它常用于方差推断与拟合优度检验。",
        )

# ======================================================================
# 11. 模块二：抽样与中心极限定理
# ======================================================================
elif module == "模块二：抽样与中心极限定理":
    st.header("模块二｜抽样与中心极限定理")
    st.write("从不同总体中重复抽样，观察**样本均值的分布**如何随样本量变化。")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        pop_key = st.selectbox("选择总体类型", list(POP_SPECS.keys()))
    with c2:
        sample_size = st.slider("每次抽样的样本量 n", 2, 200, 30, 1)
    with c3:
        repeats = st.slider("重复抽样次数", 200, 5000, 1000, 100)
    with c4:
        seed = st.number_input("随机种子（便于复现）", min_value=0, max_value=99999,
                               value=2026, step=1)

    sample_means = sampling_simulation(pop_key, sample_size, repeats, seed)
    theo_mu = POP_SPECS[pop_key]["mu"]
    theo_sigma = POP_SPECS[pop_key]["sigma"]
    theo_se = theo_sigma / sqrt(sample_size)

    tab1, tab2 = st.tabs(["样本均值分布", "标准误随 n 的变化"])

    with tab1:
        fig, ax = plt.subplots(figsize=(9.8, 4.1))
        ax.hist(sample_means, bins=40, density=True, alpha=0.78,
                edgecolor="white", color="#38bdf8", zorder=2, label="模拟样本均值")
        xx = np.linspace(sample_means.min(), sample_means.max(), 400)
        ax.plot(xx, normal_pdf(xx, theo_mu, theo_se), lw=2.4, color="#f97316",
                zorder=4, label=f"理论正态 N({theo_mu:.3f}, {theo_se:.4f}²)")
        ax.axvline(sample_means.mean(), color="#10b981", ls="--", lw=1.5,
                   zorder=5, label=f"模拟均值 = {sample_means.mean():.4f}")
        polish_axes(ax, f"样本均值的抽样分布　｜　{pop_key}", "样本均值", "密度")
        ax.legend(loc="upper right")
        render_fig(fig, "clt_sampling.png", "dl_clt_hist",
                   f"n = {sample_size}，重复 {repeats} 次。")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("模拟均值", f"{sample_means.mean():.4f}")
        c2.metric("模拟标准误", f"{sample_means.std(ddof=1):.4f}")
        c3.metric("理论标准误 σ/√n", f"{theo_se:.4f}")
        c4.metric("总体标准差 σ", f"{theo_sigma:.4f}")

        st.caption("若模拟标准误与理论标准误接近，说明抽样模拟的结果是可靠的。")

        # CSV 导出
        buf = StringIO()
        writer = csv.writer(buf)
        writer.writerow(["sample_index", "sample_mean"])
        for i, v in enumerate(sample_means, 1):
            writer.writerow([i, f"{v:.6f}"])
        st.download_button(
            "导出样本均值数据 CSV",
            data=buf.getvalue().encode("utf-8-sig"),
            file_name=f"sample_means_n{sample_size}_r{repeats}.csv",
            mime="text/csv",
            key="dl_clt_csv",
        )

    with tab2:
        ns = np.arange(1, 201)
        se_curve = theo_sigma / np.sqrt(ns)
        fig, ax = plt.subplots(figsize=(9.8, 4.1))
        ax.plot(ns, se_curve, lw=2.6, color="#6366f1", zorder=3,
                label="标准误 σ/√n")
        ax.fill_between(ns, se_curve, color="#6366f1", alpha=0.10, zorder=2)
        cur_se = theo_sigma / sqrt(sample_size)
        ax.scatter([sample_size], [cur_se], s=110, color="#f97316",
                   zorder=5, edgecolor="white", linewidth=1.6,
                   label=f"当前 n = {sample_size}，SE = {cur_se:.4f}")
        ax.annotate(f"n = {sample_size}\nSE = {cur_se:.4f}",
                    xy=(sample_size, cur_se),
                    xytext=(sample_size + 18, cur_se + theo_sigma * 0.16),
                    fontsize=10, color="#f97316",
                    arrowprops=dict(arrowstyle="->", color="#f97316", lw=1.3))
        polish_axes(ax, "标准误随样本量的衰减（σ/√n）", "样本量 n", "样本均值的标准误")
        ax.legend(loc="upper right")
        render_fig(fig, "clt_se_curve.png", "dl_clt_se",
                   "样本量变为 4 倍，标准误减半——这是「√n 定律」。")

        st.markdown("**思考任务**：如果希望把标准误缩小到原来的 1/3，样本量大约需要扩大多少倍？")
        with st.expander("查看答案"):
            st.write("标准误 ∝ 1/√n。要让 SE 变为 1/3，需要 √n 变为 3 倍，即 n 变为 **9 倍**。")

    four_steps(
        "先把 n 调小（如 5）再调大（如 100），猜一猜直方图形状和宽度会怎么变？",
        "调整 n、总体类型和重复次数，观察直方图与橙色正态曲线的贴合程度。",
        "n 越大，样本均值分布越窄、越接近正态（钟形）；标准误曲线也更平缓。",
        "即使原始总体是偏态分布，n 足够大时样本均值也近似正态；标准误 = σ/√n。",
    )

    with st.expander("如何解读实验结果？"):
        st.markdown(
            """
- 重复抽样得到的是**许多个样本均值**，而不是原始个体观测值。
- 样本量增大时，样本均值的波动通常会减小（标准误变小）。
- 在适当条件下，样本均值分布会趋近正态形态——这就是中心极限定理。
- 有限次模拟存在随机波动，图形不必与理论曲线完全重合；可以增大重复次数或固定随机种子来观察。
- 注意：若总体方差不存在（如柯西分布），中心极限定理不适用。
            """
        )

    with st.expander("对比实验建议"):
        st.markdown(
            """
| 对比项 | 操作方法 | 预期现象 |
| --- | --- | --- |
| 总体形态 | 在指数、对数正态、双峰之间切换 | 总体越偏态，小 n 时抽样分布越偏；n 大后都趋近正态 |
| 样本量 | n 从 5 → 30 → 100 | 直方图逐渐收窄、变对称 |
| 重复次数 | 200 → 5000 | 直方图更平滑，更贴近理论曲线 |
            """
        )

# ======================================================================
# 12. 模块四：大数定律演示
# ======================================================================
elif module == "模块四：大数定律演示":
    st.header("模块四｜大数定律演示")
    st.write("从同一个总体中抽取越来越大的样本，观察**样本均值随样本量增大而趋于总体均值**。")

    c1, c2, c3 = st.columns(3)
    with c1:
        lln_pop = st.selectbox("选择总体类型",
                               ["指数分布 Exp(1)", "均匀分布 U(0,1)", "伯努利分布 B(1, 0.3)", "正态分布 N(2, 1)"])
    with c2:
        n_max = st.slider("最大样本量 n", 50, 5000, 1000, 50)
    with c3:
        seed = st.number_input("随机种子", min_value=0, max_value=99999, value=2026, step=1)

    running, mu_lln = lln_simulation(lln_pop, n_max, seed)
    ns_plot = np.arange(1, n_max + 1)

    fig, ax = plt.subplots(figsize=(9.8, 4.0))
    ax.plot(ns_plot, running, lw=1.4, color="#6366f1", zorder=3, label="样本均值（累积平均）")
    ax.axhline(mu_lln, color="#f97316", ls="--", lw=1.6, zorder=4, label=f"总体均值 μ = {mu_lln:.3f}")
    ax.fill_between(ns_plot, mu_lln - 0.05, mu_lln + 0.05, color="#f97316", alpha=0.08, zorder=1)
    ax.set_xscale("log")
    polish_axes(ax, "大数定律：样本均值随样本量增大趋于总体均值",
                "样本量 n（对数刻度）", "样本均值")
    ax.legend(loc="upper right")
    render_fig(fig, "lln_demo.png", "dl_lln",
               "样本量越大，样本均值围绕总体均值的波动越小。")

    c1, c2, c3 = st.columns(3)
    c1.metric("最终样本均值（n 最大时）", f"{running[-1]:.4f}")
    c2.metric("总体均值 μ", f"{mu_lln:.4f}")
    c3.metric("偏差 |x̄ − μ|", f"{abs(running[-1] - mu_lln):.4f}")

    four_steps(
        "样本量从 100 增大到 5000，样本均值会离总体均值更近还是更远？",
        "拖动最大样本量滑块，观察累积平均曲线的波动幅度。",
        "曲线围绕总体均值 μ 波动，且波动幅度随 n 增大而收窄。",
        "大数定律：样本均值依概率收敛于总体均值；样本量越大，偏差通常越小。",
    )

# ======================================================================
# 13. 模块五：置信区间模拟
# ======================================================================
elif module == "模块五：置信区间模拟":
    st.header("模块五｜置信区间模拟")
    st.write("从 N(0,1) 总体重复抽样并构造置信区间，观察**区间覆盖率是否接近名义置信水平**。")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ci_n = st.slider("每次抽样的样本量 n", 5, 200, 30, 5)
    with c2:
        ci_k = st.slider("模拟区间数量", 50, 5000, 200, 50)
    with c3:
        conf = st.selectbox("置信水平", ["90%", "95%", "99%"])
    with c4:
        seed = st.number_input("随机种子", min_value=0, max_value=99999, value=2026, step=1,
                               key="seed_ci")

    lo, hi, covered = ci_simulation(ci_n, ci_k, conf, seed)
    cover_rate = covered.mean()
    k_plot = min(50, ci_k)

    fig, ax = plt.subplots(figsize=(9.8, 4.6))
    for i in range(k_plot):
        color = "#10b981" if covered[i] else "#ef4444"
        ax.plot([lo[i], hi[i]], [i, i], lw=2.0, color=color, zorder=3)
        ax.scatter([0.5 * (lo[i] + hi[i])], [i], s=12, color=color, zorder=4)
    ax.axvline(0.0, color="#6366f1", ls="--", lw=1.6, zorder=5, label="总体均值 μ = 0")
    ax.set_ylim(-1, k_plot)
    polish_axes(ax, f"{conf} 置信区间模拟（前 {k_plot} 个区间）", "区间范围", "区间编号")
    ax.legend(loc="upper right")
    render_fig(fig, "ci_sim.png", "dl_ci",
               "绿色区间包含总体均值，红色区间未包含（属于正常的抽样波动）。")

    c1, c2, c3 = st.columns(3)
    c1.metric("覆盖区间数", f"{int(covered.sum())}/{ci_k}")
    c2.metric("模拟覆盖率", f"{cover_rate:.2%}")
    c3.metric("名义置信水平", conf)

    four_steps(
        "若总体均值为 0，猜一猜 100 个 95% 置信区间中大约有几个不包含 0？",
        "改变样本量 n、区间数量与置信水平，观察绿色与红色区间的占比。",
        "红色区间（未覆盖）的数量大约占 5% 左右，且会随机波动。",
        "置信水平是长期覆盖频率：重复大量构造区间，约 95% 会包含真实参数；单个区间是否包含参数无法确定。",
    )

    with st.expander("如何解读覆盖率？"):
        st.write("单次实验的覆盖率会偏离名义水平，属正常随机波动；区间数量越多，覆盖率越接近名义置信水平。置信水平描述的是「长期重复构造区间」的覆盖比例，而不是某个具体区间包含参数的概率。")

# ======================================================================
# 14. 模块六：假设检验 z 检验演示
# ======================================================================
elif module == "模块六：假设检验 z 检验演示":
    st.header("模块六｜假设检验 z 检验演示")
    st.write("已知总体标准差 σ 时，用 z 检验判断样本均值是否显著偏离原假设（H₀：μ = μ₀）。")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        mu_true = st.slider("真实总体均值 μ（数据来源）", -3.0, 3.0, 0.5, 0.1)
    with c2:
        sigma_z = st.slider("总体标准差 σ（已知）", 0.5, 5.0, 1.0, 0.1)
    with c3:
        n_z = st.slider("样本量 n", 5, 200, 30, 5)
    with c4:
        mu0 = st.slider("原假设均值 μ₀", -3.0, 3.0, 0.0, 0.1)
    c1, c2 = st.columns(2)
    with c1:
        alpha = st.selectbox("显著性水平 α", ["0.01", "0.05", "0.10"])
        alpha = float(alpha)
    with c2:
        seed = st.number_input("随机种子", min_value=0, max_value=99999, value=2026, step=1,
                               key="seed_ztest")

    sample = draw_normal_sample(mu_true, sigma_z, n_z, seed)
    xbar = float(sample.mean())
    z_stat = (xbar - mu0) / (sigma_z / sqrt(n_z))
    p_value = 2.0 * (1.0 - normal_cdf(abs(z_stat), 0.0, 1.0))
    z_crit = norm_ppf(1.0 - alpha / 2.0)
    reject = p_value < alpha

    fig, ax = plt.subplots(figsize=(9.8, 4.0))
    x = np.linspace(-4.5, 4.5, 800)
    y = normal_pdf(x, 0.0, 1.0)
    ax.plot(x, y, lw=2.0, color="#94a3b8", zorder=3, label="标准正态 N(0,1)")
    left_tail = x <= -z_crit
    right_tail = x >= z_crit
    ax.fill_between(x[left_tail], y[left_tail], color="#ef4444", alpha=0.45, zorder=2,
                    label=f"拒绝域（α/2 = {alpha/2:.3f}）")
    ax.fill_between(x[right_tail], y[right_tail], color="#ef4444", alpha=0.45, zorder=2)
    ax.axvline(z_crit, color="#f97316", ls="--", lw=1.3, zorder=4)
    ax.axvline(-z_crit, color="#f97316", ls="--", lw=1.3, zorder=4,
               label=f"临界值 ±{z_crit:.3f}")
    ax.axvline(z_stat, color="#6366f1", lw=2.2, zorder=5, label=f"观测 z = {z_stat:.3f}")
    polish_axes(ax, "z 检验：检验统计量与拒绝域", "z 值", "密度")
    ax.legend(loc="upper right")
    render_fig(fig, "ztest.png", "dl_ztest",
               f"观测 z 落入{'拒绝域' if reject else '接受域'}，因此{'拒绝' if reject else '不拒绝'} H₀。")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("样本均值 x̄", f"{xbar:.4f}")
    c2.metric("z 统计量", f"{z_stat:.4f}")
    c3.metric("p 值（双侧）", f"{p_value:.4f}")
    c4.metric(f"结论（α = {alpha:.2f}）", "拒绝 H₀" if reject else "不拒绝 H₀")

    if reject:
        st.warning(f"p 值 {p_value:.4f} < α = {alpha:.3f}，统计显著：有充分证据认为总体均值 ≠ {mu0}。")
    else:
        st.info(f"p 值 {p_value:.4f} ≥ α = {alpha:.3f}，统计不显著：没有充分证据拒绝 H₀。")

    four_steps(
        "猜一猜：如果真实均值就是 μ₀，观测 z 统计量更可能落在哪个区域？",
        "调整真实均值 μ 与 μ₀ 的差距、样本量 n 和显著性水平 α，观察 z 值与 p 值的变化。",
        "μ 偏离 μ₀ 越远或 n 越大，|z| 越大、p 值越小，越容易落入拒绝域。",
        "p 值 < α 时拒绝 H₀（差异统计显著）；但统计显著不等于实际重要，也不代表 H₀ 一定为假。",
    )

# ======================================================================
# 15. 模块三：自测与分步学习助手
# ======================================================================
else:
    st.header("模块三｜自测与分步学习助手")
    st.write("先独立作答，再查看解析。本原型采用**本地规则判分**，不会把它冒充为已接入的大语言模型。")

    QUIZ = [
        {
            "id": "q1",
            "q": "正态分布 N(μ, σ²) 中，若 μ 不变、σ 增大，曲线通常会怎样变化？",
            "options": ["更窄、更高", "更宽、更矮", "整体向右平移", "形状完全不变"],
            "answer": 1,
            "ok": "正确。σ 表示离散程度，σ 越大数据越分散，曲线越宽越矮，但曲线下总面积始终为 1。",
            "no": "再想一想：σ 描述的是数据围绕 μ 的离散程度，而不是位置。",
            "hint": "回看模块一 · 正态分布：只拖动 σ 滑块，观察峰值高度与宽度。",
        },
        {
            "id": "q2",
            "q": "中心极限定理主要讨论的是哪一种分布？",
            "options": [
                "单个原始观测值的分布",
                "重复抽样所得样本均值（或适当标准化统计量）的分布",
                "样本中最大值的分布",
                "总体的分布",
            ],
            "answer": 1,
            "ok": "正确。关注的是抽样分布，不要把总体分布与样本均值分布混为一谈。",
            "no": "提示：实验中每次先抽取一组样本，再计算一个样本均值；重复后得到的是许多样本均值。",
            "hint": "回看模块二，观察样本均值直方图随 n 增大的变化。",
        },
        {
            "id": "q3",
            "q": "对二项分布 B(n, p)，若固定 p 并不断增大 n，概率质量形态会怎样变化？",
            "options": [
                "越来越接近正态分布形态",
                "越来越接近均匀分布",
                "始终完全对称、形状不变",
                "变得越来越右偏",
            ],
            "answer": 0,
            "ok": "正确。n 增大且 np 与 n(1−p) 都不太小时，二项分布可用正态分布近似。",
            "no": "提示：把 n 从 10 调到 50 再观察模块一中的二项分布条形图，轮廓是否越来越圆滑？",
            "hint": "回看模块一 · 二项分布，把 n 调大，观察条形图与橙色正态曲线的贴合程度。",
        },
        {
            "id": "q4",
            "q": "样本均值标准误为 σ/√n。当样本量 n 从 4 增大到 16 时，标准误变为原来的多少？",
            "options": ["1/2", "1/4", "1/16", "不变"],
            "answer": 0,
            "ok": "正确。n 变为原来的 4 倍，√n 变为 2 倍，标准误缩小为原来的一半。",
            "no": "提示：σ/√16 与 σ/√4 相比，等于 √4/√16 = 2/4 = 1/2。",
            "hint": "回看模块二 · 标准误曲线：样本量变为 4 倍，标准误减半。",
        },
        {
            "id": "q5",
            "q": "泊松分布 P(λ = 4) 的方差等于多少？",
            "options": ["2", "4", "16", "无法确定"],
            "answer": 1,
            "ok": "正确。泊松分布的均值与方差都等于 λ，因此方差为 4。",
            "no": "提示：泊松分布最显著的特征之一就是均值 = 方差 = λ。",
            "hint": "回看模块一 · 泊松分布，观察指标卡中的「理论均值」与「理论方差」。",
        },
        {
            "id": "q6",
            "q": "从指数分布（强右偏）总体中抽样，当每次抽样的样本量 n 增大时，样本均值的分布会怎样？",
            "options": [
                "仍然保持原来的强右偏形态",
                "越来越接近正态分布，且更加集中",
                "越来越分散",
                "变为均匀分布",
            ],
            "answer": 1,
            "ok": "正确。中心极限定理保证：n 足够大时，即使总体偏态，样本均值也近似正态，且标准误随 n 减小。",
            "no": "提示：在模块二中选择「指数分布总体」，把 n 从 5 调到 100，观察直方图形状与宽度。",
            "hint": "回看模块二，对比 n = 5 与 n = 100 时的直方图形状与宽度。",
        },
    ]

    if "quiz_res" not in st.session_state:
        st.session_state.quiz_res = {}

    total_q = len(QUIZ)
    answered = len(st.session_state.quiz_res)
    n_correct = sum(1 for v in st.session_state.quiz_res.values() if v)

    # ---------- 进度总览 ----------
    st.subheader("自测进度")
    pct = (n_correct / total_q) if total_q else 0.0
    st.progress(pct)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("已作答", f"{answered}/{total_q}")
    m2.metric("答对", f"{n_correct}")
    m3.metric("正确率", f"{(n_correct/answered):.0%}" if answered else "—")
    m4.metric("完成度", f"{answered/total_q:.0%}")

    if answered:
        wrong_ids = [k for k, v in st.session_state.quiz_res.items() if not v]
        if wrong_ids:
            st.warning("以下题目答错了，建议回看对应模块再试一次：")
            hint_map = {item["id"]: item["hint"] for item in QUIZ}
            for wid in wrong_ids:
                qtitle = next((i["q"] for i in QUIZ if i["id"] == wid), wid)
                st.markdown(f"- **{qtitle}**\n  → {hint_map.get(wid, '')}")
        if answered == total_q:
            if n_correct == total_q:
                st.success("全对！你已掌握本次实验的核心概念，试着向同学讲一遍，教学相长。")
            elif n_correct / total_q >= 0.5:
                st.info("总体掌握不错。把答错的题对应模块再实验一遍，理解会更扎实。")
            else:
                st.info("建议按顺序重做模块一、模块二，每步先预测再实验，再回来作答。")

    st.divider()

    # ---------- 逐题作答 ----------
    for item in QUIZ:
        st.markdown(f"**{item['q']}**")
        choice = st.radio(
            "请选择：",
            item["options"],
            index=None,
            key=f"q_radio_{item['id']}",
            label_visibility="collapsed",
        )
        cbtn, cmsg = st.columns([1, 4])
        with cbtn:
            if st.button("提交答案", key=f"q_btn_{item['id']}", use_container_width=True):
                if choice is None:
                    st.toast("请先选择一个选项。")
                else:
                    st.session_state.quiz_res[item["id"]] = (
                        item["options"].index(choice) == item["answer"]
                    )
        with cmsg:
            res = st.session_state.quiz_res.get(item["id"])
            if res is True:
                st.success(item["ok"])
            elif res is False:
                st.warning(item["no"])
        st.markdown("")
        st.divider()

    if st.button("重新作答", key="reset_quiz"):
        st.session_state.quiz_res = {}
        for k in list(st.session_state.keys()):
            if k.startswith("q_radio_") or k.startswith("q_btn_"):
                del st.session_state[k]
        st.rerun()

    # ---------- 分步学习助手 ----------
    st.subheader("分步学习助手")
    st.caption("先看思路提示，再决定是否需要 AI 助教的进一步追问。")

    topic = st.selectbox(
        "选择你卡住的概念",
        ["正态分布参数", "二项分布", "泊松分布", "抽样分布", "中心极限定理", "标准误", "置信区间", "假设检验"],
    )
    question = st.text_area(
        "写下你的问题（可选）",
        placeholder="例如：为什么样本量变大后，样本均值更稳定？",
    )

    guidance = {
        "正态分布参数": "① 辨认 μ 与 σ 各自控制什么；② 每次只改变一个参数；③ 比较曲线的中心、宽度、峰值三个特征。",
        "二项分布": "① 确认是否满足 n 次独立、只有成功/失败、成功概率恒为 p；② 套用 P(X=k)=C(n,k)p^k(1−p)^(n−k)；③ 用 np 与 np(1−p) 预测峰值位置与离散程度。",
        "泊松分布": "① 确认事件在单位时间/空间内独立、以固定平均速率 λ 发生；② 使用 P(X=k)=λ^k e^(−λ)/k!；③ 记住均值与方差都等于 λ。",
        "抽样分布": "① 区分总体中的个体值、一个样本的统计量、重复抽样后统计量形成的分布；② 每次抽样只产生一个样本均值；③ 直方图的横轴是「样本均值」，不是原始观测值。",
        "中心极限定理": "① 先说明适用条件（独立同分布、方差有限）；② 再看样本量与样本均值标准误的关系；③ 不要理解成「任何样本、任何条件下都必然正态」。",
        "标准误": "① 标准误衡量的是统计量的波动，不是个体数据的波动；② SE = σ/√n；③ n 变为原来的 k 倍，SE 变为原来的 1/√k。",
        "置信区间": "① 置信水平是长期覆盖频率，不是单个区间包含参数的概率；② 区间宽度随 n 增大而变窄、随置信水平提高而变宽。",
        "假设检验": "① 先写 H₀ 与 H₁；② p 值是在 H₀ 为真时观测到当前或更极端结果的概率；③ p < α 拒绝 H₀，「不拒绝」不等于「接受」。",
    }
    st.info(guidance[topic])

    if question.strip():
        st.markdown("**可复制给 AI 助教的追问提示词**")
        prompt = (
            f"你是一名耐心的大学统计学助教。请用循序渐进的方式讲解「{topic}」。\n"
            f"学生的问题是：{question}\n\n"
            "请遵守以下要求：\n"
            "1. 先问一个诊断性问题，判断学生的前置概念是否清楚；\n"
            "2. 给出提示而非直接给结论，一次只推进一小步；\n"
            "3. 若涉及公式，请逐个解释符号的含义与适用条件；\n"
            "4. 最后用一道类似的小题检查学生是否真的理解，并给出参考答案。"
        )
        st.code(prompt, language="text")
        st.caption("使用方法：复制上面的提示词，粘贴到你实际使用的 AI 助手中。当前网页不会自动向外部模型发送问题。")
    else:
        st.caption("在上方输入你的问题后，这里会生成一段可复制的提示词。")

# ======================================================================
# 13. 页脚
# ======================================================================
st.divider()
st.markdown(
    '<p class="footer-text">'
    "教学原型说明：本网页用于教学设计与演示。提交前请在实际运行环境中测试，"
    "并根据真实测试结果修订案例说明。所有模拟数据均在本地生成，不会上传任何内容。"
    "</p>",
    unsafe_allow_html=True,
)
#（注：内容由AI生成）
