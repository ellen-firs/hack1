import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Настройка страницы
st.set_page_config(page_title="Анализ теплопотребления", layout="wide")
st.title("📊 Анализ теплопотребления и температуры по № ОДПУ")

# Загрузка файла
uploaded_file = st.file_uploader("📂 Загрузите CSV-файл с показаниями", type="csv")

if uploaded_file:
    try:
        # Чтение CSV с обработкой первой колонки как индекса
        df = pd.read_csv(
            uploaded_file,
            encoding="cp1251",
            sep=",",
            index_col=0,
            parse_dates=["Дата текущего показания"],
            dayfirst=True
        )
        df.columns = df.columns.str.strip()

        # Проверка нужных колонок
        required_cols = ["№ ОДПУ", "Дата текущего показания", "Текущее потребление, Гкал"]
        for col in required_cols:
            if col not in df.columns:
                st.error(f"❌ Не найдена колонка: {col}")
                st.stop()

        # Обработка
        df["№ ОДПУ"] = df["№ ОДПУ"].astype(str)
        df = df.dropna(subset=["Дата текущего показания", "Текущее потребление, Гкал"])
        df["МесяцГод"] = df["Дата текущего показания"].dt.to_period("M").astype(str)

        # Температура по месяцам
        temperature_map = {
            "2021-10": 6.70, "2021-11": -1, "2021-12": -5.18,
            "2022-01": -11.50, "2022-02": -6.74, "2022-03": -5.15, "2022-04": 5.65,
            "2022-10": 7.14, "2022-11": -1.61, "2022-12": -10.90,
            "2023-01": -12.75, "2023-02": -8.94, "2023-03": -2.27, "2023-04": 7.82
        }

        # Выбор № ОДПУ
        selected_odpu = st.selectbox("Выберите № ОДПУ", sorted(df["№ ОДПУ"].unique()))
        df_filtered = df[df["№ ОДПУ"] == selected_odpu].copy()

        # Группировка по месяцу
        df_monthly = (
            df_filtered.groupby("МесяцГод")["Текущее потребление, Гкал"]
            .sum().reset_index()
            .sort_values("МесяцГод")
        )
        df_monthly["Температура, °C"] = df_monthly["МесяцГод"].map(temperature_map)

        # График
        st.markdown("### 📉 График потребления и температуры")
        fig, ax1 = plt.subplots(figsize=(14, 6))

        ax1.bar(df_monthly["МесяцГод"], df_monthly["Текущее потребление, Гкал"], color="orange", label="Потребление, Гкал")
        ax1.set_ylabel("Потребление, Гкал", color="orange")
        ax1.tick_params(axis='y', labelcolor='orange')
        ax1.set_xticklabels(df_monthly["МесяцГод"], rotation=45, ha="right")

        ax2 = ax1.twinx()
        ax2.plot(df_monthly["МесяцГод"], df_monthly["Температура, °C"], color="blue", marker="o", linewidth=2, label="Температура, °C")
        ax2.set_ylabel("Температура, °C", color="blue")
        ax2.tick_params(axis='y', labelcolor='blue')

        plt.title(f"Сравнение потребления и температуры — № ОДПУ {selected_odpu}")
        fig.tight_layout()
        st.pyplot(fig)

        # Таблица
        st.markdown("### 📄 Таблица значений по месяцам")
        st.dataframe(df_monthly, use_container_width=True)

    except Exception as e:
        st.error(f"🚨 Ошибка при обработке файла: {e}")
else:
    st.info("📥 Пожалуйста, загрузите CSV-файл для начала.")
