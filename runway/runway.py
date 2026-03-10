import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.integrate import odeint

# --- 1. إعدادات الصفحة الاحترافية والمتجاوبة ---
st.set_page_config(page_title="Advanced Runway Simulator", page_icon="✈️", layout="wide", initial_sidebar_state="expanded")

# --- 2. ستايل CSS מתקדמת لتنسيق العربي المتجاوب (Responsive RTL Fix) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');
    
    /* تنسيق التطبيق بالكامل ليناسب العربي */
    html, body, [class*="css"], .stApp {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* إصلاح مشكلة انضغاط النصوص والالتفاف العمودي (حل مشكلة image_9.png) */
    h1, h2, h3, p, label, .stMarkdown {
        white-space: normal !important; /* يمنع النصوص من أن تنضغط عمودياً */
        word-wrap: break-word !important; /* يسمح بالالتفاف العادي */
    }

    /* تنسيق الكروت الهندسية لتكون متجاوبة (Metric Containers) */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #1e1e2f, #2a2a40);
        border-radius: 12px;
        padding: 15px !important;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.3);
        border-left: 4px solid #00f5d4;
        width: auto !important; /* يجعل العرض تلقائي */
        max-width: 100% !important;
        margin-bottom: 10px; /* مسافة بين الكروت على الموبايل */
    }
    
    /* تنسيق النصوص داخل الكروت */
    div[data-testid="metric-container"] label {
        color: #a8b2d1 !important;
        font-size: 14px !important;
        font-weight: 500;
    }
    div[data-testid="metric-container"] div {
        color: #00f5d4 !important;
        font-weight: bold;
        font-size: 20px !important; /* تكبير بسيط للقيمة لتكون أوضح */
    }

    /* جعل التبويبات متجاوبة وعربية */
    .stTabs [data-baseweb="tab-list"] {
        flex-direction: row-reverse !important;
        justify-content: center;
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
    }
    
    /* تنسيق العنوان الرئيسي ليكون متمركزاً ومتجاوباً */
    .main-header-area {
        text-align: center !important;
        margin-bottom: 25px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. تصميم العنوان المعدل (المتجاوب) ---
st.markdown("""
<div class='main-header-area'>
    <span style='font-size: 50px;'>🛫</span>
    <h1 style='margin: 0; padding-top: 10px;'>نظام المحاكاة المتقدم لاهتزازات مدارج المطارات</h1>
    <p style='margin: 0; color: #888;'>Advanced Dynamic Pavement Response Simulator (ADPRS) - V3.1 Fixed</p>
</div>
<hr style='border-color: #333; margin: 10px 0;'>
""", unsafe_allow_html=True)

# --- 4. الدالة الفيزيائية ---
def runway_model(y, t, m, c, k):
    return [y[1], -(c/m)*y[1] - (k/m)*y[0]]

# --- 5. لوحة التحكم الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎛️ وحدة التحكم المركزية</h2>", unsafe_allow_html=True)
    st.markdown("يرجى إدخال معاملات النظام الميكانيكي:")
    
    aircraft_type = st.selectbox("✈️ نوع الطائرة (الكتلة - m)", [
        "Boeing 737 (66,000 kg)",
        "Airbus A320 (67,400 kg)",
        "Boeing 777 (200,000 kg)",
        "Antonov An-225 (285,000 kg)"
    ])
    m_val = float(aircraft_type.split('(')[1].split()[0].replace(',', ''))
    
    runway_type = st.selectbox("🛣️ خواص المدرج (معامل التخميد - c)", [
        "قديم ومتهالك - 500000 N.s/m",
        "قياسي (أسفلت) - 1500000 N.s/m",
        "حديث (خرسانة) - 4000000 N.s/m"
    ])
    c_val = float(runway_type.split('-')[1].split()[0].strip())
    
    k_val = st.number_input("🏗️ صلابة المدرج (Stiffness - k) [N/m]", value=50000000.0, step=1000000.0, format="%f")
    
    v0 = st.slider("🛬 سرعة الارتطام العمودية (Sink Rate)", min_value=-6.0, max_value=-0.5, value=-3.0, step=0.5)
    
    st.markdown("---")
    st.success("🟢 النظام متصل وجاهز.")

# --- 6. العمليات الحسابية المتقدمة ---
t = np.linspace(0, 5, 1000) # تقليل الدقة قليلاً لسرعة الموبايل
sol = odeint(runway_model, [0.0, v0], t, args=(m_val, c_val, k_val))
displacement_mm = sol[:, 0] * 1000 # تحويل إلى مليمتر
velocity = sol[:, 1]

# حسابات هندسية دقيقة
max_disp_mm = abs(np.min(displacement_mm))
impact_force_kN = (k_val * (abs(np.min(sol[:, 0])))) / 1000
damping_ratio = c_val / (2 * np.sqrt(k_val * m_val))

# حساب وقت الاستقرار (Settling Time) - دقة أعلى
try:
    threshold_mm = 0.05 * max_disp_mm
    settled_indices = np.where(np.abs(displacement_mm) > threshold_mm)[0]
    settling_time = t[settled_indices[-1]] if len(settled_indices) > 0 else 0.0
except:
    settling_time = 0.0

# حالة التخميد
if damping_ratio < 1:
    damping_status = "Underdamped (مخمد جزئياً)"
elif damping_ratio == 1:
    damping_status = "Critically Damped (تخميد حرج)"
else:
    damping_status = "Overdamped (فوق المخمد)"

# --- 7. التبويبات المتجاوبة (Responsive Tabs) ---
# استخدام التبويبات لتنظيم الشاشة الضيقة
tab1, tab2, tab3 = st.tabs(["📊 المؤشرات الفورية", "📈 الرسم البياني (Wave)", "⚙️ المحرك الرياضي"])

with tab1:
    # --- عرض الـ Dashboards بشكل عمودي متجاوب على الموبايل ---
    st.markdown("### 📋 لوحة المؤشرات الهندسية (KPIs)")
    # استخدام st.columns بس Streamlit راح ينزلهم تلقائياً جوه بعض على الموبايل
    m1, m2 = st.columns(2)
    with m1:
        st.metric("Max Deflection", f"{max_disp_mm:.2f} mm", "أقصى هبوط للتبليط")
        st.metric("Impact Force", f"{impact_force_kN:.1f} kN", "قوة الارتطام")
    with m2:
        st.metric("Damping Ratio - ζ", f"{damping_ratio:.3f}", damping_status, delta_color="off")
        st.metric("Settling Time", f"{settling_time:.2f} sec", "وقت الاستقرار")
        
    st.markdown("---")
    st.markdown("### ⚠️ مؤشر الخطر الإنشائي")
    # الـ Gauge Chart نحطه جوه تبويب لوحده أو نعطيه مساحة كاملة
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = max_disp_mm,
        title = {'text': "مستوى الإجهاد الإنشائي (mm)", 'font': {'size': 18, 'color': 'white'}},
        gauge = {
            'axis': {'range': [0, 150], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#1e1e2f", 'thickness': 0.2},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': "#00b4d8"}, # آمن
                {'range': [40, 90], 'color': "#ffb703"}, # تحذير
                {'range': [90, 150], 'color': "#ef233c"}  # خطر
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': max_disp_mm}
        }
    ))
    fig_gauge.update_layout(template="plotly_dark", height=350, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

with tab2:
    st.markdown("### 📈 استجابة الإزاحة الزمنية (Transient Deflection)")
    fig_wave = go.Figure()
    fig_wave.add_trace(go.Scatter(
        x=t, y=displacement_mm,
        mode='lines',
        name='الإزاحة (Deflection)',
        line=dict(color='#00f5d4', width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 245, 212, 0.1)'
    ))
    # خط الصفر
    fig_wave.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="حالة الاستقرار")
    
    fig_wave.update_layout(
        xaxis_title="الزمن (sec)",
        yaxis_title="الإزاحة (mm)",
        hovermode="x unified",
        template="plotly_dark",
        height=400, # تقليل الطول قليلاً ليناسب الموبايل
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig_wave, use_container_width=True)

