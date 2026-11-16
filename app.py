import re
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="ClassMate AI", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.stApp {background:#0b1020;color:#eef2ff}
[data-testid="stSidebar"] {background:#111a2e}
.block-container {padding-top:2rem;max-width:1200px}
.hero {padding:24px;border:1px solid #263653;border-radius:18px;background:linear-gradient(120deg,#172642,#10182b)}
.metric {padding:18px;border:1px solid #263653;border-radius:14px;background:#111a2e}
</style>
""", unsafe_allow_html=True)

st.title("🎓 ClassMate AI")
st.caption("مساعدك الذكي لتنظيم محادثات الدفعة")
st.markdown('<div class="hero"><h2>كل المهم في جروب الدفعة، في مكان واحد</h2><p>ارفع تصدير محادثة WhatsApp بصيغة TXT واستخرج الإعلانات والمهام والرسائل المهمة.</p></div>', unsafe_allow_html=True)

def parse_chat(raw):
    messages, current = [], None
    pattern = re.compile(r"^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),?\s+(\d{1,2}:\d{2})\s+-\s+([^:]+):\s?(.*)$")
    for line in raw.splitlines():
        m = pattern.match(line)
        if m:
            if current: messages.append(current)
            current = {"date":m.group(1), "time":m.group(2), "sender":m.group(3).strip(), "text":m.group(4).strip()}
        elif current:
            current["text"] += "\n" + line
    if current: messages.append(current)
    return messages

sample = """15/11/2026, 10:15 - دكتور المادة: المحاضرة القادمة يوم الثلاثاء الساعة 10 صباحًا.
15/11/2026, 10:20 - أحمد: تسليم الواجب يوم الخميس القادم.
15/11/2026, 10:25 - سارة: تم رفع ملف المحاضرة PDF على الجروب.
15/11/2026, 10:30 - دكتور المادة: إعلان مهم: تم تغيير موعد السكشن إلى الأربعاء."""
if "raw_chat" not in st.session_state:
    st.session_state.raw_chat = ""

with st.sidebar:
    st.header("القائمة")
    page = st.radio("انتقل إلى", ["نظرة عامة","ملخص المحادثة","الإعلانات","المهام والمواعيد","الملفات","اسأل المحادثة","استيراد المحادثة"])
    st.divider()
    st.caption("نسخة جامعية أولية — لا تتصل تلقائيًا بواتساب")

if page == "استيراد المحادثة":
    st.subheader("استيراد محادثة WhatsApp")
    uploaded = st.file_uploader("ارفع ملف TXT", type=["txt"])
    if uploaded:
        st.session_state.raw_chat = uploaded.getvalue().decode("utf-8", errors="replace")
        st.success("تم تحميل الملف. انتقل إلى نظرة عامة أو الأقسام الأخرى.")
    if st.button("تحميل محادثة تجريبية"):
        st.session_state.raw_chat = sample
        st.success("تم تحميل المحادثة التجريبية.")
elif not st.session_state.raw_chat:
    st.info("ابدأ بتحميل محادثة من قسم «استيراد المحادثة»، أو استخدم البيانات التجريبية.")
    if st.button("جرّب بيانات تجريبية"):
        st.session_state.raw_chat = sample
        st.rerun()
else:
    messages = parse_chat(st.session_state.raw_chat)
    texts = [m["text"] for m in messages]
    announcements = [m for m in messages if any(k in m["text"].lower() for k in ["إعلان","مهم","تنبيه","announcement"])]
    tasks = [m for m in messages if any(k in m["text"].lower() for k in ["واجب","تسليم","موعد","امتحان","محاضرة","السكشن","deadline"])]
    files_found = [m for m in messages if any(k in m["text"].lower() for k in ["pdf","ملف","رابط","ppt","doc"])]

    if page == "نظرة عامة":
        st.subheader("نظرة عامة")
        cols = st.columns(4)
        for col, value, label in zip(cols,[len(messages),len(announcements),len(tasks),len(files_found)],["الرسائل","الإعلانات","المهام والمواعيد","رسائل الملفات"]):
            with col: st.markdown(f'<div class="metric"><h2>{value}</h2><p>{label}</p></div>', unsafe_allow_html=True)
        st.markdown("### آخر الرسائل")
        for m in messages[-5:]:
            st.info(f'**{m["sender"]}** — {m["date"]} {m["time"]}\n\n{m["text"]}')
    elif page == "ملخص المحادثة":
        st.subheader("ملخص المحادثة")
        st.write(f"تم العثور على {len(messages)} رسالة.")
        if messages:
            st.write("**أبرز الموضوعات المستخرجة مبدئيًا:**")
            for m in (announcements + tasks + files_found)[:10]:
                st.write(f'• {m["text"]}')
        st.caption("هذا ملخص أولي يعتمد على قواعد وكلمات مفتاحية، وليس تلخيصًا بنموذج AI حتى الآن.")
    elif page == "الإعلانات":
        st.subheader("الإعلانات والتنبيهات")
        if announcements:
            for m in announcements: st.warning(f'**{m["sender"]}:** {m["text"]}')
        else: st.write("لم يتم العثور على إعلانات واضحة.")
    elif page == "المهام والمواعيد":
        st.subheader("المهام والمواعيد")
        if tasks:
            for m in tasks: st.info(f'**{m["sender"]}:** {m["text"]}')
        else: st.write("لم يتم العثور على مهام واضحة.")
    elif page == "الملفات":
        st.subheader("رسائل الملفات")
        if files_found:
            for m in files_found: st.write(f'📎 **{m["sender"]}:** {m["text"]}')
        else: st.write("لم يتم العثور على رسائل ملفات.")
    elif page == "اسأل المحادثة":
        st.subheader("ابحث داخل المحادثة")
        q = st.text_input("اكتب كلمة أو سؤالًا")
        if q:
            hits = [m for m in messages if q.lower() in m["text"].lower()]
            st.write(f"نتائج البحث: {len(hits)}")
            for m in hits: st.write(f'**{m["sender"]}:** {m["text"]}')
            if not hits: st.info("لا توجد رسائل تطابق عبارة البحث.")
        st.caption("البحث الحالي نصي، وسيتم تطويره لاحقًا ليصبح مساعدًا ذكيًا.")
    if st.button("مسح المحادثة الحالية"):
        st.session_state.raw_chat = ""
        st.rerun()
