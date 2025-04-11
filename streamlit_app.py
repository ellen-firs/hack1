import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Анализ теплопотребления", layout="wide")
st.markdown("## 📊 Анализ теплопотребления и температуры по № ОДПУ")

uploaded_file = st.file_uploader("📂 Загрузите CSV-файл с показаниями", type="csv")

if uploaded_file:
    try:
        # Сначала считываем без парсинга дат
        df_raw = pd.read_csv(uploaded_file, encoding="cp1251", delimiter=';')
        df_raw.columns = df_raw.columns.str.strip().str.strip('"')  # удалим кавычки и пробелы

        st.markdown("### 🧾 Заголовки после очистки:")
        st.write(df_raw.columns.tolist())

        if "Дата текущего показания" not in df_raw.columns:
            st.error("⛔️ Даже после очистки не найдена колонка 'Дата текущего показания'.")
            st.stop()

        # Теперь читаем с парсингом дат
        uploaded_file.seek(0)  # возвращаемся в начало файла
        df = pd.read_csv(uploaded_file, encoding="cp1251", delimiter=';', parse_dates=['"Дата текущего показания"'], dayfirst=True)
        df.columns = df.columns.str.strip().str.strip('"')

        df['№ ОДПУ'] = df['№ ОДПУ'].astype(str).str.strip()
        df['МесяцГод'] = df['Дата текущего показания'].dt.to_period('M').astype(str)

        temperature_map = {
            "2021-10": 6.70, "2021-11": -1, "2021-12": -5.18,
            "2022-01": -11.50, "2022-02": -6.74, "2022-03": -5.15, "2022-04": 5.65,
            "2022-10": 7.14, "2022-11": -1.61, "2022-12": -10.90,
            "2023-01": -12.75, "2023-02": -8.94, "2023-03": -2.27, "2023-04": 7.82
        }

        selected_odpu = st.selectbox("Выберите № ОДПУ", df["№ ОДПУ"].unique())

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
