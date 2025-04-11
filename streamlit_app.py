import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Анализ теплопотребления", layout="wide")
st.markdown("## 📊 Анализ теплопотребления и температуры по № ОДПУ")

uploaded_file = st.file_uploader("📂 Загрузите CSV-файл с показаниями", type="csv")

if uploaded_file:
    try:
        # Пробуем сначала просто считать и вывести заголовки
        df_preview = pd.read_csv(uploaded_file, encoding="cp1251", delimiter=';')
        st.markdown("### 🧾 Заголовки в файле:")
        st.write(df_preview.columns.tolist())

        # Определим подходящую колонку с датой
        if 'Дата текущего показания' in df_preview.columns:
            df = pd.read_csv(uploaded_file, encoding="cp1251", delimiter=';', parse_dates=['Дата текущего показания'], dayfirst=True)
        else:
            st.error("⛔️ Не найдена колонка 'Дата текущего показания'. Пожалуйста, проверьте заголовки в вашем CSV.")
            st.stop()

        # Очистка и подготовка
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

        # Выбор ОДПУ
        available_odpu = df["№ ОДПУ"].unique()
        selected_odpu = st.selectbox("Выберите № ОДПУ", available_odpu)

        df_filtered = df[df["№ ОДПУ"] == selected_odpu].copy()
        df_monthly = df_filtered.groupby("МесяцГод")["Текущее потребление, Гкал"].sum().reset_index()
        df_monthly = df_monthly.sort_values("МесяцГод")
        df_monthly["Температура, °C"] = df_monthly["МесяцГод"].map(temperature_map)

        st.markdown("### 📉 График потребления и температуры")

        fig, ax1 = plt.subplots(figsize=(14, 6))
        ax1.bar(df_monthly["МесяцГод"], df_monthly["Текущее потребление, Гкал"], color='orange')
        ax1.set_ylabel("Потребление, Гкал", color='orange')
        ax1.tick_params(axis='y', labelcolor='orange')
        ax1.set_xticklabels(df_monthly["МесяцГод"], rotation=45, ha='right')

        ax2 = ax1.twinx()
        ax2.plot(df_monthly["МесяцГод"], df_monthly["Температура, °C"], color='blue', marker='o', linewidth=2)
        ax2.set_ylabel("Температура, °C", color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')

        plt.title(f"Сравнение потребления и температуры ({selected_odpu})")
        fig.tight_layout()
        st.pyplot(fig)

        st.markdown("### 📄 Таблица данных")
        st.dataframe(df_monthly, use_container_width=True)

    except Exception as e:
        st.error(f"🚨 Ошибка при обработке файла: {str(e)}")
else:
    st.info("Пожалуйста, загрузите CSV-файл для анализа.")
