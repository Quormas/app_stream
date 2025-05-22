import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Настройка страницы
st.set_page_config(
    page_title="РосСтат Аналитик",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стили CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2563EB;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #EFF6FF;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .stat-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.3s;
    }
    .stat-card:hover {
        transform: translateY(-5px);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E40AF;
    }
    .stat-label {
        font-size: 1rem;
        color: #6B7280;
    }
    .footer {
        text-align: center;
        color: #6B7280;
        font-size: 0.8rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Функция для загрузки данных
@st.cache_data
def load_data():
    # Создаем синтетические данные
    
    # Региональные данные
    regions = ['Москва', 'Санкт-Петербург', 'Владимирская область', 'Краснодарский край', 
               'Свердловская область', 'Новосибирская область', 'Татарстан', 'Калининградская область',
               'Нижегородская область', 'Приморский край', 'Хабаровский край', 'Тюменская область']
    
    regional_data = pd.DataFrame({
        'Регион': regions,
        'Население': [12600000, 5400000, 1350000, 5600000, 4300000, 2800000, 3900000, 1000000,
                      3200000, 1900000, 1300000, 1500000],
        'Средняя_зарплата': [100000, 75000, 35000, 42000, 47000, 45000, 43000, 39000,
                            41000, 48000, 46000, 52000],
        'Инвестиции_млрд': [3500, 1200, 90, 420, 450, 230, 380, 110,
                           350, 280, 240, 390],
        'Индекс_потребления': [120, 110, 95, 105, 100, 98, 103, 97,
                              102, 104, 99, 107]
    })
    
    # Муниципальные данные
    municipalities = []
    populations = []
    regions_list = []
    
    # Создаем список муниципалитетов с разным населением
    for region in regions:
        if region in ['Москва', 'Санкт-Петербург']:
            districts = [f"{region} - Район {i}" for i in range(1, 6)]
            municipalities.extend(districts)
            populations.extend(np.random.randint(200000, 500000, len(districts)))
            regions_list.extend([region] * len(districts))
        else:
            # Административный центр (крупный город)
            municipalities.append(f"{region} - Административный центр")
            populations.append(np.random.randint(300000, 1000000, 1)[0])
            regions_list.append(region)
            
            # Средние города
            mid_cities = [f"{region} - Город {i}" for i in range(2, 5)]
            municipalities.extend(mid_cities)
            populations.extend(np.random.randint(50000, 300000, len(mid_cities)))
            regions_list.extend([region] * len(mid_cities))
            
            # Малые города
            small_cities = [f"{region} - Малый город {i}" for i in range(1, 4)]
            municipalities.extend(small_cities)
            populations.extend(np.random.randint(10000, 50000, len(small_cities)))
            regions_list.extend([region] * len(small_cities))
    
    np.random.seed(42)
    municipal_data = pd.DataFrame({
        'Муниципалитет': municipalities,
        'Регион': regions_list,
        'Население': populations,
        'Средняя_зарплата': [int(np.random.normal(35000, 15000)) for _ in range(len(municipalities))],
        'Количество_предприятий': [int(pop/100 * np.random.uniform(0.8, 1.2)) for pop in populations],
        'Оборот_розничной_торговли_млн': [int(pop/10 * np.random.uniform(0.7, 1.5)) for pop in populations],
        'Индекс_потребления': np.random.randint(80, 130, len(municipalities))
    })
    
    # Корректируем зарплаты в соответствии с регионом
    for idx, row in municipal_data.iterrows():
        region_salary = regional_data[regional_data['Регион'] == row['Регион']]['Средняя_зарплата'].values[0]
        municipal_data.at[idx, 'Средняя_зарплата'] = int(region_salary * np.random.uniform(0.7, 1.2))
    
    # СберИндекс данные (имитация)
    sber_index = pd.DataFrame({
        'Регион': regions,
        'Индекс_потребительской_активности': np.random.randint(90, 120, len(regions)),
        'Индекс_транзакций_общепит': np.random.randint(85, 125, len(regions)),
        'Индекс_транзакций_одежда': np.random.randint(80, 130, len(regions)),
        'Индекс_транзакций_услуги': np.random.randint(85, 115, len(regions)),
        'Средний_чек': np.random.randint(500, 3000, len(regions))
    })
    
        # Добавляем временные ряды для СберИндекса
    months = pd.date_range(start='2022-01-01', periods=24, freq='M')
    sber_time_series = []
    
    for region in regions:
        base_value = np.random.randint(90, 110)
        seasonal_factor = np.sin(np.linspace(0, 2*np.pi, 12)) * 10 + 5
        seasonal_factor = np.tile(seasonal_factor, 2)  # Повторяем для 2 лет
        
        for i, month in enumerate(months):
            trend = i * 0.2  # Небольшой восходящий тренд
            random_factor = np.random.normal(0, 3)
            value = base_value + trend + seasonal_factor[i] + random_factor
            
            sber_time_series.append({
                'Регион': region,
                'Дата': month,
                'Индекс_потребительской_активности': max(80, min(130, value)),
                'Индекс_транзакций_общепит': max(80, min(130, value + np.random.normal(0, 5))),
                'Индекс_транзакций_одежда': max(80, min(130, value + np.random.normal(0, 7))),
                'Индекс_транзакций_услуги': max(80, min(130, value + np.random.normal(0, 4)))
            })
    
    sber_time_series_df = pd.DataFrame(sber_time_series)
    
    return regional_data, municipal_data, sber_index, sber_time_series_df

# Загрузка данных
regional_data, municipal_data, sber_index, sber_time_series = load_data()

# Заголовок приложения
st.markdown('<h1 class="main-header">РосСтат Аналитик</h1>', unsafe_allow_html=True)
st.markdown('<p class="info-box">Анализ российской региональной и муниципальной статистики</p>', unsafe_allow_html=True)

# Боковая панель
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4341/4341050.png", width=100)
st.sidebar.markdown("## Навигация")

# Выбор раздела
page = st.sidebar.radio("Выберите раздел:", 
                       ["Обзор данных", "Региональная статистика", "Муниципальная статистика", 
                        "СберИндекс", "Сравнительный анализ", "Готовые отчеты", "ИИ-Агент"])

# Обзор данных
if page == "Обзор данных":
    st.markdown('<h2 class="sub-header">Обзор доступных данных</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="stat-value">{len(regional_data)}</p>', unsafe_allow_html=True)
        st.markdown('<p class="stat-label">Регионов в базе</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="stat-value">{len(municipal_data)}</p>', unsafe_allow_html=True)
        st.markdown('<p class="stat-label">Муниципалитетов в базе</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="stat-value">{len(sber_time_series["Регион"].unique())}</p>', unsafe_allow_html=True)
        st.markdown('<p class="stat-label">Регионов с данными СберИндекс</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Примеры доступных данных")
    
    tab1, tab2, tab3 = st.tabs(["Региональные данные", "Муниципальные данные", "СберИндекс"])
    
    with tab1:
        st.dataframe(regional_data)
    
    with tab2:
        st.dataframe(municipal_data)
    
    with tab3:
        st.dataframe(sber_index)
    
    st.markdown("### Описание данных")
    st.markdown("""
    В нашей базе содержатся следующие типы данных:
    
    1. **Региональные данные**:
       - Население регионов
       - Средняя заработная плата
       - Объем инвестиций
       - Индекс потребления
    
    2. **Муниципальные данные**:
       - Население муниципалитетов
       - Средняя заработная плата
       - Количество предприятий
       - Оборот розничной торговли
       - Индекс потребления
    
    3. **Данные СберИндекс**:
       - Индекс потребительской активности
       - Индекс транзакций в сфере общепита
       - Индекс транзакций в сфере одежды
       - Индекс транзакций в сфере услуг
       - Средний чек
    """)

# Региональная статистика
elif page == "Региональная статистика":
    st.markdown('<h2 class="sub-header">Региональная статистика</h2>', unsafe_allow_html=True)
    
    # Фильтры
    st.sidebar.markdown("### Фильтры")
    selected_regions = st.sidebar.multiselect("Выберите регионы:", 
                                             options=regional_data['Регион'].unique(),
                                             default=regional_data['Регион'].unique()[:5])
    
    # Фильтрация данных
    filtered_regional_data = regional_data[regional_data['Регион'].isin(selected_regions)]
    
    # Показатели
    metric = st.selectbox("Выберите показатель для анализа:", 
                         ["Население", "Средняя_зарплата", "Инвестиции_млрд", "Индекс_потребления"])
    
    # Визуализация
    st.markdown("### Сравнение регионов")
    
    fig = px.bar(filtered_regional_data, x='Регион', y=metric, 
                color='Регион', text_auto='.2s',
                title=f"{metric} по регионам")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Карта регионов (заглушка, т.к. нет геоданных)
    st.markdown("### Карта регионов")
    st.info("Для отображения интерактивной карты необходимы геоданные регионов. В демо-версии карта недоступна.")
    
    # Таблица с данными
    st.markdown("### Детальные данные")
    st.dataframe(filtered_regional_data)
    
    # Корреляция показателей
      # Корреляция показателей
    st.markdown("### Корреляция показателей")
    
    numeric_cols = ['Население', 'Средняя_зарплата', 'Инвестиции_млрд', 'Индекс_потребления']
    corr_matrix = filtered_regional_data[numeric_cols].corr()
    
    fig = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r',
                   title="Корреляция между показателями")
    st.plotly_chart(fig, use_container_width=True)

# Муниципальная статистика
elif page == "Муниципальная статистика":
    st.markdown('<h2 class="sub-header">Муниципальная статистика</h2>', unsafe_allow_html=True)
    
    # Фильтры
    st.sidebar.markdown("### Фильтры")
    selected_region = st.sidebar.selectbox("Выберите регион:", 
                                         options=sorted(municipal_data['Регион'].unique()))
    
    population_filter = st.sidebar.slider("Население (тыс. человек):", 
                                        min_value=0, 
                                        max_value=int(municipal_data['Население'].max()/1000), 
                                        value=(0, int(municipal_data['Население'].max()/1000)))
    
    # Фильтрация данных
    filtered_municipal_data = municipal_data[
        (municipal_data['Регион'] == selected_region) & 
        (municipal_data['Население'] >= population_filter[0]*1000) & 
        (municipal_data['Население'] <= population_filter[1]*1000)
    ]
    
    # Показатели
    metric = st.selectbox("Выберите показатель для анализа:", 
                         ["Население", "Средняя_зарплата", "Количество_предприятий", 
                          "Оборот_розничной_торговли_млн", "Индекс_потребления"])
    
    # Визуализация
    st.markdown("### Муниципалитеты региона")
    
    if len(filtered_municipal_data) > 0:
        fig = px.bar(filtered_municipal_data, x='Муниципалитет', y=metric, 
                    color='Муниципалитет', text_auto='.2s',
                    title=f"{metric} по муниципалитетам {selected_region}")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Таблица с данными
        st.markdown("### Детальные данные")
        st.dataframe(filtered_municipal_data)
        
        # Анализ по размеру населенного пункта
        st.markdown("### Анализ по размеру населенного пункта")
        
        # Создаем категории по населению
        def population_category(population):
            if population < 50000:
                return "Малый город (до 50 тыс.)"
            elif population < 100000:
                return "Средний город (50-100 тыс.)"
            elif population < 250000:
                return "Большой город (100-250 тыс.)"
            elif population < 1000000:
                return "Крупный город (250 тыс.-1 млн.)"
            else:
                return "Мегаполис (более 1 млн.)"
        
        filtered_municipal_data['Категория'] = filtered_municipal_data['Население'].apply(population_category)
        
        fig = px.box(filtered_municipal_data, x='Категория', y='Средняя_зарплата',
                    title="Распределение средней зарплаты по размеру населенного пункта")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Нет данных, соответствующих выбранным фильтрам.")

# СберИндекс
elif page == "СберИндекс":
    st.markdown('<h2 class="sub-header">Данные СберИндекс</h2>', unsafe_allow_html=True)
    
    # Фильтры
    st.sidebar.markdown("### Фильтры")
    selected_regions = st.sidebar.multiselect("Выберите регионы:", 
                                             options=sber_index['Регион'].unique(),
                                             default=sber_index['Регион'].unique()[:3])
    
    date_range = st.sidebar.date_input(
        "Выберите период:",
        value=(sber_time_series['Дата'].min().date(), sber_time_series['Дата'].max().date()),
        min_value=sber_time_series['Дата'].min().date(),
        max_value=sber_time_series['Дата'].max().date()
    )
    
    # Фильтрация данных
    filtered_sber_index = sber_index[sber_index['Регион'].isin(selected_regions)]
    
    filtered_time_series = sber_time_series[
        (sber_time_series['Регион'].isin(selected_regions)) &
        (sber_time_series['Дата'] >= pd.Timestamp(date_range[0])) &
        (sber_time_series['Дата'] <= pd.Timestamp(date_range[1]))
    ]
    
    # Показатели
    metric = st.selectbox("Выберите показатель для анализа:", 
                         ["Индекс_потребительской_активности", "Индекс_транзакций_общепит", 
                          "Индекс_транзакций_одежда", "Индекс_транзакций_услуги", "Средний_чек"])
    
    # Визуализация
    st.markdown("### Динамика показателей СберИндекс")
    
    if len(filtered_time_series) > 0:
        fig = px.line(filtered_time_series, x='Дата', y=metric, color='Регион',
                     title=f"Динамика {metric} по регионам")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Сравнение текущих значений
        st.markdown("### Текущие значения показателей")
        
        latest_data = filtered_sber_index.copy()
        fig = px.bar(latest_data, x='Регион', y=metric, color='Регион',
                    title=f"Текущие значения {metric} по регионам")
        st.plotly_chart(fig, use_container_width=True)
        
        # Сезонность
        st.markdown("### Сезонность потребительской активности")
        
        # Группировка по месяцам для анализа сезонности
        filtered_time_series['Месяц'] = filtered_time_series['Дата'].dt.month_name()
        monthly_avg = filtered_time_series.groupby(['Регион', 'Месяц'])['Индекс_потребительской_активности'].mean().reset_index()
        
        # Сортировка месяцев в правильном порядке
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        # Сортировка месяцев в правильном порядке
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        monthly_avg['Месяц'] = pd.Categorical(monthly_avg['Месяц'], categories=month_order, ordered=True)
        monthly_avg = monthly_avg.sort_values('Месяц')
        
        fig = px.line(monthly_avg, x='Месяц', y='Индекс_потребительской_активности', color='Регион',
                     title="Сезонность потребительской активности", markers=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # Таблица с данными
        st.markdown("### Детальные данные")
        st.dataframe(filtered_time_series)
    else:
        st.warning("Нет данных, соответствующих выбранным фильтрам.")

# Сравнительный анализ
elif page == "Сравнительный анализ":
    st.markdown('<h2 class="sub-header">Сравнительный анализ</h2>', unsafe_allow_html=True)
    
    # Выбор типа анализа
    analysis_type = st.radio("Выберите тип анализа:", 
                            ["Сравнение регионов", "Сравнение муниципалитетов", 
                             "Корреляционный анализ"])
    
    if analysis_type == "Сравнение регионов":
        # Фильтры
        st.sidebar.markdown("### Фильтры")
        selected_regions = st.sidebar.multiselect("Выберите регионы для сравнения:", 
                                                options=regional_data['Регион'].unique(),
                                                default=regional_data['Регион'].unique()[:5])
        
        metrics = st.multiselect("Выберите показатели для сравнения:", 
                               ["Население", "Средняя_зарплата", "Инвестиции_млрд", "Индекс_потребления"],
                               default=["Средняя_зарплата", "Индекс_потребления"])
        
        if selected_regions and metrics:
            # Фильтрация данных
            filtered_data = regional_data[regional_data['Регион'].isin(selected_regions)]
            
            # Радарная диаграмма для сравнения регионов
            st.markdown("### Сравнение регионов по выбранным показателям")
            
            # Нормализация данных для радарной диаграммы
            radar_data = filtered_data.copy()
            for metric in metrics:
                max_val = radar_data[metric].max()
                radar_data[f"{metric}_norm"] = radar_data[metric] / max_val * 100
            
            fig = go.Figure()
            
            for _, region in radar_data.iterrows():
                fig.add_trace(go.Scatterpolar(
                    r=[region[f"{metric}_norm"] for metric in metrics],
                    theta=metrics,
                    fill='toself',
                    name=region['Регион']
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=True,
                title="Сравнение регионов (нормализованные значения)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Таблица сравнения
            st.markdown("### Таблица сравнения")
            st.dataframe(filtered_data[['Регион'] + metrics])
            
            # Визуализация отдельных показателей
            st.markdown("### Детальное сравнение по показателям")
            
            for metric in metrics:
                fig = px.bar(filtered_data, x='Регион', y=metric, color='Регион',
                           title=f"Сравнение регионов по показателю: {metric}")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Пожалуйста, выберите регионы и показатели для сравнения.")
    
    elif analysis_type == "Сравнение муниципалитетов":
        # Фильтры
        st.sidebar.markdown("### Фильтры")
        selected_region = st.sidebar.selectbox("Выберите регион:", 
                                             options=sorted(municipal_data['Регион'].unique()))
        
        municipalities_in_region = municipal_data[municipal_data['Регион'] == selected_region]['Муниципалитет'].unique()
        selected_municipalities = st.sidebar.multiselect("Выберите муниципалитеты для сравнения:", 
                                                      options=municipalities_in_region,
                                                      default=municipalities_in_region[:min(5, len(municipalities_in_region))])
        
        metrics = st.multiselect("Выберите показатели для сравнения:", 
                               ["Население", "Средняя_зарплата", "Количество_предприятий", 
                                "Оборот_розничной_торговли_млн", "Индекс_потребления"],
                               default=["Средняя_зарплата", "Индекс_потребления"])
        
        if selected_municipalities and metrics:
            # Фильтрация данных
            filtered_data = municipal_data[municipal_data['Муниципалитет'].isin(selected_municipalities)]
            
            # Визуализация сравнения
            st.markdown("### Сравнение муниципалитетов по выбранным показателям")
            
            for metric in metrics:
                fig = px.bar(filtered_data, x='Муниципалитет', y=metric, color='Муниципалитет',
                           title=f"Сравнение муниципалитетов по показателю: {metric}")
                st.plotly_chart(fig, use_container_width=True)
            
            # Таблица сравнения
            st.markdown("### Таблица сравнения")
            st.dataframe(filtered_data[['Муниципалитет'] + metrics])
            
            # Расчет относительных показателей
            st.markdown("### Относительные показатели")
            
            if "Население" in filtered_data.columns and "Оборот_розничной_торговли_млн" in filtered_data.columns:
                filtered_data['Оборот_на_душу_населения'] = filtered_data['Оборот_розничной_торговли_млн'] * 1000000 / filtered_data['Население']
                
                fig = px.bar(filtered_data, x='Муниципалитет', y='Оборот_на_душу_населения', color='Муниципалитет',
                           title="Оборот розничной торговли на душу населения (руб.)")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Пожалуйста, выберите муниципалитеты и показатели для сравнения.")
    
    elif analysis_type == "Корреляционный анализ":
        # Выбор данных для анализа
        data_source = st.selectbox("Выберите источник данных:", 
                                 ["Региональные данные", "Муниципальные данные"])
    elif analysis_type == "Корреляционный анализ":
        # Выбор данных для анализа
        data_source = st.selectbox("Выберите источник данных:", 
                                 ["Региональные данные", "Муниципальные данные", "СберИндекс"])
        
        if data_source == "Региональные данные":
            data = regional_data
            numeric_cols = ['Население', 'Средняя_зарплата', 'Инвестиции_млрд', 'Индекс_потребления']
        elif data_source == "Муниципальные данные":
            data = municipal_data
            numeric_cols = ['Население', 'Средняя_зарплата', 'Количество_предприятий', 
                           'Оборот_розничной_торговли_млн', 'Индекс_потребления']
        else:  # СберИндекс
            data = sber_index
            numeric_cols = ['Индекс_потребительской_активности', 'Индекс_транзакций_общепит', 
                           'Индекс_транзакций_одежда', 'Индекс_транзакций_услуги', 'Средний_чек']
        
        # Корреляционная матрица
        st.markdown("### Корреляционная матрица")
        
        corr_matrix = data[numeric_cols].corr()
        
        fig = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r',
                       title=f"Корреляция между показателями ({data_source})")
        st.plotly_chart(fig, use_container_width=True)
        
        # Выбор показателей для диаграммы рассеяния
        st.markdown("### Диаграмма рассеяния")
        
        x_metric = st.selectbox("Выберите показатель для оси X:", numeric_cols)
        y_metric = st.selectbox("Выберите показатель для оси Y:", 
                              [col for col in numeric_cols if col != x_metric], 
                              index=min(1, len(numeric_cols)-1))
        
        if data_source == "Региональные данные" or data_source == "СберИндекс":
            color_by = 'Регион'
        else:
            color_by = 'Регион'
        
        fig = px.scatter(data, x=x_metric, y=y_metric, color=color_by,
                        hover_name=data.columns[0],  # Первый столбец (Регион или Муниципалитет)
                        title=f"Зависимость {y_metric} от {x_metric}",
                        trendline="ols")  # Добавляем линию тренда
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Расчет коэффициента корреляции
        correlation = data[x_metric].corr(data[y_metric])
        st.markdown(f"**Коэффициент корреляции Пирсона:** {correlation:.3f}")
        
        if abs(correlation) < 0.3:
            st.markdown("Слабая корреляция между показателями.")
        elif abs(correlation) < 0.7:
            st.markdown("Умеренная корреляция между показателями.")
        else:
            st.markdown("Сильная корреляция между показателями.")

# Готовые отчеты
elif page == "Готовые отчеты":
    st.markdown('<h2 class="sub-header">Готовые отчеты</h2>', unsafe_allow_html=True)
    
    report_type = st.selectbox("Выберите тип отчета:", 
                             ["Топ-10 муниципалитетов по средней зарплате", 
                              "Анализ потребительской активности по регионам",
                              "Инвестиционная привлекательность регионов",
                              "Малые города с высоким потенциалом развития"])
    
    if report_type == "Топ-10 муниципалитетов по средней зарплате":
        st.markdown("### Топ-10 муниципалитетов по средней зарплате")
        
        # Фильтры
        population_threshold = st.slider("Максимальное население (тыс. человек):", 
                                       min_value=10, max_value=1000, value=100, step=10)
        
        # Фильтрация данных
        filtered_data = municipal_data[municipal_data['Население'] <= population_threshold * 1000]
        top_municipalities = filtered_data.sort_values('Средняя_зарплата', ascending=False).head(10)
        
        # Визуализация
        fig = px.bar(top_municipalities, x='Муниципалитет', y='Средняя_зарплата', 
                    color='Регион', text_auto='.2s',
                    title=f"Топ-10 муниципалитетов с населением до {population_threshold} тыс. человек по средней зарплате")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Таблица с данными
        st.markdown("### Детальные данные")
        st.dataframe(top_municipalities[['Муниципалитет', 'Регион', 'Население', 'Средняя_зарплата', 
                                        'Количество_предприятий', 'Оборот_розничной_торговли_млн']])
        
        # Анализ
        st.markdown("### Анализ")
        st.markdown("""
        Анализ показывает, что среди малых и средних городов с населением до 100 тысяч человек 
        наиболее высокие зарплаты наблюдаются в муниципалитетах, расположенных в регионах с развитой 
        промышленностью или добычей полезных ископаемых. Также высокие зарплаты характерны для 
        городов-спутников крупных мегаполисов.
        
        Факторы, влияющие на высокий уровень зарплат в малых городах:
        - Наличие крупных промышленных предприятий
        - Близость к региональным центрам
        - Развитие специализированных отраслей
        - Инвестиционная активность в регионе
        """)
    
    elif report_type == "Анализ потребительской активности по регионам":
        st.markdown("### Анализ потребительской активности по регионам")
        
        # Визуализация динамики потребительской активности
        regions_to_show = sber_index.sort_values('Индекс_потребительской_активности', ascending=False)['Регион'].head(5).tolist()
        
        filtered_time_series = sber_time_series[sber_time_series['Регион'].isin(regions_to_show)]
        
        fig = px.line(filtered_time_series, x='Дата', y='Индекс_потребительской_активности', color='Регион',
                     title="Динамика потребительской активности в топ-5 регионах")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
elif page == "ИИ-Агент":
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    st.title("ИИ-Агент")

    for msg in st.session_state.chat_history:
        st.write(f"👤 {msg}")

    user_input = st.text_input("Введите сообщение", key="chat_input", placeholder="Напишите что-нибудь...")

    if st.button("Отправить"):
        if user_input.strip():
            st.session_state.chat_history.append(user_input)
            st.rerun()  # обновление страницы (если поддерживается)
