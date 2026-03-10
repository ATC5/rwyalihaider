import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.integrate import odeint

# --- 1. إعدادات الصفحة الاحترافية ---
st.set_page_config(page_title="Dynamic Runway Simulator", page_icon="✈️", layout="wide", initial_sidebar_state="expanded")

# --- 2. ستايل CSS متقدم (Glassmorphism & Dark Aerospace Theme) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');
    html, body, [class*="css"] {font-family: 'Tajawal', sans-serif !important; direction: rtl;}
    
    /* تصميم الكروت الهندسية الفوق */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #1e1e2f, #2a2a40);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5), -5px -5px 15px rgba(255,255,255,0.05);
        border-left: 5px solid #00f5d4;
    }
    div[data-testid="metric-container"] label {color: #a8b2d1 !important; font-size: 16px;}
    div[data-testid="metric-container"] div {color: #00f5d4 !important; font-weight: bold;}
    
    /* فواصل العناوين */
    h1, h2, h3 {color: #e6f1ff;}
    hr {border-color: #333;}
</style>
""", unsafe_allow_html=True)

# --- 3. تصميم الهيدر (العنوان) ---
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.markdown("<h1 style='text-align: center; font-size: 60px;'>🛫</h1>", unsafe_allow_html=True)
with col_title:
    st.title("نظام المحاكاة المتقدم لاهتزازات مدارج المطارات")
    st.markdown("**Advanced Dynamic Pavement Response Simulator (ADPRS) - V3.0**")
st.markdown("---")

# --- 4. الدالة الفيزيائية ---
def runway_model(y, t, m, c, k):
    return [y[1], -(c/m)*y[1] - (k/m)*y[0]]

# --- 5. لوحة التحكم الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3125/3125713.png", width=100)
    st.header("🎛️ وحدة التحكم المركزية")
    st.markdown("يرجى إدخال معاملات النظام الميكانيكي:")
    
    aircraft_type = st.selectbox("✈️ نوع الطائرة (الكتلة - m)", [
        "Boeing 737 (66,000 kg)",
        "Airbus A320 (67,400 kg)",
        "Boeing 777 (200,000 kg)",
        "Antonov An-225 (285,000 kg)" # ضفتلك طيارة عملاقة حتى تبين الفرق
    ])
    m_val = float(aircraft_type.split('(')[1].split()[0].replace(',', ''))
    
    runway_type = st.selectbox("🛣️ خواص المدرج (معامل التخميد - c)", [
        "مدرج قديم ومتهالك - 500000 N.s/m",
        "مدرج قياسي (أسفلت) - 1500000 N.s/m",
        "مدرج حديث (خرسانة مسلحة) - 4000000 N.s/m",
        "تخميد حرج (نظري) - 6000000 N.s/m"
    ])
    c_val = float(runway_type.split('-')[1].split()[0].strip())
    
    k_val = st.number_input("🏗️ صلابة المدرج (Stiffness - k) [N/m]", value=50000000.0, step=1000000.0, format="%f")
    
    v0 = st.slider("🛬 سرعة الارتطام العمودية (Sink Rate)", min_value=-6.0, max_value=-0.5, value=-3.0, step=0.5, help="السرعة التي تلامس بها عجلات الطائرة أرضية المدرج")
    
    st.markdown("---")
    st.success("🟢 النظام متصل. يتم المعالجة بالزمن الفعلي.")

# --- 6. العمليات الحسابية المتقدمة ---
t = np.linspace(0, 5, 2000) # دقة أعلى (2000 نقطة)
sol = odeint(runway_model, [0.0, v0], t, args=(m_val, c_val, k_val))
displacement = sol[:, 0] * 1000 # تحويل إلى مليمتر
velocity = sol[:, 1]

# حسابات هندسية دقيقة
max_disp_mm = abs(np.min(displacement))
impact_force_kN = (k_val * (max_disp_mm / 1000)) / 1000
natural_freq = np.sqrt(k_val / m_val)
damping_ratio = c_val / (2 * np.sqrt(k_val * m_val))

# حساب وقت الاستقرار (Settling Time)
threshold = 0.05 * max_disp_mm
settled_indices = np.where(np.abs(displacement) > threshold)[0]
settling_time = t[settled_indices[-1]] if len(settled_indices) > 0 else 0.0

# تحديد حالة التخميد
if damping_ratio < 1:
    damping_status = "Underdamped (مخمد جزئياً)"
elif damping_ratio == 1:
    damping_status = "Critically Damped (تخميد حرج)"
else:
    damping_status = "Overdamped (فوق المخمد)"

# --- 7. عرض الـ Dashboards (المؤشرات العلوية) ---
st.subheader("📊 لوحة المؤشرات الهندسية (KPIs)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("أقصى هبوط للتبليط (Max Deflection)", f"{max_disp_mm:.2f} mm")
m2.metric("قوة الارتطام (Impact Force)", f"{impact_force_kN:.1f} kN")
m3.metric("نسبة التخميد (Damping Ratio - ζ)", f"{damping_ratio:.3f}", damping_status, delta_color="off")
m4.metric("وقت الاستقرار (Settling Time)", f"{settling_time:.2f} sec")

st.markdown("<br>", unsafe_allow_html=True)

# --- 8. الرسوم البيانية (الجرافيكس) ---
col_graph, col_gauge = st.columns([2.5, 1])

with col_graph:
    st.markdown("### 📈 موجة الاهتزاز الزمنية (Transient Response)")
    fig_wave = go.Figure()
    fig_wave.add_trace(go.Scatter(
        x=t, y=displacement,
        mode='lines',
        name='Deflection',
        line=dict(color='#00f5d4', width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 245, 212, 0.1)'
    ))
    # إضافة خط الصفر
    fig_wave.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="حالة الاستقرار (Equilibrium)")
    fig_wave.update_layout(
        xaxis_title="الزمن (sec)",
        yaxis_title="الإزاحة (mm)",
        hovermode="x unified",
        template="plotly_dark",
        height=450,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_wave, use_container_width=True)

with col_gauge:
    st.markdown("### ⚠️ مؤشر الخطر الإنشائي")
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = max_disp_mm,
        title = {'text': "مستوى الإجهاد (mm)", 'font': {'size': 20, 'color': 'white'}},
        gauge = {
            'axis': {'range': [0, 150], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#1e1e2f", 'thickness': 0.2},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': "#00b4d8", 'name': 'آمن'},
                {'range': [40, 90], 'color': "#ffb703", 'name': 'تحذير'},
                {'range': [90, 150], 'color': "#ef233c", 'name': 'خطر حرجة'}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': max_disp_mm}
        }
    ))
    fig_gauge.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

# --- 9. قسم تصدير البيانات والمحرك الرياضي (Expanders) ---
st.markdown("---")
col_export, col_math = st.columns(2)

with col_export:
    st.markdown("### 💾 استخراج التقرير الرقمي")
    st.markdown("يمكنك تحميل نتائج المحاكاة اللحظية لتحليلها في برامج خارجية مثل Excel أو MATLAB.")
    # إنشاء DataFrame
    df = pd.DataFrame({'Time (s)': t, 'Displacement (mm)': displacement, 'Velocity (m/s)': velocity})
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 تحميل البيانات (Download CSV)",
        data=csv,
        file_name='Runway_Simulation_Data.csv',
        mime='text/csv',
    )

with col_math:
    with st.expander("⚙️ المحرك الرياضي (Mathematical Engine)"):
        st.markdown("يعتمد هذا النظام على حل معادلة الاهتزاز الحر المخمد (Damped Free Vibration) باستخدام طريقة Runge-Kutta:")
        st.latex(r"m\frac{d^2x}{dt^2} + c\frac{dx}{dt} + kx = 0")
        st.markdown("حيث تم احتساب نسبة التخميد وفقاً للقانون:")
        st.latex(r"\zeta = \frac{c}{2\sqrt{km}}")

# --- حقوق الملكية والتفاصيل الأكاديمية ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #8a94a6; font-size: 15px; background-color: #1e1e2f; padding: 10px; border-radius: 10px; border: 1px solid #333;'>
    👨‍💻 <b>إعداد وتصميم الطالب:</b> علي حيدر اموري (المرحلة الثالثة)<br>
    🎓 <b>إشراف:</b> د. محمد جواد<br>
    🏛️ <b>قسم هندسة الملاحة والتوجيه - مادة الاهتزازات</b> © 2026
</div>
""", unsafe_allow_html=True)