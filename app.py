"""
Mental Health in Tech Industry - Interactive Dashboard
A Streamlit application for exploring mental health survey data
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Mental Health in Tech Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #444;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


# Data loading and caching
@st.cache_data
def load_data():
    """Load and preprocess the mental health survey data"""
    df = pd.read_csv('survey.csv')

    # Data cleaning
    # Remove age outliers
    df = df[(df['Age'] > 16) & (df['Age'] < 100)].copy()

    # Standardize gender
    df['Gender'] = df['Gender'].str.lower().str.strip()
    gender_map = {
        'male': 'Male', 'm': 'Male', 'man': 'Male', 'cis male': 'Male',
        'male-ish': 'Male', 'maile': 'Male', 'mal': 'Male', 'male (cis)': 'Male',
        'make': 'Male', 'male ': 'Male', 'msle': 'Male', 'mail': 'Male',
        'malr': 'Male', 'cis man': 'Male',
        'female': 'Female', 'f': 'Female', 'woman': 'Female', 'cis female': 'Female',
        'femake': 'Female', 'female ': 'Female', 'cis-female/femme': 'Female',
        'female (cis)': 'Female', 'femail': 'Female',
        'trans-female': 'Trans', 'trans woman': 'Trans', 'female (trans)': 'Trans',
        'non-binary': 'Non-binary', 'genderqueer': 'Non-binary', 'fluid': 'Non-binary',
        'queer': 'Non-binary', 'androgyne': 'Non-binary', 'agender': 'Non-binary',
        'genderfluid': 'Non-binary', 'enby': 'Non-binary'
    }
    df['Gender'] = df['Gender'].map(gender_map).fillna('Other')

    # Handle missing values
    df['state'].fillna('Not Applicable', inplace=True)
    df['work_interfere'].fillna('Not Applicable', inplace=True)
    df['self_employed'].fillna('No', inplace=True)

    # Create age groups
    df['Age_Group'] = pd.cut(df['Age'],
                             bins=[0, 25, 35, 45, 55, 100],
                             labels=['18-25', '26-35', '36-45', '46-55', '56+'])

    # Convert timestamp
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    return df


# Load data
try:
    df = load_data()
    data_loaded = True
except Exception as e:
    data_loaded = False
    st.error(f"Error loading data: {e}")
    st.info("Please ensure 'survey__1_.csv' is in the same directory as this script.")

# App Header
st.markdown('<h1 class="main-header">🧠 Mental Health in Tech Industry Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Interactive Analysis of Mental Health Survey Data from 1,259 Tech Workers</p>',
            unsafe_allow_html=True)

if data_loaded:
    # Sidebar filters
    st.sidebar.header("🔍 Filters")

    # Gender filter
    gender_options = ['All'] + sorted(df['Gender'].unique().tolist())
    selected_gender = st.sidebar.multiselect(
        'Select Gender',
        options=gender_options,
        default=['All']
    )

    # Age filter
    age_range = st.sidebar.slider(
        'Age Range',
        min_value=int(df['Age'].min()),
        max_value=int(df['Age'].max()),
        value=(int(df['Age'].min()), int(df['Age'].max()))
    )

    # Country filter
    country_options = ['All'] + sorted(df['Country'].unique().tolist())
    selected_countries = st.sidebar.multiselect(
        'Select Country',
        options=country_options,
        default=['All']
    )

    # Treatment filter
    treatment_filter = st.sidebar.radio(
        'Treatment Status',
        options=['All', 'Yes', 'No']
    )

    # Apply filters
    filtered_df = df.copy()

    if 'All' not in selected_gender:
        filtered_df = filtered_df[filtered_df['Gender'].isin(selected_gender)]

    filtered_df = filtered_df[(filtered_df['Age'] >= age_range[0]) & (filtered_df['Age'] <= age_range[1])]

    if 'All' not in selected_countries:
        filtered_df = filtered_df[filtered_df['Country'].isin(selected_countries)]

    if treatment_filter != 'All':
        filtered_df = filtered_df[filtered_df['treatment'] == treatment_filter]

    # Key Metrics
    st.header("📊 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Respondents", f"{len(filtered_df):,}")

    with col2:
        treatment_pct = (filtered_df['treatment'].value_counts().get('Yes', 0) / len(filtered_df) * 100)
        st.metric("Seeking Treatment", f"{treatment_pct:.1f}%")

    with col3:
        avg_age = filtered_df['Age'].mean()
        st.metric("Average Age", f"{avg_age:.1f}")

    with col4:
        family_history_pct = (filtered_df['family_history'].value_counts().get('Yes', 0) / len(filtered_df) * 100)
        st.metric("Family History", f"{family_history_pct:.1f}%")

    with col5:
        countries = filtered_df['Country'].nunique()
        st.metric("Countries", f"{countries}")

    st.markdown("---")

    # Create tabs for different analysis sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview",
        "👥 Demographics",
        "🏢 Workplace Analysis",
        "💡 Treatment Insights",
        "🌍 Geographic Analysis"
    ])

    # TAB 1: OVERVIEW
    with tab1:
        st.header("Overview Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Treatment Distribution
            st.subheader("Treatment Status Distribution")
            treatment_counts = filtered_df['treatment'].value_counts()
            fig = go.Figure(data=[go.Pie(
                labels=treatment_counts.index,
                values=treatment_counts.values,
                hole=0.4,
                marker=dict(colors=['#ef553b', '#00cc96']),
                textinfo='label+percent',
                textfont_size=14
            )])
            fig.update_layout(
                title_text="Seeking Mental Health Treatment",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("""
            <div class="insight-box">
            <b>💡 Insight:</b> Nearly half of tech workers are seeking mental health treatment, 
            indicating high prevalence of mental health concerns in the industry.
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Family History
            st.subheader("Family History of Mental Illness")
            family_counts = filtered_df['family_history'].value_counts()
            fig = go.Figure(data=[go.Bar(
                x=family_counts.index,
                y=family_counts.values,
                marker=dict(color=['#3498db', '#e67e22']),
                text=family_counts.values,
                textposition='auto'
            )])
            fig.update_layout(
                xaxis_title="Family History",
                yaxis_title="Count",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("""
            <div class="insight-box">
            <b>💡 Insight:</b> Significant portion have family history, highlighting 
            the genetic component and need for early screening programs.
            </div>
            """, unsafe_allow_html=True)

        # Work Interference
        st.subheader("How Often Does Mental Health Interfere with Work?")
        work_counts = filtered_df['work_interfere'].value_counts()
        order = ['Never', 'Rarely', 'Sometimes', 'Often', 'Not Applicable']
        work_ordered = work_counts.reindex([x for x in order if x in work_counts.index], fill_value=0)

        fig = go.Figure(data=[go.Bar(
            x=work_ordered.index,
            y=work_ordered.values,
            marker=dict(color=['#27ae60', '#f39c12', '#e67e22', '#e74c3c', '#95a5a6']),
            text=work_ordered.values,
            textposition='auto'
        )])
        fig.update_layout(
            xaxis_title="Frequency of Interference",
            yaxis_title="Number of Respondents",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div class="insight-box">
        <b>💡 Insight:</b> Mental health regularly interferes with work for many employees, 
        directly impacting productivity and justifying investment in support programs.
        </div>
        """, unsafe_allow_html=True)

    # TAB 2: DEMOGRAPHICS
    with tab2:
        st.header("Demographic Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Age Distribution
            st.subheader("Age Distribution")
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=filtered_df['Age'],
                nbinsx=30,
                marker=dict(color='steelblue', line=dict(color='black', width=1)),
                name='Age Distribution'
            ))
            fig.add_vline(
                x=filtered_df['Age'].mean(),
                line_dash="dash",
                line_color="red",
                annotation_text=f"Mean: {filtered_df['Age'].mean():.1f}"
            )
            fig.update_layout(
                xaxis_title="Age",
                yaxis_title="Frequency",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Gender Distribution
            st.subheader("Gender Distribution")
            gender_counts = filtered_df['Gender'].value_counts()
            fig = go.Figure(data=[go.Bar(
                x=gender_counts.index,
                y=gender_counts.values,
                marker=dict(color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12']),
                text=gender_counts.values,
                textposition='auto'
            )])
            fig.update_layout(
                xaxis_title="Gender",
                yaxis_title="Count",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        # Age Group Analysis
        st.subheader("Treatment by Age Group")
        age_treatment = pd.crosstab(filtered_df['Age_Group'], filtered_df['treatment'], normalize='index') * 100

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='No Treatment',
            x=age_treatment.index,
            y=age_treatment['No'],
            marker=dict(color='#ef553b')
        ))
        fig.add_trace(go.Bar(
            name='Seeking Treatment',
            x=age_treatment.index,
            y=age_treatment['Yes'],
            marker=dict(color='#00cc96')
        ))
        fig.update_layout(
            barmode='stack',
            xaxis_title="Age Group",
            yaxis_title="Percentage (%)",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Gender vs Treatment
        st.subheader("Treatment Seeking by Gender")
        gender_treatment = pd.crosstab(filtered_df['Gender'], filtered_df['treatment'], normalize='index') * 100

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='No Treatment',
            x=gender_treatment.index,
            y=gender_treatment['No'],
            marker=dict(color='#ef553b')
        ))
        fig.add_trace(go.Bar(
            name='Seeking Treatment',
            x=gender_treatment.index,
            y=gender_treatment['Yes'],
            marker=dict(color='#00cc96')
        ))
        fig.update_layout(
            barmode='group',
            xaxis_title="Gender",
            yaxis_title="Percentage (%)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div class="insight-box">
        <b>💡 Insight:</b> Gender differences in treatment-seeking behavior suggest need 
        for targeted outreach programs, especially for underrepresented groups.
        </div>
        """, unsafe_allow_html=True)

    # TAB 3: WORKPLACE ANALYSIS
    with tab3:
        st.header("Workplace Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Company Size vs Treatment
            st.subheader("Treatment by Company Size")
            size_treatment = pd.crosstab(filtered_df['no_employees'], filtered_df['treatment'], normalize='index') * 100

            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='No Treatment',
                x=size_treatment.index,
                y=size_treatment['No'],
                marker=dict(color='#ef553b')
            ))
            fig.add_trace(go.Bar(
                name='Seeking Treatment',
                x=size_treatment.index,
                y=size_treatment['Yes'],
                marker=dict(color='#00cc96')
            ))
            fig.update_layout(
                barmode='stack',
                xaxis_title="Company Size (Employees)",
                yaxis_title="Percentage (%)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Tech vs Non-Tech
            st.subheader("Tech vs Non-Tech Companies")
            tech_treatment = pd.crosstab(filtered_df['tech_company'], filtered_df['treatment'], normalize='index') * 100

            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='No Treatment',
                x=tech_treatment.index,
                y=tech_treatment['No'],
                marker=dict(color='#ef553b')
            ))
            fig.add_trace(go.Bar(
                name='Seeking Treatment',
                x=tech_treatment.index,
                y=tech_treatment['Yes'],
                marker=dict(color='#00cc96')
            ))
            fig.update_layout(
                barmode='group',
                xaxis_title="Tech Company",
                yaxis_title="Percentage (%)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        # Remote Work Analysis
        st.subheader("Remote Work vs Treatment")
        remote_treatment = pd.crosstab(filtered_df['remote_work'], filtered_df['treatment'])

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='No Treatment',
            x=remote_treatment.index,
            y=remote_treatment['No'],
            marker=dict(color='#ef553b'),
            text=remote_treatment['No'],
            textposition='auto'
        ))
        fig.add_trace(go.Bar(
            name='Seeking Treatment',
            x=remote_treatment.index,
            y=remote_treatment['Yes'],
            marker=dict(color='#00cc96'),
            text=remote_treatment['Yes'],
            textposition='auto'
        ))
        fig.update_layout(
            barmode='group',
            xaxis_title="Remote Work",
            yaxis_title="Count",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        # Benefits Analysis
        st.subheader("Mental Health Benefits Availability")
        benefits_counts = filtered_df['benefits'].value_counts()

        fig = go.Figure(data=[go.Pie(
            labels=benefits_counts.index,
            values=benefits_counts.values,
            hole=0.3,
            marker=dict(colors=['#00cc96', '#ef553b', '#ffa15a'])
        )])
        fig.update_layout(
            title_text="Do Employers Provide Mental Health Benefits?",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div class="insight-box">
        <b>💡 Insight:</b> Company size and benefits availability significantly impact 
        mental health treatment access. Larger companies typically offer better support.
        </div>
        """, unsafe_allow_html=True)

    # TAB 4: TREATMENT INSIGHTS
    with tab4:
        st.header("Treatment Insights")

        # Family History vs Treatment
        st.subheader("Impact of Family History on Treatment Seeking")
        fam_treatment = pd.crosstab(filtered_df['family_history'], filtered_df['treatment'], normalize='index') * 100

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='No Treatment',
            x=fam_treatment.index,
            y=fam_treatment['No'],
            marker=dict(color='#ef553b'),
            text=[f"{v:.1f}%" for v in fam_treatment['No']],
            textposition='auto'
        ))
        fig.add_trace(go.Bar(
            name='Seeking Treatment',
            x=fam_treatment.index,
            y=fam_treatment['Yes'],
            marker=dict(color='#00cc96'),
            text=[f"{v:.1f}%" for v in fam_treatment['Yes']],
            textposition='auto'
        ))
        fig.update_layout(
            barmode='group',
            xaxis_title="Family History of Mental Illness",
            yaxis_title="Percentage (%)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            # Mental Health Consequences
            st.subheader("Fear of Consequences")
            consequence_counts = filtered_df['mental_health_consequence'].value_counts()

            fig = go.Figure(data=[go.Pie(
                labels=consequence_counts.index,
                values=consequence_counts.values,
                hole=0.4
            )])
            fig.update_layout(
                title_text="Discussing Mental Health with Employer",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Mental vs Physical Health
            st.subheader("Equality of Treatment")
            mental_vs_phys = filtered_df['mental_vs_physical'].value_counts()

            fig = go.Figure(data=[go.Bar(
                x=mental_vs_phys.index,
                y=mental_vs_phys.values,
                marker=dict(color=['#ef553b', '#ffa15a', '#00cc96']),
                text=mental_vs_phys.values,
                textposition='auto'
            )])
            fig.update_layout(
                xaxis_title="Employer Takes Mental Health as Seriously as Physical",
                yaxis_title="Count",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        # Comfort discussing with coworkers vs supervisor
        st.subheader("Comfort Level in Discussing Mental Health")

        col1, col2 = st.columns(2)

        with col1:
            coworker_counts = filtered_df['coworkers'].value_counts()
            fig = go.Figure(data=[go.Bar(
                x=coworker_counts.index,
                y=coworker_counts.values,
                marker=dict(color='skyblue'),
                text=coworker_counts.values,
                textposition='auto'
            )])
            fig.update_layout(
                title_text="With Coworkers",
                xaxis_title="Willingness",
                yaxis_title="Count",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            supervisor_counts = filtered_df['supervisor'].value_counts()
            fig = go.Figure(data=[go.Bar(
                x=supervisor_counts.index,
                y=supervisor_counts.values,
                marker=dict(color='coral'),
                text=supervisor_counts.values,
                textposition='auto'
            )])
            fig.update_layout(
                title_text="With Supervisor",
                xaxis_title="Willingness",
                yaxis_title="Count",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div class="insight-box">
        <b>💡 Insight:</b> Strong correlation between family history and treatment. 
        Employees are generally more comfortable discussing with coworkers than supervisors.
        </div>
        """, unsafe_allow_html=True)

    # TAB 5: GEOGRAPHIC ANALYSIS
    with tab5:
        st.header("Geographic Analysis")

        # Top countries
        st.subheader("Respondents by Country (Top 15)")
        top_countries = filtered_df['Country'].value_counts().head(15)

        fig = go.Figure(data=[go.Bar(
            x=top_countries.values,
            y=top_countries.index,
            orientation='h',
            marker=dict(color='steelblue'),
            text=top_countries.values,
            textposition='auto'
        )])
        fig.update_layout(
            xaxis_title="Number of Respondents",
            yaxis_title="Country",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

        # Treatment by top countries
        st.subheader("Treatment Rates by Country (Top 10)")
        top_10_countries = filtered_df['Country'].value_counts().head(10).index
        df_top = filtered_df[filtered_df['Country'].isin(top_10_countries)]
        country_treatment = pd.crosstab(df_top['Country'], df_top['treatment'], normalize='index') * 100
        country_treatment = country_treatment.sort_values('Yes', ascending=True)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='No Treatment',
            y=country_treatment.index,
            x=country_treatment['No'],
            orientation='h',
            marker=dict(color='#ef553b')
        ))
        fig.add_trace(go.Bar(
            name='Seeking Treatment',
            y=country_treatment.index,
            x=country_treatment['Yes'],
            orientation='h',
            marker=dict(color='#00cc96')
        ))
        fig.update_layout(
            barmode='stack',
            xaxis_title="Percentage (%)",
            yaxis_title="Country",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div class="insight-box">
        <b>💡 Insight:</b> Geographic variations in treatment rates reflect cultural 
        differences in mental health awareness and healthcare system accessibility.
        </div>
        """, unsafe_allow_html=True)

    # Footer with data summary
    st.markdown("---")
    st.header("📋 Data Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Treatment Statistics")
        treatment_summary = filtered_df['treatment'].value_counts()
        for status, count in treatment_summary.items():
            pct = (count / len(filtered_df)) * 100
            st.write(f"**{status}:** {count} ({pct:.1f}%)")

    with col2:
        st.subheader("Top 5 Countries")
        top_5 = filtered_df['Country'].value_counts().head(5)
        for country, count in top_5.items():
            st.write(f"**{country}:** {count}")

    with col3:
        st.subheader("Age Statistics")
        st.write(f"**Mean Age:** {filtered_df['Age'].mean():.1f} years")
        st.write(f"**Median Age:** {filtered_df['Age'].median():.1f} years")
        st.write(f"**Std Dev:** {filtered_df['Age'].std():.1f} years")
        st.write(f"**Range:** {filtered_df['Age'].min():.0f} - {filtered_df['Age'].max():.0f} years")

    # Download filtered data
    st.markdown("---")
    st.subheader("📥 Download Filtered Data")

    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="filtered_mental_health_data.csv",
        mime="text/csv"
    )

else:
    st.warning("⚠️ Please upload the data file to proceed.")
    st.info("""
    **Instructions:**
    1. Ensure 'survey__1_.csv' is in the same directory as this script
    2. Restart the Streamlit app
    3. The dashboard will automatically load the data
    """)

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.info("""
**About this Dashboard**

This interactive dashboard provides comprehensive analysis of mental health 
in the tech industry based on survey data from 1,259 respondents across 48 countries.

**Features:**
- Interactive filtering
- Multiple visualization types
- Demographic analysis
- Workplace insights
- Geographic patterns
- Treatment analysis

**Data Source:** Mental Health in Tech Survey
""")