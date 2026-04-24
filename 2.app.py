import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import plotly.express as px

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('ems_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employees
                 (emp_id TEXT PRIMARY KEY, name TEXT, dept TEXT, 
                  role TEXT, salary REAL, join_date TEXT)''')
    conn.commit()
    conn.close()

def add_data(id, name, dept, role, sal, date):
    conn = sqlite3.connect('ems_data.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO employees VALUES (?,?,?,?,?,?)", (id, name, dept, role, sal, date))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def view_all_data():
    conn = sqlite3.connect('ems_data.db')
    df = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()
    return df

def delete_data(id):
    conn = sqlite3.connect('ems_data.db')
    c = conn.cursor()
    c.execute('DELETE FROM employees WHERE emp_id=?', (id,))
    conn.commit()
    conn.close()

# --- UI CONFIG ---
st.set_page_config(page_title="StaffCore EMS", layout="wide", page_icon="👥")
init_db()

# --- THEME CUSTOMIZATION ---
def apply_custom_theme():
    st.markdown(
        """
        <style>
        /* 1. Main Background Overlay */
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                        url("https://images.unsplash.com/photo-1497215728101-856f4ea42174?q=80&w=2070&auto=format&fit=crop");
            background-size: cover;
            background-attachment: fixed;
        }

        /* 2. SIDEBAR RED GRADIENT */
        [data-testid="stSidebar"] {
            background: linear-gradient(#8B0000, #4B0000) !important;
            border-right: 2px solid #FF0000;
        }
        
        /* 3. NAVIGATION & LABELS - FULL BLACK */
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
            background-color: #000000 !important;
            color: white !important;
        }
        
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1 {
            color: #000000 !important; 
            font-weight: 900 !important;
        }

        /* 4. Metric Styling */
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.05);
            border-left: 5px solid #8B0000;
            padding: 15px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }

        /* Global White Text for main area */
        h1, h2, h3, span, .stMarkdown p {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_theme()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🏢 StaffCore EMS")
menu = ["Dashboard", "Add Employee", "Search & Manage"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- 1. DASHBOARD ---
if choice == "Dashboard":
    st.title("📊 HR Command Center")
    df = view_all_data()
    
    if not df.empty:
        # Metrics Row
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Staff", len(df))
        col2.metric("Monthly Payroll", f"Rs. {df['salary'].sum():,.0f}")
        col3.metric("Departments", len(df['dept'].unique()))
        
        st.divider()

        # MULTI-COLOR CHART SECTION
        st.subheader("Department-wise Salary Distribution")
        dept_sal = df.groupby('dept')['salary'].sum().reset_index()
        
        # Using a Red-to-White gradient for a professional "Multi-Color" result
        fig = px.bar(
            dept_sal, 
            x='dept', 
            y='salary', 
            color='salary', 
            color_continuous_scale=['#8B0000', '#FFFFFF'],
            labels={'salary': 'Total PKR', 'dept': 'Department'}
        ) 
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            coloraxis_showscale=False, # Keeps the dashboard clean
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#333')
        )
        fig.update_traces(marker_line_color='white', marker_line_width=1)
        
        st.plotly_chart(fig, use_container_width=True)
            
        st.subheader("Employee Directory")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("The database is currently empty. Please register new staff.")

# --- 2. ADD EMPLOYEE ---
elif choice == "Add Employee":
    st.title("📝 Staff Registration")
    with st.form("Add Form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            emp_id = st.text_input("Employee ID").upper().strip()
            name = st.text_input("Full Name").strip()
            dept = st.selectbox("Department", ["IT", "HR", "Finance", "Sales", "Operations"])
        with col2:
            role = st.text_input("Designation").strip()
            salary = st.number_input("Monthly Salary (PKR)", min_value=0, step=5000)
            join_date = st.date_input("Joining Date", date.today())
            
        if st.form_submit_button("✅ Register Employee"):
            if emp_id and name:
                if add_data(emp_id, name, dept, role, salary, str(join_date)):
                    st.success(f"Record for {name} saved successfully!")
                    st.balloons()
                else:
                    st.error("Employee ID already exists!")
            else:
                st.warning("Please fill required fields (ID & Name)")

# --- 3. SEARCH & MANAGE ---
elif choice == "Search & Manage":
    st.title("🔍 Record Management")
    df = view_all_data()
    if not df.empty:
        search_term = st.text_input("Search Employee by Name")
        if search_term:
            filtered_df = df[df['name'].str.contains(search_term, case=False)]
            st.dataframe(filtered_df, use_container_width=True)
        
        st.divider()
        st.subheader("🗑️ Remove Employee")
        delete_id = st.selectbox("Select Employee ID to Delete", df['emp_id'].unique())
        if st.button("❌ Permanent Delete"):
            delete_data(delete_id)
            st.rerun()
    else:
        st.info("No records to manage.")

st.sidebar.markdown("---")
st.sidebar.caption("Enterprise Edition v1.0 | 2026")