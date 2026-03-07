import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

if "complaints" not in st.session_state:
    st.session_state.complaints = []

def classify_complaint(text):

    text = text.lower()

    if "garbage" in text or "trash" in text:
        return {
            "Category": "Sanitation",
            "Department": "Waste Management",
            "Urgency": "High"
        }

    elif "streetlight" in text or "light" in text:
        return {
            "Category": "Infrastructure",
            "Department": "Electrical Department",
            "Urgency": "Medium"
        }

    elif "water" in text or "leak" in text:
        return {
            "Category": "Water Supply",
            "Department": "Water Department",
            "Urgency": "High"
        }

    elif "traffic" in text or "signal" in text:
        return {
            "Category": "Traffic",
            "Department": "Traffic Department",
            "Urgency": "Medium"
        }

    else:
        return {
            "Category": "General Complaint",
            "Department": "City Services",
            "Urgency": "Low"
        }
  

st.title("City Complaint AI Analyzer")

st.header("Submit a Complaint")

complaint = st.text_area("Describe your issue")

location = st.text_input("Location")

if st.button("Submit Complaint"):

    # Check if complaint box is empty
    if complaint.strip() == "":
        st.error("Please enter a complaint.")

    else:
        # Run the AI classification
        result = classify_complaint(complaint)

        # Show success message
        st.success("Complaint analyzed!")

        # Show what user entered
        st.write("Complaint:", complaint)
        st.write("Location:", location)

        # Show AI results
        st.subheader("AI Analysis")

        st.write("Category:", result["Category"])
        st.write("Department:", result["Department"])
        st.write("Urgency:", result["Urgency"])

        # Save complaint into storage
        st.session_state.complaints.append({
            "complaint": complaint,
            "location": location,
            "category": result["Category"],
            "department": result["Department"],
            "urgency": result["Urgency"]
        })
st.header("Complaint Dashboard")

if len(st.session_state.complaints) > 0:

    df = pd.DataFrame(st.session_state.complaints)

    st.dataframe(df.rename(columns={
    "complaint": "Complaint",
    "location": "Location",
    "category": "Category",
    "department": "Department",
    "urgency": "Urgency"
}))

else:
    st.write("No complaints submitted yet.")

if len(st.session_state.complaints) > 0:

    df = pd.DataFrame(st.session_state.complaints)

    high = len(df[df["urgency"] == "High"])
    medium = len(df[df["urgency"] == "Medium"])
    low = len(df[df["urgency"] == "Low"])

    st.subheader("Complaint Summary")

    st.write("🔴 High Urgency Complaints:", high)
    st.write("🟠 Medium Urgency Complaints:", medium)
    st.write("🟢 Low Urgency Complaints:", low)

else:
    st.write("No complaints submitted yet.")

st.subheader("Complaint Summary")


m = folium.Map(location=[32.37, -86.30], zoom_start=12)

for c in st.session_state.complaints:

    if c["urgency"] == "High":
        color = "red"
    elif c["urgency"] == "Medium":
        color = "orange"
    else:
        color = "green"

    popup_text = f"""
    Complaint: {c['complaint']}
    Location: {c['location']}
    Category: {c['category']}
    Urgency: {c['urgency']}
    """

    folium.Marker(
        [32.37, -86.30],
        popup=popup_text,
        icon=folium.Icon(color=color)
    ).add_to(m)

st_folium(m, width=700)            
st.header("City Insights")

if len(st.session_state.complaints) > 0:

    df = pd.DataFrame(st.session_state.complaints)

    # total complaints
    total = len(df)

    # most common complaint category
    top_category = df["category"].value_counts().idxmax()

    # number of high urgency complaints
    high_urgency = len(df[df["urgency"] == "High"])

    st.write("Total Complaints:", total)
    st.write("Most Common Issue:", top_category)
    st.write("High Urgency Complaints:", high_urgency)