import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="脂肪酸合成(FAS)动态模拟系统",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #00ffcc, #00ccff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e1e2e, #2d2d44);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #00ffcc;
    }
    .reaction-step {
        background: rgba(0, 255, 204, 0.1);
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        border: 1px solid rgba(0, 255, 204, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# 应用标题
st.markdown('<h1 class="main-header">🧬 脂肪酸合成(FAS)动态模拟系统</h1>', unsafe_allow_html=True)

# 侧边栏 - 控制面板
with st.sidebar:
    st.header("⚙️ 控制面板")

    # 模拟参数设置
    st.subheader("模拟参数")
    target_cycle = st.slider(
        "循环次数",
        min_value=0,
        max_value=7,
        value=4,
        help="脂肪酸合成循环次数（0=C₂, 7=C₁₆）"
    )

    # 能量参数调整
    st.subheader("能量参数")
    initial_energy = st.slider("初始能量状态(%)", 0, 100, 20, help="乙酰-CoA阶段的能量水平")
    energy_variation = st.slider("能量波动范围", 0, 30, 5, help="每次循环的能量变化波动")

    # 环境条件
    st.subheader("环境条件")
    atp_availability = st.slider("ATP可用性(%)", 0, 100, 85)
    nadph_availability = st.slider("NADPH可用性(%)", 0, 100, 90)
    temperature = st.slider("温度(°C)", 25, 40, 37)

    # 显示模拟信息
    st.divider()
    st.info(f"""
    **模拟状态**: {"运行中" if target_cycle > 0 else "待开始"}
    **当前时间**: {datetime.now().strftime("%H:%M:%S")}
    **总反应数**: {target_cycle * 4}
    """)


# 主要数据
def generate_fas_data(cycles, initial_energy, energy_variation):
    """生成FAS模拟数据"""
    cycles_data = []
    carbon_lengths = ["C₂", "C₄", "C₆", "C₈", "C₁₀", "C₁₂", "C₁₄", "C₁₆"]
    energy_base = initial_energy

    for i in range(cycles + 1):
        # 模拟能量变化（基准 + 随机波动）
        if i > 0:
            variation = np.random.uniform(-energy_variation, energy_variation)
            energy_base = max(10, min(100, energy_base + variation))

        cycles_data.append({
            "循环次数": i,
            "碳链长度": carbon_lengths[i],
            "碳原子数": 2 * (i + 1),
            "能量状态(%)": round(energy_base, 2),
            "ATP消耗": i,
            "NADPH消耗": i * 2,
            "反应时间(模拟)": i * 2.5,  # 模拟反应时间
            "酶活性(%)": max(60, 100 - i * 5)  # 模拟酶活性下降
        })

    return pd.DataFrame(cycles_data)


# 生成数据
df = generate_fas_data(target_cycle, initial_energy, energy_variation)

# 主界面布局
col1, col2 = st.columns([2, 1])

with col1:
    # 选项卡布局
    tab1, tab2, tab3 = st.tabs(["📈 能量动态", "⚡ 代谢流", "🧪 分子结构"])

    with tab1:
        # 多指标图表
        fig = go.Figure()

        # 能量曲线
        fig.add_trace(go.Scatter(
            x=df["碳链长度"],
            y=df["能量状态(%)"],
            mode="lines+markers",
            name="能量状态",
            line=dict(color="#00ffcc", width=4),
            marker=dict(size=12, color="#00ffcc"),
            hovertemplate="<b>碳链: %{x}</b><br>能量: %{y}%<br>循环: %{customdata}<extra></extra>",
            customdata=df["循环次数"]
        ))

        # 酶活性曲线
        fig.add_trace(go.Scatter(
            x=df["碳链长度"],
            y=df["酶活性(%)"],
            mode="lines",
            name="FAS酶活性",
            line=dict(color="#ff9966", width=3, dash="dash"),
            yaxis="y2"
        ))

        fig.update_layout(
            title="脂肪酸合成能量动态与酶活性",
            plot_bgcolor="#1e1e2e",
            paper_bgcolor="#1e1e2e",
            xaxis=dict(
                title="碳链长度",
                color="white",
                gridcolor="#444466"
            ),
            yaxis=dict(
                title="能量状态(%)",
                color="white",
                gridcolor="#444466",
                range=[0, 100]
            ),
            yaxis2=dict(
                title="酶活性(%)",
                color="#ff9966",
                overlaying="y",
                side="right",
                range=[0, 100]
            ),
            hovermode="x unified",
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor="rgba(30, 30, 46, 0.8)",
                bordercolor="rgba(0, 255, 204, 0.3)"
            ),
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # 代谢消耗堆叠图
        fig2 = go.Figure()

        fig2.add_trace(go.Bar(
            x=df["碳链长度"],
            y=df["ATP消耗"],
            name="ATP消耗",
            marker_color="#ff5555",
            hovertemplate="ATP: %{y}分子"
        ))

        fig2.add_trace(go.Bar(
            x=df["碳链长度"],
            y=df["NADPH消耗"],
            name="NADPH消耗",
            marker_color="#55aaff",
            hovertemplate="NADPH: %{y}分子"
        ))

        fig2.update_layout(
            title="代谢物累积消耗",
            plot_bgcolor="#1e1e2e",
            paper_bgcolor="#1e1e2e",
            barmode="stack",
            xaxis=dict(color="white", gridcolor="#444466"),
            yaxis=dict(title="分子数", color="white", gridcolor="#444466"),
            height=400
        )

        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        # 分子结构信息
        st.subheader("当前脂肪酸链结构")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.metric("碳原子数", f"{df.iloc[-1]['碳原子数']}")
        with col_b:
            st.metric("双键数", "0")
        with col_c:
            st.metric("分子量(Da)", f"{df.iloc[-1]['碳原子数'] * 12 + 32:.1f}")

        # 简单的分子结构表示
        st.code(f"""
        H₃C-(CH₂)ₙ-COOH
        n = {(df.iloc[-1]['碳原子数'] - 2) // 2}

        结构式: CH₃(CH₂){df.iloc[-1]['碳原子数'] - 2}COOH
        类别: 饱和脂肪酸
        名称: 已完成 {target_cycle}/7 次延长循环
        """)

with col2:
    # 关键指标展示
    st.subheader("📊 关键指标")

    metrics_col1, metrics_col2 = st.columns(2)

    with metrics_col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="总能量消耗",
            value=f"{df['ATP消耗'].iloc[-1] + df['NADPH消耗'].iloc[-1]} ATP当量",
            delta=f"{df['能量状态(%)'].iloc[-1] - df['能量状态(%)'].iloc[0]:+.1f}%"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="合成效率",
            value=f"{(target_cycle / 7 * 100):.1f}%",
            delta=f"{target_cycle}/7 循环"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with metrics_col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="ATP可用性",
            value=f"{atp_availability}%",
            delta="正常" if atp_availability > 70 else "不足",
            delta_color="normal" if atp_availability > 70 else "inverse"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="NADPH可用性",
            value=f"{nadph_availability}%",
            delta="充足" if nadph_availability > 75 else "偏低",
            delta_color="normal" if nadph_availability > 75 else "inverse"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # 反应步骤详情
    st.subheader("🔄 当前循环反应")

    if target_cycle > 0:
        reaction_steps = [
            "1. 缩合反应: 乙酰-ACP + 丙二酰-ACP → β-酮脂酰-ACP",
            "2. 第一次还原: β-酮脂酰-ACP → β-羟脂酰-ACP (NADPH+H⁺)",
            "3. 脱水反应: β-羟脂酰-ACP → 烯脂酰-ACP",
            "4. 第二次还原: 烯脂酰-ACP → 脂酰-ACP (NADPH+H⁺)"
        ]

        for step in reaction_steps:
            st.markdown(f'<div class="reaction-step">{step}</div>', unsafe_allow_html=True)

    # 数据表
    st.subheader("📋 详细数据")
    st.dataframe(
        df[["循环次数", "碳链长度", "能量状态(%)", "ATP消耗", "NADPH消耗", "酶活性(%)"]],
        use_container_width=True,
        hide_index=True
    )

# 底部信息栏
st.divider()
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.caption("🧬 FAS复合体: 多功能酶复合体")
with footer_col2:
    st.caption(f"🌡️ 温度: {temperature}°C | pH: 7.0-7.4")
with footer_col3:
    st.caption("🔄 总反应: CH₃COSCoA + 7HOOCCH₂COSCoA + 14NADPH + 14H⁺ → C₁₅H₃₁COOH + 7CO₂ + 14NADP⁺ + 8HSCoA + 6H₂O")

# 添加进度条
st.progress(target_cycle / 7, text=f"合成进度: {target_cycle}/7 循环")