with tab3:
    st.markdown("### ⚙️ المحرك الرياضي وتحميل البيانات")
    with st.expander("⚙️ المعادلات الفيزيائية المستخدمة"):
        st.markdown("يعتمد هذا النظام على حل معادلة الاهتزاز الحر المخمد (Damped Free Vibration):")
        st.latex(r"m\frac{d^2x}{dt^2} + c\frac{dx}{dt} + kx = 0")
        st.markdown("نسبة التخميد (Damping Ratio):")
        st.latex(r"\zeta = \frac{c}{2\sqrt{km}}")
    
    st.markdown("---")
    # زر تصدير البيانات
    df = pd.DataFrame({'Time (s)': t, 'Displacement (mm)': displacement_mm, 'Velocity (m/s)': velocity})
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 تحميل بيانات المحاكاة (CSV)",
        data=csv,
        file_name='Runway_Simulation_Data.csv',
        mime='text/csv',
        use_container_width=True # الزر يملأ عرض الموبايل
    )

# --- حقوق الملكية والتفاصيل الأكاديمية المعدلة ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #8a94a6; font-size: 14px; background-color: #1e1e2f; padding: 15px; border-radius: 10px; border: 1px solid #333;'>
    👨‍💻 <b>إعداد وتصميم الطالب:</b> علي حيدر اموري (المرحلة الثالثة)<br>
    🎓 <b>إشراف:</b> د. محمد جواد<br>
    🏛️ قسم هندسة الملاحة والتوجيه - مادة الاهتزازات © 2024
</div>
""", unsafe_allow_html=True)
