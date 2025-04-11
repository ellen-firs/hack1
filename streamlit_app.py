import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 Анализ теплопотребления по № ОДПУ")

# Загрузка данных
df = pd.read_csv("merge3 (1).csv", encoding="cp1251", parse_dates=["Дата текущего показания"], dayfirst=True)

# Предобработка
df = df.dropna(subset=["Дата текущего показания", "Текущее потребление, Гкал", "№ ОДПУ"])
df["МесяцГод"] = df["Дата текущего показания"].dt.to_period("M").astype(str)
df = df.sort_values("Дата текущего показания")
df["Текущее потребление, Гкал"] = pd.to_numeric(df["Текущее потребление, Гкал"], errors="coerce")

# Фильтр по № ОДПУ
odp_list = df["№ ОДПУ"].dropna().unique()
selected_odpu = st.selectbox("Выберите № ОДПУ", odp_list)

filtered_df = df[df["№ ОДПУ"] == selected_odpu].copy()
filtered_df["Разница"] = filtered_df["Текущее потребление, Гкал"].diff()
filtered_df["Изменение (%)"] = filtered_df["Разница"] / filtered_df["Текущее потребление, Гкал"].shift(1) * 100

# 📌 Информация об объекте
obj_info = filtered_df.iloc[-1]
st.markdown(f"""
**📍 Адрес:** {obj_info['Адрес объекта']}  
**🏢 Тип объекта:** {obj_info['Тип объекта']}  
**🏗️ Год постройки:** {obj_info['Дата постройки'][:10]}  
**📐 Этажность:** {obj_info['Этажность объекта']}  
**📏 Площадь (м²):** {obj_info['Общая площадь объекта']}
""")

# 📉 График потребления
st.subheader("📉 Потребление тепловой энергии")

fig, ax = plt.subplots(figsize=(14, 6))
bars = ax.bar(filtered_df["МесяцГод"], filtered_df["Текущее потребление, Гкал"], color='orange')
ax.set_ylabel("Гкал")
ax.set_title("Потребление тепла по месяцам")
ax.set_xticklabels(filtered_df["МесяцГод"], rotation=45)
fig.tight_layout()
st.pyplot(fig)

# 📊 Таблица сравнения
st.subheader("📊 Сравнение с предыдущим месяцем")

def highlight_anomaly(val):
    try:
        if val > 30:
            return "background-color: #ffcccc"  # красный
        elif val < -30:
            return "background-color: #ccffcc"  # зелёный
    except:
        pass
    return ""

styled_df = filtered_df[["МесяцГод", "Текущее потребление, Гкал", "Разница", "Изменение (%)"]].style.applymap(highlight_anomaly, subset=["Изменение (%)"])
st.dataframe(styled_df, use_container_width=True)

# ⚠️ Аномалии
st.subheader("⚠️ Обнаруженные аномалии")
threshold = st.slider("Порог аномального изменения (%)", 10, 100, 30)
anom = filtered_df[filtered_df["Изменение (%)"].abs() > threshold]
st.write(f"Найдено аномалий: {len(anom)}")
st.dataframe(anom[["МесяцГод", "Текущее потребление, Гкал", "Разница", "Изменение (%)"]])
