import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from math import comb, factorial, sqrt, pi, exp
import os
import base64

# ============ 页面配置 ============
st.set_page_config(page_title="数智统计实验室", page_icon="📊", layout="wide")

# matplotlib 中文字体（避免图表中文乱码）
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

# ============ 全局样式 ============
st.markdown(
    """
    <style>
    .block-container {padding-top: 1.6rem;}
    h1 {
        background: linear-gradient(90deg, #6366f1 0%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 1px;
    }
    section[data-testid="stSidebar"] {border-right: 1px solid rgba(128,128,128,0.15);}
    .stButton button {border-radius: 8px; transition: all .2s ease;}
    .stButton button:hover {transform: translateY(-1px);}
    [data-testid="stMetric"] {
        background: rgba(128,128,128,0.10);
        border: 1px solid rgba(128,128,128,0.18);
        border-radius: 12px;
        padding: 14px 16px;
    }
    details {border-radius: 10px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# 校徽图片：与 app.py 同目录，转 base64 内嵌，直接显示在标题文字前（原 📊 图标位置）
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nenu_logo.jpg")
with open(LOGO_PATH, "rb") as f:
    LOGO_B64 = base64.b64encode(f.read()).decode()

st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:14px;">
        <img src="data:image/jpeg;base64,{LOGO_B64}" style="width:60px; height:60px; flex-shrink:0; border-radius:8px;" alt="东北师范大学校徽"/>
        <h1 style="margin:0;">数智统计实验室</h1>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("AI赋能统计学交互式教学资源原型｜概率分布 · 随机抽样 · 中心极限定理")

with st.sidebar:
    st.header("学习导航")
    module = st.radio("选择学习模块", [
        "模块一：概率分布实验室",
        "模块二：抽样与中心极限定理",
        "模块三：自测与分步学习助手"
    ])
    st.divider()
    st.info("教学路径：先预测 → 再实验 → 观察结果 → 解释原因。")

def normal_pdf(x, mu, sigma):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))

# ============ 模块一：概率分布实验室 ============
if module == "模块一：概率分布实验室":
    st.header("模块一｜概率分布实验室")
    st.write("通过调整参数，观察分布形态如何变化。建议先预测曲线变化，再移动参数验证。")
    dist = st.selectbox("选择分布", ["正态分布", "二项分布", "泊松分布"])

    # ---------- 正态分布 ----------
    if dist == "正态分布":
        c1, c2 = st.columns(2)
        with c1:
            mu = st.slider("均值 μ", -5.0, 5.0, 0.0, 0.5)
        with c2:
            sigma = st.slider("标准差 σ", 0.2, 3.0, 1.0, 0.1)
        x = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 500)
        y = normal_pdf(x, mu, sigma)
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(x, y, linewidth=2, color="#6366f1")
        ax.fill_between(x, y, alpha=0.12, color="#6366f1")
        ax.axvline(mu, color="#f97316", linestyle="--", linewidth=1.2, label=f"μ = {mu:.1f}")
        ax.set_title(f"正态分布 N({mu:.1f}, {sigma:.1f}²)")
        ax.set_xlabel("x")
        ax.set_ylabel("概率密度")
        ax.grid(alpha=0.25)
        ax.legend()
        st.pyplot(fig)

        c1, c2, c3 = st.columns(3)
        c1.metric("均值 μ", f"{mu:.1f}")
        c2.metric("标准差 σ", f"{sigma:.2f}")
        c3.metric("方差 σ²", f"{sigma**2:.2f}")

        with st.expander("📌 教学四步法：预测 → 实验 → 观察 → 解释"):
            st.write("**第1步 预测**：先别动滑块——如果 σ 不变、μ 增大，曲线整体会往哪边移动？")
            st.write("**第2步 实验**：拖动滑块，观察曲线实际变化。")
            st.write("**第3步 观察**：注意曲线中心（μ）、宽度与峰值高度（σ）的变化。")
            st.write("**第4步 解释**：μ 决定分布中心；σ 越大数据越分散、曲线越矮胖；曲线下总面积为 1。")

        st.markdown("**观察任务**")
        st.write("1. 保持标准差不变，改变均值：曲线位置发生什么变化？")
        st.write("2. 保持均值不变，增大标准差：曲线的高度和宽度如何变化？")
        with st.expander("查看分步提示"):
            st.write("提示1：均值描述分布的中心位置。")
            st.write("提示2：标准差描述数据围绕均值的离散程度。")
            st.write("提示3：正态曲线关于均值对称，曲线下的总面积为1。")

    # ---------- 二项分布 ----------
    elif dist == "二项分布":
        n = st.slider("试验次数 n", 1, 40, 10)
        p = st.slider("单次成功概率 p", 0.05, 0.95, 0.5, 0.05)
        xs = np.arange(n + 1)
        probs = np.array([comb(n, int(k)) * (p**k) * ((1 - p) ** (n - k)) for k in xs])
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.bar(xs, probs, width=0.8, color="#38bdf8", edgecolor="white")
        # 正态近似叠加：n 较大且 np、n(1-p) 均不太小时，二项概率质量≈正态密度
        mu_b = n * p
        sd_b = np.sqrt(n * p * (1 - p))
        x_norm = np.linspace(max(0, mu_b - 4 * sd_b), mu_b + 4 * sd_b, 200)
        ax.plot(x_norm, normal_pdf(x_norm, mu_b, sd_b), linewidth=2, color="#f97316",
                label=f"正态近似 N({mu_b:.1f}, {sd_b:.1f}²)")
        ax.set_title(f"二项分布 B({n}, {p:.2f})")
        ax.set_xlabel("成功次数 k")
        ax.set_ylabel("P(X = k)")
        ax.grid(axis="y", alpha=0.25)
        ax.legend()
        st.pyplot(fig)

        c1, c2 = st.columns(2)
        c1.metric("理论均值 np", f"{n * p:.2f}")
        c2.metric("理论方差 np(1-p)", f"{n * p * (1 - p):.2f}")

        with st.expander("📌 教学四步法：预测 → 实验 → 观察 → 解释"):
            st.write("**第1步 预测**：固定 n，把 p 从 0.1 拉到 0.9，概率质量会向哪边移动？")
            st.write("**第2步 实验**：拖动 p 的滑块，观察条形图变化。")
            st.write("**第3步 观察**：峰值出现在 n·p 附近；p 越接近 0.5，图形越对称。")
            st.write("**第4步 解释**：p > 0.5 时成功更常见，分布右偏（质量向大 k 移动）；p < 0.5 时左偏。")

        st.markdown("**思考任务**：固定 n，逐渐增大 p，概率质量主要向哪个方向移动？")

    # ---------- 泊松分布 ----------
    else:
        lam = st.slider("平均发生率 λ", 0.5, 15.0, 3.0, 0.5)
        kmax = int(lam + 5 * sqrt(lam)) + 5
        xs = np.arange(kmax + 1)
        probs = np.array([exp(-lam) * lam**k / factorial(k) for k in xs])
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.bar(xs, probs, width=0.8, color="#f97316", edgecolor="white")
        # 正态近似叠加：λ 较大时泊松分布趋近正态 N(λ, λ)
        x_norm = np.linspace(max(0, lam - 4 * sqrt(lam)), lam + 4 * sqrt(lam), 200)
        ax.plot(x_norm, normal_pdf(x_norm, lam, sqrt(lam)), linewidth=2, color="#6366f1",
                label=f"正态近似 N(λ={lam:.1f}, σ=√λ)")
        ax.set_title(f"泊松分布 P(λ={lam:.1f})")
        ax.set_xlabel("事件发生次数 k")
        ax.set_ylabel("P(X = k)")
        ax.grid(axis="y", alpha=0.25)
        ax.legend()
        st.pyplot(fig)

        c1, c2 = st.columns(2)
        c1.metric("理论均值 λ", f"{lam:.2f}")
        c2.metric("理论方差 λ", f"{lam:.2f}")

        with st.expander("📌 教学四步法：预测 → 实验 → 观察 → 解释"):
            st.write("**第1步 预测**：λ 从 1 增大到 10，条形图会变高还是变宽？")
            st.write("**第2步 实验**：拖动 λ 滑块，观察概率质量如何扩散。")
            st.write("**第3步 观察**：分布中心约等于 λ，λ 越大图形越向右移、越接近对称。")
            st.write("**第4步 解释**：泊松分布描述单位时间/空间内稀有事件发生次数，其均值与方差都等于 λ。")

        st.markdown("**思考任务**：λ 增大时，分布整体形态（位置与形状）如何变化？")

# ============ 模块二：抽样与中心极限定理 ============
elif module == "模块二：抽样与中心极限定理":
    st.header("模块二｜抽样与中心极限定理")
    st.write("从偏态总体中重复抽样，观察样本均值的分布。")
    c1, c2, c3 = st.columns(3)
    with c1:
        sample_size = st.slider("每次抽样样本量 n", 2, 200, 30, 1)
    with c2:
        repeats = st.slider("重复抽样次数", 100, 5000, 1000, 100)
    with c3:
        seed = st.number_input("随机种子（便于复现）", min_value=0, max_value=99999, value=2026, step=1)
    rng = np.random.default_rng(int(seed))
    # 向量化抽样：一次性生成 repeats×sample_size 矩阵，按行求均值（比逐次循环快几十倍）
    sample_means = rng.exponential(scale=1.0, size=(repeats, sample_size)).mean(axis=1)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.hist(sample_means, bins=35, density=True, alpha=0.75, edgecolor="white", color="#38bdf8")
    xx = np.linspace(max(0, sample_means.min()), sample_means.max(), 300)
    theo_mu = 1.0
    theo_sd = 1.0 / np.sqrt(sample_size)
    ax.plot(xx, normal_pdf(xx, theo_mu, theo_sd), linewidth=2, color="#f97316",
            label=f"正态近似 N(1, 1/{sample_size})")
    ax.set_title("重复抽样得到的样本均值分布（指数总体）")
    ax.set_xlabel("样本均值")
    ax.set_ylabel("密度")
    ax.legend()
    ax.grid(alpha=0.2)
    st.pyplot(fig)

    c1, c2 = st.columns(2)
    c1.metric("模拟样本均值", f"{sample_means.mean():.4f}")
    c2.metric("模拟样本均值标准差", f"{sample_means.std(ddof=1):.4f}")

    st.write(f"理论总体均值为 1，样本均值标准误为 1/√n ≈ **{theo_sd:.4f}**。")

    with st.expander("📌 教学四步法：预测 → 实验 → 观察 → 解释"):
        st.write("**第1步 预测**：先把 n 调小（如 5）再调大（如 100），猜一猜直方图形状和宽度会怎么变？")
        st.write("**第2步 实验**：调整 n 和重复次数，观察直方图与橙色正态曲线的贴合程度。")
        st.write("**第3步 观察**：n 越大，样本均值分布越窄、越接近正态（钟形）。")
        st.write("**第4步 解释**：单个观测服从偏态的指数分布，但样本均值近似正态——这正是中心极限定理：n 足够大时，样本均值分布近似正态，标准误 = σ/√n。")

    with st.expander("如何解读实验结果？"):
        st.write("重复抽样得到的是许多个样本均值，而不是原始个体观测值。样本量增大时，样本均值的波动通常会减小；在适当条件下，样本均值分布会趋近正态形态。有限次模拟会有随机波动，因此图形不必与理论曲线完全重合。")

# ============ 模块三：自测与分步学习助手 ============
else:
    st.header("模块三｜自测与分步学习助手")
    st.write("先独立作答，再查看解析。此原型采用本地规则提示，不会把它冒充为已接入的大语言模型。")

    # ---------- 答题状态（跨页面重跑保留） ----------
    for _qk in ["q1", "q2", "q3", "q4"]:
        if _qk not in st.session_state:
            st.session_state[_qk] = None  # None=未作答；"correct"/"wrong"=作答结果

    # ---------- 题目 1 ----------
    q = st.radio("问题1：正态分布 N(μ, σ²) 中，σ 增大且 μ 不变，通常会怎样？", [
        "曲线更窄、更高",
        "曲线更宽、更低",
        "曲线中心向右移动"
    ])
    if st.button("提交问题1答案"):
        st.session_state.q1 = "correct" if q == "曲线更宽、更低" else "wrong"
        if q == "曲线更宽、更低":
            st.success("回答正确。标准差增大意味着离散程度增加，曲线变宽，峰值降低。")
        else:
            st.warning("再想一想：σ 描述离散程度，而 μ 决定中心位置。")
    st.divider()

    # ---------- 题目 2 ----------
    q2 = st.radio("问题2：中心极限定理主要讨论哪一种分布？", [
        "单个原始观测值的分布",
        "重复抽样得到的样本均值（或适当标准化统计量）的分布",
        "样本中最大值的分布"
    ])
    if st.button("提交问题2答案"):
        st.session_state.q2 = "correct" if q2.startswith("重复抽样") else "wrong"
        if q2.startswith("重复抽样"):
            st.success("回答正确。关注的是抽样分布，不要把总体分布与样本均值分布混为一谈。")
        else:
            st.warning("提示：实验中每次先抽取一组样本，再计算一个样本均值；重复后得到的是许多样本均值。")
    st.divider()

    # ---------- 题目 3 ----------
    q3 = st.radio("问题3：对二项分布 B(n, p)，若固定 p 并不断增大 n，概率质量形态会怎样？", [
        "越来越接近正态分布形态",
        "越来越接近均匀分布",
        "形状保持不变"
    ])
    if st.button("提交问题3答案"):
        st.session_state.q3 = "correct" if q3.startswith("越来越接近正态") else "wrong"
        if q3.startswith("越来越接近正态"):
            st.success("回答正确。n 增大且 np 不太小时，二项分布可用正态分布近似（二项分布的正态近似）。")
        else:
            st.warning("提示：把 n 从 10 调到 40 再观察模块一中的二项分布条形图，峰值两侧是否越来越对称、圆滑？")
    st.divider()

    # ---------- 题目 4 ----------
    q4 = st.radio("问题4：样本均值标准误为 σ/√n。当样本量 n 从 4 增大到 16 时，标准误变为原来的多少？", [
        "1/2",
        "1/4",
        "不变"
    ])
    if st.button("提交问题4答案"):
        st.session_state.q4 = "correct" if q4 == "1/2" else "wrong"
        if q4 == "1/2":
            st.success("回答正确。n 变为原来的 4 倍，√n 变为原来的 2 倍，标准误缩小为原来的一半。")
        else:
            st.warning("提示：σ/√16 与 σ/√4 相比，等于 √4/√16 = 2/4 = 1/2。")
    st.divider()

    # ---------- 得分汇总与错题回顾 ----------
    answered = [k for k in ["q1", "q2", "q3", "q4"] if st.session_state[k] is not None]
    if answered:
        n_correct = sum(1 for k in answered if st.session_state[k] == "correct")
        pct = n_correct / len(answered)
        st.subheader("📈 自测进度")
        st.progress(pct)
        st.write(f"已作答 **{len(answered)}/4** 题，答对 **{n_correct}** 题，当前正确率 **{pct:.0%}**")
        wrong = [k for k in answered if st.session_state[k] == "wrong"]
        if wrong:
            st.warning("以下题目答错了，建议回看对应模块再试一次：")
            wrong_hint = {
                "q1": "问题1（σ 决定离散程度、μ 决定中心）→ 回看模块一·正态分布，拖动 σ 滑块观察曲线宽度变化。",
                "q2": "问题2（中心极限定理关注的是抽样分布）→ 回看模块二，观察样本均值直方图随 n 增大的变化。",
                "q3": "问题3（二项分布的正态近似）→ 回看模块一·二项分布，把 n 调大观察条形图是否更对称、更贴近橙线。",
                "q4": "问题4（标准误 = σ/√n）→ 回看模块二，n 变为 4 倍时 √n 变为 2 倍，标准误减半。"
            }
            for k in wrong:
                st.write("• " + wrong_hint[k])
        if len(answered) == 4:
            if pct == 1.0:
                st.success("🎉 全对！你已掌握本次实验的核心概念，试着向同学讲一遍，教学相长。")
            elif pct >= 0.5:
                st.info("总体掌握不错。把答错的题对应模块再实验一遍，理解会更扎实。")
            else:
                st.info("建议按顺序重做模块一、模块二，每步先预测再实验，再回来作答。")
        if st.button("🔁 重新作答"):
            for _qk in ["q1", "q2", "q3", "q4"]:
                st.session_state[_qk] = None
            st.rerun()

    # ---------- 分步学习助手 ----------
    st.subheader("分步学习助手")
    topic = st.selectbox("选择你卡住的概念", ["正态分布参数", "二项分布", "泊松分布", "抽样分布", "中心极限定理"])
    question = st.text_area("写下你的问题（可选）", placeholder="例如：为什么样本量变大后，样本均值更稳定？")
    guidance = {
        "正态分布参数": "第1步先辨认 μ 和 σ 分别控制什么；第2步只改变一个参数；第3步比较曲线中心、宽度和峰值。",
        "二项分布": "先确认固定试验次数 n、每次只有成功/失败两种结果、各次成功概率 p 相同且独立；再使用 P(X=k)=C(n,k)p^k(1-p)^(n-k)。",
        "泊松分布": "先确认事件在单位时间/空间内独立、以固定平均速率 λ 发生；再使用 P(X=k)=λ^k e^(-λ)/k!，并记住均值与方差都等于 λ。",
        "抽样分布": "区分总体中的个体值、一个样本的统计量，以及重复抽样后统计量形成的分布。每次抽样只产生一个样本均值。",
        "中心极限定理": "先说明适用条件，再看样本量与样本均值标准误的关系；不要把定理理解成任何样本、任何条件下都必然正态。"
    }
    st.info(guidance[topic])
    if question.strip():
        st.markdown("**可复制给AI助教的追问提示词**")
        prompt = f"你是一名耐心的大学统计学助教。请用循序渐进的方式讲解“{topic}”。学生的问题是：{question}。请先问一个诊断性问题，再给提示，不要直接跳到结论；最后用一道类似的小题检查理解。若涉及公式，请解释每个符号。"
        st.code(prompt, language="text")
        st.caption("使用方法：复制上面的提示词，粘贴到你实际使用的AI助手中。当前网页不会自动向外部模型发送问题。")

st.divider()
st.caption("教学原型说明：本网页用于教学设计与演示。提交前请在实际运行环境中测试，并根据真实测试结果修订案例说明。")
