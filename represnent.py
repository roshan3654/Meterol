import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from io import BytesIO
import calendar
import random

# Page Configuration
st.set_page_config(
    page_title="Food Flow Tracker",
    page_icon="🍽️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
:root {
    --primary: #4361ee;
    --secondary: #3f37c9;
    --success: #4cc9f0;
    --danger: #f72585;
    --light: #f8f9fa;
    --dark: #212529;
}

.header {
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: white;
    padding: 2rem;
    border-radius: 0 0 10px 10px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    border-left: 4px solid var(--primary);
}

.metric-card {
    background: white;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.metric-value {
    font-size: 2rem;
    font-weight: bold;
    color: var(--primary);
}

.metric-label {
    font-size: 0.9rem;
    color: var(--dark);
    opacity: 0.8;
}

.stButton>button {
    background-color: var(--primary);
    color: white;
    border-radius: 8px;
    border: none;
    padding: 0.5rem 1rem;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background-color: var(--secondary);
    transform: translateY(-2px);
}

.date-picker {
    background: white;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.food-table {
    width: 100%;
    border-collapse: collapse;
}

.food-table th {
    background-color: var(--light);
    text-align: left;
    padding: 0.75rem;
}

.food-table td {
    padding: 0.75rem;
    border-bottom: 1px solid #eee;
}

.positive {
    color: var(--success);
}

.negative {
    color: var(--danger);
}
</style>
""", unsafe_allow_html=True)

# Function to create new sample data every time
def create_sample_data():
    num_days = 7
    sample_dates = [datetime.today().date() - timedelta(days=i) for i in range(num_days)]
    sample_items = ['Rice', 'Chicken', 'Vegetables', 'Bread', 'Milk', 'Eggs', 'Fruits', 'Pasta', 'Beef', 'Salad']
    sample_categories = ['Grains', 'Protein', 'Vegetables', 'Grains', 'Dairy', 'Protein', 'Fruits', 'Grains', 'Protein', 'Vegetables']
    units = ['kg', 'kg', 'kg', 'loaf', 'L', 'dozen', 'kg', 'kg', 'kg', 'kg']

    data = []
    for date in sample_dates:
        for i in range(random.randint(5, 10)):  # Generate a random number of items per day
            item = random.choice(sample_items)
            category = sample_categories[sample_items.index(item)]
            unit = units[sample_items.index(item)]
            prepared = round(random.uniform(1, 5), 1)
            consumed = round(random.uniform(0, prepared), 1)
            wasted = round(prepared - consumed, 2)
            data.append({
                'date': date,
                'item_name': item,
                'category': category,
                'prepared_qty': prepared,
                'consumed_qty': consumed,
                'wasted_qty': wasted,
                'unit': unit
            })
    return pd.DataFrame(data)

# Initialize Session State
if 'food_data' not in st.session_state:
    st.session_state.food_data = create_sample_data()

# Helper Functions
def calculate_daily_summary(df, date):
    daily = df[df['date'] == pd.to_datetime(date).date()]
    if daily.empty:
        return None
    return {
        'total_prepared': daily['prepared_qty'].sum(),
        'total_consumed': daily['consumed_qty'].sum(),
        'total_wasted': daily['wasted_qty'].sum(),
        'utilization_rate': (daily['consumed_qty'].sum() / daily['prepared_qty'].sum() * 100) if daily['prepared_qty'].sum() else 0,
        'waste_percentage': (daily['wasted_qty'].sum() / daily['prepared_qty'].sum() * 100) if daily['prepared_qty'].sum() else 0
    }

# Main App
def main():
    st.markdown("<div class='header'><h1>🍽️ Food Flow Tracker</h1><p>Monitor preparation vs consumption to reduce waste</p></div>", unsafe_allow_html=True)

    # Date and View Mode Selection
    col1, col2 = st.columns(2)
    with col1:
        today = datetime.today().date()
        selected_date = st.date_input("Select Date", today)
    with col2:
        view_mode = st.selectbox("View Mode", ["Daily", "Weekly", "Monthly"])

    # Data Entry Form
    with st.expander("➕ Add Food Item", expanded=False):
        with st.form("food_form"):
            cols = st.columns([2, 1, 1, 1, 1, 1])
            with cols[0]:
                item_name = st.text_input("Item Name")
            with cols[1]:
                category = st.selectbox("Category", ["Grains", "Protein", "Vegetables", "Fruits", "Dairy", "Other"])
            with cols[2]:
                prepared_qty = st.number_input("Prepared (Qty)", min_value=0.0, step=0.1, value=1.0)
            with cols[3]:
                consumed_qty = st.number_input("Consumed (Qty)", min_value=0.0, step=0.1, value=0.8)
            with cols[4]:
                wasted_qty = st.number_input("Wasted (Qty)", min_value=0.0, step=0.01, value=0.05)
            with cols[5]:
                unit = st.selectbox("Unit", ["kg", "g", "L", "ml", "piece", "dozen", "loaf", "other"])

            submitted = st.form_submit_button("Add Item")
            if submitted and item_name:
                new_entry = pd.DataFrame([{
                    'date': selected_date,
                    'item_name': item_name,
                    'category': category,
                    'prepared_qty': prepared_qty,
                    'consumed_qty': consumed_qty,
                    'wasted_qty': wasted_qty,
                    'unit': unit
                }])
                st.session_state.food_data = pd.concat([st.session_state.food_data, new_entry], ignore_index=True)
                st.success("Item added successfully!")
            elif submitted:
                st.warning("Please enter an item name")

    # Metrics Dashboard
    st.markdown("## 📊 Food Flow Metrics")
    if view_mode == "Daily":
        summary = calculate_daily_summary(st.session_state.food_data, selected_date)
        if summary:
            cols = st.columns(4)
            with cols[0]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{summary['total_prepared']:.1f}</div>
                    <div class="metric-label">Prepared</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{summary['total_consumed']:.1f}</div>
                    <div class="metric-label">Consumed</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value {'negative' if summary['waste_percentage'] > 5 else 'positive'}">{summary['waste_percentage']:.1f}%</div>
                    <div class="metric-label">Waste %</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[3]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value {'positive' if summary['utilization_rate'] > 85 else 'negative'}">{summary['utilization_rate']:.1f}%</div>
                    <div class="metric-label">Utilization</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No data available for selected date")

    # Data Visualization
    st.markdown("## 📈 Visualization")
    tab1, tab2, tab3 = st.tabs(["Daily Flow", "Category Analysis", "Trends"])

    with tab1:
        if view_mode == "Daily":
            daily_data = st.session_state.food_data[
                st.session_state.food_data['date'] == pd.to_datetime(selected_date).date()
            ]
            if not daily_data.empty:
                fig = px.bar(daily_data,
                             x='item_name',
                             y=['prepared_qty', 'consumed_qty', 'wasted_qty'],
                             title=f"Food Flow on {selected_date.strftime('%B %d, %Y')}",
                             labels={'value': 'Quantity', 'variable': 'Type', 'item_name': 'Food Item'},
                             barmode='group')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available for selected date")

    with tab2:
        category_data = st.session_state.food_data.groupby('category').agg({
            'prepared_qty': 'sum',
            'consumed_qty': 'sum',
            'wasted_qty': 'sum'
        }).reset_index()

        fig = px.pie(category_data,
                     values='prepared_qty',
                     names='category',
                     title='Food Preparation by Category',
                     hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.bar(category_data,
                      x='category',
                      y=['consumed_qty', 'wasted_qty'],
                      title='Consumption vs Waste by Category',
                      barmode='group')
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        trend_data = st.session_state.food_data.copy()
        trend_data['date'] = pd.to_datetime(trend_data['date'])
        trend_data = trend_data.groupby('date').agg({
            'prepared_qty': 'sum',
            'consumed_qty': 'sum',
            'wasted_qty': 'sum'
        }).reset_index()

        trend_data['utilization_rate'] = (trend_data['consumed_qty'] / trend_data['prepared_qty'] * 100) if trend_data['prepared_qty'].sum() else 0
        trend_data['waste_percentage'] = (trend_data['wasted_qty'] / trend_data['prepared_qty'] * 100) if trend_data['prepared_qty'].sum() else 0

        fig = px.line(trend_data,
                      x='date',
                      y=['prepared_qty', 'consumed_qty'],
                      title='Daily Food Preparation vs Consumption',
                      labels={'value': 'Quantity', 'variable': 'Type'})
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.line(trend_data,
                       x='date',
                       y=['util.inoization_rate', 'waste_percentage'],
                       title='Utilization Rate & Waste Percentage Trend',
                       labels={'value': 'Percentage (%)', 'variable': 'Metric'})
        st.plotly_chart(fig2, use_container_width=True)

    # Data Table
    st.markdown("## 📝 Detailed Records")
    # Load new sample data every time the app runs to update the detailed records
    st.session_state.food_data = create_sample_data()
    display_data = st.session_state.food_data.copy()
    display_data['date'] = display_data['date'].astype(str)
    st.dataframe(display_data, hide_index=True, use_container_width=True)

    # Data Export
    st.markdown("## 💾 Export Data")
    col1, col2 = st.columns(2)
    with col1:
        csv = st.session_state.food_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="food_flow_data.csv",
            mime="text/csv"
        )
    with col2:
        excel = BytesIO()
        with pd.ExcelWriter(excel, engine='xlsxwriter') as writer:
            st.session_state.food_data.to_excel(writer, index=False)
        excel.seek(0)
        st.download_button(
            label="Download Excel",
            data=excel.getvalue(),
            file_name="food_flow_data.xlsx",
            mime="application/vnd.ms-excel"
        )

if __name__ == "__main__":
    main()
