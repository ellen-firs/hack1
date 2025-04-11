import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 Анализ теплопотребления и температуры по № ОДПУ")

# Загрузка данных
df = pd.read_csv("merge3 (1).csv", encoding="cp1251")
df["Дата текущего показания"] = pd.to_datetime(df["Дата текущего показания"], errors="coerce", dayfirst=True)

# Предобработка
df = df.dropna(subset=["Дата текущего показания", "Текущее потребление, Гкал", "№ ОДПУ"])
df["МесяцГод"] = df["Дата текущего показания"].dt.to_period("M").astype(str)
df["Текущее потребление, Гкал"] = pd.to_numeric(df["Текущее потребление, Гкал"], errors="coerce")
df = df.sort_values("Дата текущего показания")

# Выбор ОДПУ
odpu_list = df["№ ОДПУ"].dropna().unique()
selected_odpu = st.selectbox("Выберите № ОДПУ", odpu_list)

filtered_df = df[df["№ ОДПУ"] == selected_odpu].copy()
filtered_df = filtered_df.dropna(subset=["Текущее потребление, Гкал"])
filtered_df["МесяцГод"] = filtered_df["Дата текущего показания"].dt.strftime("%b.%y")

# Сопоставление температуры по месяцам (сопоставим вручную!)
temperature_map = {
    "Jul.21": None, "Aug.21": None, "Sep.21": None, "Oct.21": 6.70, "Nov.21": -1, "Dec.21": -5.18,
    "Jan.22": -11.50, "Feb.22": -6.74, "Mar.22": -5.15, "Apr.22": 5.65, "May.22": None, "Jun.22": None,
    "Jul.22": None, "Aug.22": None, "Sep.22": None, "Oct.22": 7.14, "Nov.22": -1.61, "Dec.22": -10.90,
    "Jan.23": -12.75, "Feb.23": -8.94, "Mar.23": -2.27, "Apr.23": 7.82, "May.23": None, "Jun.23": None
}

# Приводим даты к англ. сокращениям для маппинга
month_map = {
    "янв": "Jan", "фев": "Feb", "мар": "Mar", "апр": "Apr", "май": "May", "июн": "Jun",
    "июл": "Jul", "авг": "Aug", "сен": "Sep", "окт": "Oct", "ноя": "Nov", "дек": "Dec"
}
filtered_df["МесяцГод_en"] = filtered_df["Дата текущего показания"].dt.strftime("%b.%y")
filtered_df["МесяцГод_en"] = filtered_df["МесяцГод_en"].replace(month_map, regex=True)
filtered_df["Температура"] = filtered_df["МесяцГод_en"].map(temperature_map)

# 📈 График: потребление + температура
st.subheader("📉 График потребления и температуры")

fig, ax1 = plt.subplots(figsize=(14, 6))

# Потребление (гистограмма)
ax1.bar(filtered_df["МесяцГод"], filtered_df["Текущее потребление, Гкал"], color='orange', label='Потребление, Гкал')
ax1.set_ylabel("Потребление, Гкал", color='orange')
ax1.tick_params(axis='y', labelcolor='orange')
ax1.set_xticklabels(filtered_df["МесяцГод"], rotation=45)

# Температура (линия)
ax2 = ax1.twinx()
ax2.plot(filtered_df["МесяцГод"], filtered_df["Температура"], color='blue', marker='o', label='Температура')
ax2.set_ylabel("Температура, °C", color='blue')
ax2.tick_params(axis='y', labelcolor='blue')

fig.tight_layout()
st.pyplot(fig)
