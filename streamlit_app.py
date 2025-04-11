import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Анализ теплопотребления", layout="wide")
st.title("📊 Анализ теплопотребления по № ОДПУ")

uploaded_file = st.file_uploader("📂 Загрузите файл merge3.csv", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="cp1251")
        df.columns = df.columns.str.strip().str.strip('"')

        # Парсинг даты
        df["Дата текущего показания"] = pd.to_datetime(df["Дата текущего показания"], errors="coerce", dayfirst=True)

        # Очистка и подготовка
        df = df.dropna(subset=["Дата текущего показания", "Текущее потребление, Гкал", "№ ОДПУ"])
        df["№ ОДПУ"] = df["№ ОДПУ"].astype(str).str.strip()
        df["МесяцГод"] = df["Дата текущего показания"].dt.to_period("M").astype(str)
        df["Текущее потребление, Гкал"] = pd.to_numeric(df["Текущее потребление, Гкал"], errors="coerce")

        # Температуры — только для известных месяцев
        temperature_map = {
            "2021-07": None, "2021-08": None, "2021-09": None, "2021-10": 6.70, "2021-11": -1, "2021-12": -5.18,
            "2022-01": -11.50, "2022-02": -6.74, "2022-03": -5.15, "2022-04": 5.65, "2022-05": None, "2022-06": None,
            "2022-07": 7.14, "2022-08": -1.61, "2022-09": -10.90, "2022-10": -12.75, "2022-11": -8.94, "2022-12": -2.27,
            "2023-01": 7.82, "2023-02": None, "2023-03": None, "2023-04": None, "2023-05": None, "2023-06": None
        }

        selected_odpu = st.selectbox("Выберите № ОДПУ", sorted(df["№ ОДПУ"].unique()))
        df_filtered = df[df["№ ОДПУ"] == selected_odpu].copy()

        df_monthly = (
            df_filtered.groupby("МесяцГод", as_index=False)["Текущее потребление, Гкал"]
            .sum()
            .sort_values("МесяцГод")
        )
        df_monthly["Температура, °C"] = df_monthly["МесяцГод"].map(temperature_map)

        # 📊 Построение графика
        st.markdown("### 📉 Гистограмма потребления + график температуры")

        fig, ax1 = plt.subplots(figsize=(14, 6))

        # Гистограмма: потребление
        ax1.bar(df_monthly["МесяцГод"], df_monthly["Текущее потребление, Гкал"], color="orange", label="Потребление, Гкал")
        ax1.set_ylabel("Потребление, Гкал", color="orange")
        ax1.tick_params(axis="y", labelcolor="orange")
        ax1.set_xticks(range(len(df_monthly)))
        ax1.set_xticklabels(df_monthly["МесяцГод"], rotation=45, ha="right")

        # Линия: температура
        ax2 = ax1.twinx()
        ax2.plot(df_monthly["МесяцГод"], df_monthly["Температура, °C"], color="blue", marker="o", label="Температура, °C")
        ax2.set_ylabel("Температура, °C", color="blue")
        ax2.tick_params(axis="y", labelcolor="blue")

        # Легенда и оформление
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")
        plt.title(f"📊 Потребление тепла и температура — № ОДПУ {selected_odpu}")
        fig.tight_layout()
        st.pyplot(fig)

        # 📋 Таблица
        st.markdown("### 📄 Таблица значений")
        st.dataframe(df_monthly, use_container_width=True)

    except Exception as e:
        st.error(f"🚨 Ошибка при обработке файла: {e}")
else:
    st.info("📥 Пожалуйста, загрузите файл merge3.csv для начала.")
