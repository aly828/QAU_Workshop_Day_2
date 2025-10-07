import streamlit as st
from datetime import datetime, timedelta
import json

# Maintenance schedules (in days or km)
MAINTENANCE_SCHEDULE = {
    "Oil Change": {"days": 90, "km": 5000, "icon": "🛢️"},
    "Air Filter": {"days": 180, "km": 15000, "icon": "🌬️"},
    "Tire Rotation": {"days": 120, "km": 8000, "icon": "🔄"},
    "Brake Inspection": {"days": 180, "km": 10000, "icon": "🛑"},
    "Battery Check": {"days": 180, "km": None, "icon": "🔋"},
    "Coolant Flush": {"days": 730, "km": 50000, "icon": "❄️"},
    "Transmission Fluid": {"days": 730, "km": 60000, "icon": "⚙️"},
    "Spark Plugs": {"days": 1095, "km": 50000, "icon": "⚡"},
    "Tire Pressure Check": {"days": 7, "km": None, "icon": "🎈"},
    "Wiper Blades": {"days": 180, "km": None, "icon": "🌧️"},
}

def calculate_alert_status(last_service_date, last_service_km, current_km, service_type):
    """Calculate if maintenance is due"""
    schedule = MAINTENANCE_SCHEDULE[service_type]
    alerts = []
    
    # Check days since last service
    if last_service_date:
        days_since = (datetime.now() - last_service_date).days
        days_remaining = schedule["days"] - days_since
        
        if days_remaining <= 0:
            alerts.append(("OVERDUE", f"Overdue by {abs(days_remaining)} days"))
        elif days_remaining <= 7:
            alerts.append(("URGENT", f"Due in {days_remaining} days"))
        elif days_remaining <= 30:
            alerts.append(("WARNING", f"Due in {days_remaining} days"))
        else:
            alerts.append(("OK", f"{days_remaining} days remaining"))
    
    # Check km since last service
    if schedule["km"] and last_service_km is not None and current_km is not None:
        km_since = current_km - last_service_km
        km_remaining = schedule["km"] - km_since
        
        if km_remaining <= 0:
            alerts.append(("OVERDUE", f"Overdue by {abs(km_remaining)} km"))
        elif km_remaining <= 500:
            alerts.append(("URGENT", f"Due in {km_remaining} km"))
        elif km_remaining <= 2000:
            alerts.append(("WARNING", f"Due in {km_remaining} km"))
        else:
            alerts.append(("OK", f"{km_remaining} km remaining"))
    
    # Return the most critical alert
    if any(alert[0] == "OVERDUE" for alert in alerts):
        return "OVERDUE", [a[1] for a in alerts if a[0] == "OVERDUE"]
    elif any(alert[0] == "URGENT" for alert in alerts):
        return "URGENT", [a[1] for a in alerts if a[0] == "URGENT"]
    elif any(alert[0] == "WARNING" for alert in alerts):
        return "WARNING", [a[1] for a in alerts if a[0] == "WARNING"]
    else:
        return "OK", [a[1] for a in alerts]

def get_alert_color(status):
    """Return color based on alert status"""
    colors = {
        "OVERDUE": "🔴",
        "URGENT": "🟠",
        "WARNING": "🟡",
        "OK": "🟢"
    }
    return colors.get(status, "⚪")

# Initialize session state
if 'maintenance_records' not in st.session_state:
    st.session_state.maintenance_records = {}

if 'car_info' not in st.session_state:
    st.session_state.car_info = {
        "make": "",
        "model": "",
        "year": "",
        "current_km": 0
    }

# Main UI
st.title("🚗 Car Maintenance Alert System")
st.write("Track your car maintenance and get timely alerts!")

# Sidebar - Car Information
with st.sidebar:
    st.header("🚙 Car Information")
    st.session_state.car_info["make"] = st.text_input("Make", value=st.session_state.car_info["make"], placeholder="e.g., Toyota")
    st.session_state.car_info["model"] = st.text_input("Model", value=st.session_state.car_info["model"], placeholder="e.g., Camry")
    st.session_state.car_info["year"] = st.text_input("Year", value=st.session_state.car_info["year"], placeholder="e.g., 2020")
    st.session_state.car_info["current_km"] = st.number_input("Current Odometer (km)", min_value=0, value=st.session_state.car_info["current_km"], step=100)
    
    st.divider()
    st.caption("💾 Data is stored in your browser session")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "➕ Add Service", "📋 Service History"])

