import streamlit as st

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

    if complaint.strip() == "":
        st.error("Please enter a complaint.")
    else:
        result = classify_complaint(complaint)

        st.success("Complaint analyzed!")

        st.write("Complaint:", complaint)
        st.write("Location:", location)

        st.subheader("AI Analysis")

        st.write("Category:", result["Category"])
        st.write("Department:", result["Department"])
        st.write("Urgency:", result["Urgency"])