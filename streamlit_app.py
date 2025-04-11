import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Анализ теплопотребления", layout="wide")
st.title("📊 Анализ теплопотребления по № ОДПУ")

uploaded_file = st.file_uploader("📂 Загрузите файл merge3.csv", type="csv")

if uploaded_file:
    try:
        # Загрузка и предварительная очистка
        df = pd.read_csv(uploaded_file, encoding="cp1251")
        df.columns = df.columns.str.strip().str.strip('"')

        # Парсинг даты с автоопределением формата
        df["Дата текущего показания"] = pd.to_datetime(df["Дата текущего показания"], errors="coerce", infer_datetime_format=True)

        # Числовое значение и очистка
        df["Текущее потребление, Гкал"] = pd.to_numeric(df["Текущее потребление, Гкал"], errors="coerce")
        df["№ ОДПУ"] = df["№ ОДПУ"].astype(str).str.strip()

        # Удаляем пустые строки по ключевым полям
        df = df.dropna(subset=["Дата текущего показания", "Текущее потребление, Гкал", "№ ОДПУ"])

        # Группировка по месяцу
        df["МесяцГод"] = df["Дата текущего показания"].dt.to_period("M").astype(str)

        # Температура — словарь по МесяцГод
        temperature_map = {
            "2021-10": 6.70, "2021-11": -1, "2021-12": -5.18,
            "2022-01": -11.50, "2022-02": -6.74, "2022-03": -5.15, "2022-04": 5.65,
            "2022-07": 7.14, "2022-08": -1.61, "2022-09": -10.90, "2022-10": -12.75, "2022-11": -8.94, "2022-12": -2.27,
            "2023-01": 7.82,
            "2023-10": 6.0, "2023-11": -3.5, "2023-12": -6.2,
            "2024-01": -12.8, "2024-02": -9.1, "2024-03": -2.3
        }

        # Интерфейс — выбор ОДПУ
        selected_odpu = st.selectbox("Выберите № ОДПУ", sorted(df["№ ОДПУ"].unique()))
        df_filtered = df[df["№ ОДПУ"] == selected_odpu].copy()

        # Группировка по МесяцГод
        df_monthly = (
            df_filtered.groupby("МесяцГод", as_index=False)["Текущее потребление, Гкал"]
            .sum()
            .sort_values("МесяцГод")
        )
        df_monthly["Температура, °C"] = df_monthly["МесяцГод"].map(temperature_map)

        # График
        st.markdown("### 📉 Потребление тепла + температура по месяцам")

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
        ax2.set_yticks([-15, -10, -5, 0, 5, 10])

        # Легенда
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")
        plt.title(f"📊 Потребление и температура — № ОДПУ {selected_odpu}")
        fig.tight_layout()
        st.pyplot(fig)

        # Таблица
        st.markdown("### 📄 Таблица по месяцам")
        st.dataframe(df_monthly, use_container_width=True)

        # Отладочный вывод
        with st.expander("🛠️ Посмотреть все даты и значения"):
            st.dataframe(df_filtered[["Дата текущего показания", "Текущее потребление, Гкал", "МесяцГод"]])

    except Exception as e:
        st.error(f"🚨 Ошибка: {e}")
else:
    st.info("📥 Пожалуйста, загрузите файл `merge3.csv` для анализа.")
