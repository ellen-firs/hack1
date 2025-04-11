import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Название дашборда
st.set_page_config(page_title="Анализ теплопотребления", layout="wide")
st.markdown("## 📊 Анализ теплопотребления и температуры по № ОДПУ")

# Загрузка данных
uploaded_file = st.file_uploader("📂 Загрузите CSV-файл с показаниями", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding="cp1251", delimiter=';', parse_dates=['Дата текущего показания'], dayfirst=True)

    # Удалим лишние пробелы и приведем к нужному формату
    df.columns = df.columns.str.strip()
    df['№ ОДПУ'] = df['№ ОДПУ'].astype(str).str.strip()
    df['МесяцГод'] = df['Дата текущего показания'].dt.to_period('M').astype(str)

    # Температурная карта
    temperature_map = {
        "2021-07": None, "2021-08": None, "2021-09": None, "2021-10": 6.70, "2021-11": -1, "2021-12": -5.18,
        "2022-01": -11.50, "2022-02": -6.74, "2022-03": -5.15, "2022-04": 5.65, "2022-05": None, "2022-06": None,
        "2022-07": None, "2022-08": None, "2022-09": None, "2022-10": 7.14, "2022-11": -1.61, "2022-12": -10.90,
        "2023-01": -12.75, "2023-02": -8.94, "2023-03": -2.27, "2023-04": 7.82, "2023-05": None, "2023-06": None
    }

    # Выпадающий список с ОДПУ
    available_odpu = df["№ ОДПУ"].unique()
    selected_odpu = st.selectbox("Выберите № ОДПУ", available_odpu)

    # Фильтрация данных по выбранному ОДПУ
    df_filtered = df[df["№ ОДПУ"] == selected_odpu].copy()

    # Агрегирование по месяцам
    df_monthly = df_filtered.groupby("МесяцГод")["Текущее потребление, Гкал"].sum().reset_index()
    df_monthly = df_monthly.sort_values("МесяцГод")

    # Добавление температуры
    df_monthly["Температура, °C"] = df_monthly["МесяцГод"].map(temperature_map)

    # Построение графика
    st.markdown("### 📉 График потребления и температуры")

    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Гистограмма по потреблению
    bars = ax1.bar(df_monthly["МесяцГод"], df_monthly["Текущее потребление, Гкал"], color='orange', label='Потребление, Гкал')
    ax1.set_ylabel("Потребление, Гкал", color='orange')
    ax1.tick_params(axis='y', labelcolor='orange')
    ax1.set_xticklabels(df_monthly["МесяцГод"], rotation=45, ha='right')

    # Линия температуры
    ax2 = ax1.twinx()
    ax2.plot(df_monthly["МесяцГод"], df_monthly["Температура, °C"], color='blue', marker='o', linewidth=2, label='Температура, °C')
    ax2.set_ylabel("Температура, °C", color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')

    # Заголовок и легенда
    plt.title(f"Сравнение потребления тепла и температуры ({selected_odpu})", fontsize=14)
    fig.tight_layout()
    st.pyplot(fig)

    # Дополнительная таблица
    st.markdown("### 📄 Таблица значений")
    st.dataframe(df_monthly.rename(columns={
        "МесяцГод": "Месяц",
        "Текущее потребление, Гкал": "Потребление, Гкал",
        "Температура, °C": "Температура, °C"
    }), use_container_width=True)
else:
    st.warning("Пожалуйста, загрузите CSV-файл для начала анализа.")
