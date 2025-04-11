import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 Анализ теплопотребления и температуры по № ОДПУ")

# Загрузка данных
df = pd.read_csv("merge3 (1).csv", encoding="cp1251")

# Приведение даты к нужному формату
df["Дата текущего показания"] = pd.to_datetime(df["Дата текущего показания"], errors="coerce")
df["МесяцГод"] = df["Дата текущего показания"].dt.to_period("M").astype(str)

# UI: Выбор ОДПУ
selected_odpu = st.selectbox("Выберите № ОДПУ", df["№ ОДПУ"].unique())

# Фильтруем по ОДПУ
filtered_df = df[df["№ ОДПУ"] == selected_odpu]

# Группировка по месяцам
grouped = filtered_df.groupby("МесяцГод")["Текущее потребление, Гкал"].sum().reset_index()

# Словарь с температурами
temperature_map = {
    "2021-07": None, "2021-08": None, "2021-09": None, "2021-10": 6.70, "2021-11": -1, "2021-12": -5.18,
    "2022-01": -11.50, "2022-02": -6.74, "2022-03": -5.15, "2022-04": 5.65, "2022-05": None, "2022-06": None,
    "2022-07": None, "2022-08": None, "2022-09": None, "2022-10": 7.14, "2022-11": -1.61, "2022-12": -10.90,
    "2023-01": -12.75, "2023-02": -8.94, "2023-03": -2.27, "2023-04": 7.82, "2023-05": None, "2023-06": None
}

# Добавим температуру к данным
grouped["Температура, °C"] = grouped["МесяцГод"].map(temperature_map)

# Построение графика
fig, ax1 = plt.subplots(figsize=(12, 6))

# Столбчатая диаграмма — потребление
ax1.bar(grouped["МесяцГод"], grouped["Текущее потребление, Гкал"], color='orange', label="Потребление, Гкал")
ax1.set_ylabel("Потребление, Гкал", color="orange")
ax1.tick_params(axis='y', labelcolor="orange")
plt.xticks(rotation=45)

# Линейный график — температура
ax2 = ax1.twinx()
ax2.plot(grouped["МесяцГод"], grouped["Температура, °C"], color="blue", marker="o", label="Температура, °C")
ax2.set_ylabel("Температура, °C", color="blue")
ax2.tick_params(axis='y', labelcolor="blue")

# Заголовок и легенда
plt.title("График потребления и температуры")
fig.tight_layout()
st.pyplot(fig)
