import streamlit as st
import pandas as pd
import folium
import uuid
import requests
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MarkerCluster
from datetime import datetime
from geopy.geocoders import Nominatim
from textblob import TextBlob
from streamlit_js_eval import get_geolocation
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Smart City AI Command Center", layout="wide")

# ---------------- UI STYLE ---------------- #

st.markdown("""
<style>

.main {
    background: linear-gradient(180deg,#f8fafc,#eef2f7);
}

.block-container {
    padding-top:2rem;
    padding-bottom:2rem;
    max-width:1400px;
}

h1,h2,h3{
color:#1f2937;
}

section[data-testid="stSidebar"]{
background:linear-gradient(180deg,#1e293b,#0f172a);
}

section[data-testid="stSidebar"] *{
color:white !important;
}

.stButton>button{
background-color:#2563eb;
color:white;
border-radius:8px;
border:none;
padding:8px 16px;
font-weight:500;
}

.stButton>button:hover{
background-color:#1d4ed8;
}

.metric-card{
background:white;
padding:22px;
border-radius:12px;
border:1px solid #e5e7eb;
box-shadow:0 6px 18px rgba(0,0,0,0.06);
transition:transform 0.15s ease;
}

.metric-card:hover{
transform:translateY(-2px);
}

.complaint-card{
background:white;
padding:18px;
border-radius:12px;
border-left:5px solid #2563eb;
box-shadow:0 4px 14px rgba(0,0,0,0.05);
margin-bottom:18px;
}

.divider{
border-bottom:1px solid #e6e6e6;
margin-top:10px;
margin-bottom:10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SYSTEM ---------------- #

GOV_PASSWORD = "smartcity2026"

st_autorefresh(interval=10000, key="refresh")

geolocator = Nominatim(user_agent="smart_city_ai")

if "complaints" not in st.session_state:
    st.session_state.complaints=[]

if "gov_logged_in" not in st.session_state:
    st.session_state.gov_logged_in=False

# ---------------- DATA ---------------- #

@st.cache_data(ttl=300)
def load_city_data():

    url="https://data.montgomeryal.gov/resource/8u7v-jw6c.json"

    try:

        r=requests.get(url)
        data=r.json()

        df=pd.DataFrame(data)

        if "latitude" in df.columns:
            df["lat"]=pd.to_numeric(df["latitude"],errors="coerce")
            df["lon"]=pd.to_numeric(df["longitude"],errors="coerce")

        return df

    except:
        return pd.DataFrame()

city_df=load_city_data()

# ---------------- AI ---------------- #

def summarize(text):

    blob=TextBlob(text)

    if len(blob.sentences)>0:
        return str(blob.sentences[0])

    return text[:80]

def detect_urgency(text):

    text=text.lower()

    high=["fire","accident","sewage","leak"]
    medium=["traffic","pothole","garbage"]

    score=0

    for w in high:
        if w in text:
            score+=3

    for w in medium:
        if w in text:
            score+=2

    if score>=5:
        return "High"
    elif score>=3:
        return "Medium"
    else:
        return "Low"

def classify(text):

    text=text.lower()

    if "garbage" in text:
        return "Sanitation","Waste Management"

    elif "light" in text:
        return "Infrastructure","Electrical"

    elif "water" in text:
        return "Water","Water Department"

    elif "traffic" in text:
        return "Traffic","Traffic Department"

    elif "pothole" in text:
        return "Road Damage","Road Department"

    return "General","City Services"

def urgency_color(level):

    if level=="High":
        return "red"
    elif level=="Medium":
        return "orange"
    else:
        return "green"

# ---------------- GEO ---------------- #

def get_coordinates(location):

    try:

        loc=geolocator.geocode(location)

        if loc:
            return loc.latitude,loc.longitude,loc.address

    except:
        pass

    return None,None,location

def reverse_geocode(lat,lon):

    try:

        loc=geolocator.reverse((lat,lon))

        if loc:
            return loc.address

    except:
        pass

    return f"{lat},{lon}"

# ---------------- SIDEBAR ---------------- #

st.sidebar.markdown("# 🏙 Smart City AI")
st.sidebar.markdown("### Command Center")
st.sidebar.markdown("---")

page=st.sidebar.radio(
"Navigation",
[
"Citizen Portal",
"Track Complaint",
"Government Portal",
"Dashboard",
"City Map",
"Analytics",
"Risk Dashboard",
"Emergency Alerts"
]
)

# ---------------- CITIZEN ---------------- #

if page=="Citizen Portal":

    st.markdown("## 🏙 Citizen Complaint Portal")
    st.caption("Report civic issues directly to the city command center")
    st.markdown("---")

    if st.button("📍 Use Current Location"):

        gps=get_geolocation()

        if gps:

            st.session_state.lat=gps["coords"]["latitude"]
            st.session_state.lon=gps["coords"]["longitude"]

            st.session_state.address=reverse_geocode(
            st.session_state.lat,
            st.session_state.lon
            )

            st.success(f"Location detected: {st.session_state.address}")

    with st.form("complaint_form",clear_on_submit=True):

        complaint=st.text_area("Describe Issue")

        location=st.text_input("Enter Location")

        image=st.file_uploader("Upload Photo",type=["jpg","png","jpeg"])

        if image:
            st.image(image,width=300)

        lat=None
        lon=None
        address=location

        if location:
            lat,lon,address=get_coordinates(location)

        if "lat" in st.session_state:

            lat=st.session_state.lat
            lon=st.session_state.lon
            address=st.session_state.address

        st.subheader("Select location on map")

        map_select=folium.Map(location=[32.37,-86.30],zoom_start=12)

        map_data=st_folium(map_select,height=400,use_container_width=True)

        if map_data and map_data["last_clicked"]:
            lat=map_data["last_clicked"]["lat"]
            lon=map_data["last_clicked"]["lng"]
            address=reverse_geocode(lat,lon)

        submitted=st.form_submit_button("Submit Complaint")

        if submitted:

            if complaint.strip()=="":
                st.error("Please describe the issue")
                st.stop()

            summary=summarize(complaint)
            urgency=detect_urgency(complaint)
            category,department=classify(complaint)

            complaint_id=str(uuid.uuid4())[:8]

            st.session_state.complaints.append({

            "id":complaint_id,
            "complaint":complaint,
            "summary":summary,
            "location":address,
            "category":category,
            "department":department,
            "urgency":urgency,
            "lat":lat,
            "lon":lon,
            "image":image,
            "status":"Pending",
            "time":datetime.now()

            })

            st.success(f"✅ Complaint submitted successfully. Your ID: {complaint_id}")

# ---------------- TRACK ---------------- #

elif page=="Track Complaint":

    st.markdown("## 📍 Track Complaint")
    st.markdown("---")

    cid=st.text_input("Enter Complaint ID")

    if st.button("Track"):

        df=pd.DataFrame(st.session_state.complaints)

        result=df[df["id"]==cid]

        if len(result)==0:
            st.error("Complaint not found")

        else:

            row=result.iloc[0]

            st.markdown(f"""
            <div class="complaint-card">
            <b>Issue:</b> {row['summary']}<br>
            <b>Location:</b> {row['location']}<br>
            <b>Department:</b> {row['department']}
            </div>
            """,unsafe_allow_html=True)

            status=row["status"]

            if status=="Pending":
                st.info("Complaint received")

            elif status=="In Progress":
                st.warning("Work in progress")

            elif status=="Resolved":
                st.success("Issue resolved")

# ---------------- GOVERNMENT ---------------- #

elif page=="Government Portal":

    st.markdown("## 🏛 Government Control Panel")
    st.markdown("---")

    if not st.session_state.gov_logged_in:

        password=st.text_input("Enter Government Password",type="password")

        if st.button("Login"):

            if password==GOV_PASSWORD:
                st.session_state.gov_logged_in=True
                st.success("Access Granted")
                st.rerun()

            else:
                st.error("Incorrect Password")

        st.stop()

    if st.button("Logout"):
        st.session_state.gov_logged_in=False
        st.rerun()

    df=pd.DataFrame(st.session_state.complaints)

    if len(df)==0:
        st.info("No complaints")

    else:

        priority_map={"High":3,"Medium":2,"Low":1}
        df["priority"]=df["urgency"].map(priority_map)
        df=df.sort_values("priority",ascending=False)

        for i,row in df.iterrows():

            color=urgency_color(row["urgency"])

            st.markdown(f"""
            <div class="complaint-card">
            <b>Issue:</b> {row['summary']}<br>
            <b>Location:</b> {row['location']}<br>
            <span style='color:{color};font-weight:bold'>Urgency: {row['urgency']}</span>
            </div>
            """,unsafe_allow_html=True)

            if row["image"]:
                st.image(row["image"],width=250)

            status=st.selectbox(
            "Update Status",
            ["Pending","In Progress","Resolved"],
            index=["Pending","In Progress","Resolved"].index(row["status"]),
            key=f"s{i}"
            )

            if st.button("Update",key=f"b{i}"):

                st.session_state.complaints[i]["status"]=status
                st.success("Updated")

            st.markdown('<div class="divider"></div>',unsafe_allow_html=True)

# ---------------- DASHBOARD ---------------- #

elif page=="Dashboard":

    st.markdown("## 📊 City Dashboard")
    st.markdown("---")

    df=pd.DataFrame(st.session_state.complaints)

    if len(df)==0:
        st.info("No complaints")

    else:

        c1,c2,c3=st.columns(3)

        with c1:
            st.markdown('<div class="metric-card">',unsafe_allow_html=True)
            st.metric("Total Complaints",len(df))
            st.markdown('</div>',unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="metric-card">',unsafe_allow_html=True)
            st.metric("High Priority",len(df[df["urgency"]=="High"]))
            st.markdown('</div>',unsafe_allow_html=True)

        with c3:
            st.markdown('<div class="metric-card">',unsafe_allow_html=True)
            st.metric("Resolved",len(df[df["status"]=="Resolved"]))
            st.markdown('</div>',unsafe_allow_html=True)

        st.dataframe(
        df[["id","summary","location","department","urgency","status"]],
        use_container_width=True
        )

        st.download_button(
        "Download Complaints CSV",
        df.to_csv(index=False),
        "complaints.csv"
        )

# ---------------- MAP ---------------- #

elif page=="City Map":

    st.markdown("## 🗺 City Issue Map")
    st.markdown("---")

    df=pd.DataFrame(st.session_state.complaints)

    if len(df)>0:
        df["lat"]=pd.to_numeric(df["lat"],errors="coerce")
        df["lon"]=pd.to_numeric(df["lon"],errors="coerce")

    if len(df)>0 and df["lat"].notnull().any():
        center_lat=df["lat"].mean()
        center_lon=df["lon"].mean()
    else:
        center_lat,center_lon=32.37,-86.30

    m=folium.Map(location=[center_lat,center_lon],zoom_start=12)

    cluster=MarkerCluster().add_to(m)

    heat=[]

    for _,row in df.iterrows():

        if pd.notnull(row["lat"]) and pd.notnull(row["lon"]):

            folium.Marker(
            [row["lat"],row["lon"]],
            popup=row["summary"],
            icon=folium.Icon(color="red")
            ).add_to(cluster)

            heat.append([row["lat"],row["lon"]])

    for _,row in city_df.iterrows():

        if "lat" in row and pd.notnull(row["lat"]):

            folium.Marker(
            [row["lat"],row["lon"]],
            popup="City Data",
            icon=folium.Icon(color="blue")
            ).add_to(cluster)

            heat.append([row["lat"],row["lon"]])

    if heat:
        HeatMap(heat).add_to(m)

    st_folium(m,use_container_width=True,height=600)

# ---------------- ANALYTICS ---------------- #

elif page=="Analytics":

    st.markdown("## 📈 City Analytics")
    st.markdown("---")

    df=pd.DataFrame(st.session_state.complaints)

    if len(df)>0:

        st.bar_chart(df["department"].value_counts())
        st.bar_chart(df["location"].value_counts())

# ---------------- RISK ---------------- #

elif page=="Risk Dashboard":

    st.markdown("## ⚠ City Risk Prediction")
    st.markdown("---")

    df=pd.DataFrame(st.session_state.complaints)

    if len(df)==0:
        st.info("No data")

    else:

        risk=df["urgency"].map({
        "High":5,
        "Medium":3,
        "Low":1
        }).sum()

        if risk<10:
            level="Low"
        elif risk<25:
            level="Moderate"
        elif risk<50:
            level="High"
        else:
            level="Critical"

        st.metric("City Risk Level",level)

# ---------------- ALERTS ---------------- #

elif page=="Emergency Alerts":

    st.markdown("## 🚨 Emergency Alerts")
    st.markdown("---")

    df=pd.DataFrame(st.session_state.complaints)

    if len(df)==0 or "urgency" not in df.columns:
        st.success("No emergencies")

    else:

        alerts=df[df["urgency"]=="High"]

        if len(alerts)==0:
            st.success("No emergencies")

        else:

            for _,row in alerts.iterrows():

                st.error(
                f"🚨 {row['summary']} at {row['location']}"
                )