# Tab 1: Dashboard
with tab1:
    st.header("Maintenance Status")
    
    if not st.session_state.maintenance_records:
        st.info("👋 Welcome! Add your first service record in the 'Add Service' tab to get started.")
    else:
        # Count alerts by status
        overdue = urgent = warning = ok = 0
        
        for service_type in MAINTENANCE_SCHEDULE.keys():
            if service_type in st.session_state.maintenance_records:
                record = st.session_state.maintenance_records[service_type]
                status, _ = calculate_alert_status(
                    record["date"],
                    record["km"],
                    st.session_state.car_info["current_km"],
                    service_type
                )
                if status == "OVERDUE": overdue += 1
                elif status == "URGENT": urgent += 1
                elif status == "WARNING": warning += 1
                else: ok += 1
        
        # Display summary
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🔴 Overdue", overdue)
        col2.metric("🟠 Urgent", urgent)
        col3.metric("🟡 Warning", warning)
        col4.metric("🟢 Good", ok)
        
        st.divider()
        
        # Display all maintenance items
        for service_type, schedule in MAINTENANCE_SCHEDULE.items():
            icon = schedule["icon"]
            
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 2])
                
                with col1:
                    st.write(f"### {icon}")
                
                with col2:
                    st.write(f"**{service_type}**")
                    
                    if service_type in st.session_state.maintenance_records:
                        record = st.session_state.maintenance_records[service_type]
                        status, messages = calculate_alert_status(
                            record["date"],
                            record["km"],
                            st.session_state.car_info["current_km"],
                            service_type
                        )
                        
                        alert_icon = get_alert_color(status)
                        st.write(f"{alert_icon} **{status}**")
                        for msg in messages:
                            st.caption(msg)
                    else:
                        st.write("⚪ No record")
                        st.caption("Add service record")
                
                with col3:
                    if service_type in st.session_state.maintenance_records:
                        record = st.session_state.maintenance_records[service_type]
                        st.caption(f"Last: {record['date'].strftime('%Y-%m-%d')}")
                        if record['km']:
                            st.caption(f"at {record['km']:,} km")
                
                st.divider()

# Tab 2: Add Service
with tab2:
    st.header("Add Service Record")
    
    service_type = st.selectbox("Service Type", list(MAINTENANCE_SCHEDULE.keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        service_date = st.date_input("Service Date", value=datetime.now())
    with col2:
        service_km = st.number_input("Odometer at Service (km)", min_value=0, step=100)
    
    notes = st.text_area("Notes (optional)", placeholder="Any additional details...")
    
    if st.button("💾 Save Service Record", type="primary"):
        st.session_state.maintenance_records[service_type] = {
            "date": datetime.combine(service_date, datetime.min.time()),
            "km": service_km if service_km > 0 else None,
            "notes": notes
        }
        st.success(f"✅ {service_type} record saved!")
        st.rerun()

# Tab 3: Service History
with tab3:
    st.header("Service History")
    
    if not st.session_state.maintenance_records:
        st.info("No service records yet. Add some in the 'Add Service' tab!")
    else:
        for service_type, record in sorted(st.session_state.maintenance_records.items(), 
                                          key=lambda x: x[1]["date"], reverse=True):
            with st.expander(f"{MAINTENANCE_SCHEDULE[service_type]['icon']} {service_type} - {record['date'].strftime('%Y-%m-%d')}"):
                st.write(f"**Date:** {record['date'].strftime('%Y-%m-%d')}")
                if record['km']:
                    st.write(f"**Odometer:** {record['km']:,} km")
                if record['notes']:
                    st.write(f"**Notes:** {record['notes']}")
                
                if st.button(f"🗑️ Delete", key=f"del_{service_type}"):
                    del st.session_state.maintenance_records[service_type]
                    st.rerun()

# Footer
st.markdown("---")
st.caption("🔔 Check this dashboard regularly to stay on top of your car maintenance!")