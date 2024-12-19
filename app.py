import streamlit as st
import pydeck as pdk
from fetch_news import fetch_and_store_news, fetch_data_from_mongo
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
from datetime import date

# Define disaster types for filtering
disaster_types = ['All', 'Flood', 'Landslide', 'Earthquake', 'Tsunami', 'Wildfire', 'Hurricane', 'Cyclone', 'Storm', 'Drought', 'Volcano']

# Define precautions and images for each disaster type
precautions = {
    'Flood': {
        'text': "1. Avoid walking or driving through floodwater.\n2. Stay indoors and away from windows.\n3. Use sandbags to block water entry if possible.\n4. Keep important documents and valuables on higher floors.",
        'image': 'https://ichef.bbci.co.uk/news/976/cpsprodpb/920A/production/_103068373_048715246-1.jpg'
    },
    'Landslide': {
        'text': "1. Avoid areas prone to landslides.\n2. Stay alert to weather forecasts and warnings.\n3. Evacuate if landslide activity is reported in your area.\n4. Secure your home and avoid placing structures on slopes.",
        'image': 'https://img.manoramayearbook.in/content/dam/yearbook/learn/world/images/2024/may/landslide.jpg'
    },
    'Earthquake': {
        'text': "1. Drop, Cover, and Hold On during shaking.\n2. Stay away from windows and heavy furniture.\n3. Have an emergency kit ready.\n4. Plan and practice earthquake drills with your family.",
        'image': 'https://media-cldnry.s-nbcnews.com/image/upload/t_fit-760w,f_auto,q_auto:best/rockcms/2024-01/240117-japan-earthquake-05-aa-1b5d87.jpg'
    },
    'Tsunami': {
        'text': "1. Move to higher ground immediately if you feel an earthquake.\n2. Follow evacuation orders and avoid going to the beach.\n3. Stay away from coastal areas during a tsunami warning.\n4. Have an emergency kit prepared and include a battery-powered radio.",
        'image': 'https://www.optimumseismic.com/wp-content/uploads/2022/02/Earthquakes-and-Tsunamis-A-Double-Whammy-for-Coastal-Communities.jpg'
    },
    'Wildfire': {
        'text': "1. Create a defensible space around your home.\n2. Avoid using outdoor fires and smoking.\n3. Follow evacuation orders promptly.\n4. Have an emergency kit ready, including masks for smoke inhalation.",
        'image': 'https://cdn.who.int/media/images/default-source/health-and-climate-change/fire-fighters-at-forest-fire-c-quarrie-photography.tmb-479v.jpg?sfvrsn=8b60f828_4%20479w'
    },
    'Hurricane': {
        'text': "1. Prepare an emergency kit with essential supplies.\n2. Follow evacuation orders and seek shelter in a safe location.\n3. Stay informed about weather updates and potential impact.\n4. Secure your home and protect windows and doors.",
        'image': 'https://images.contentstack.io/v3/assets/blt0a0cb058815d4d96/blta962aadca1267515/6310fa17eb56af5839111e2e/Wind_and_Hurricane_Damage_to_Home.jpg?width=1440'
    },
    'Cyclone': {
        'text': "1. Move to a safe location away from coastal areas.\n2. Follow local authorities' evacuation orders.\n3. Secure your home and bring in outdoor furniture.\n4. Have an emergency kit ready with food, water, and medical supplies.",
        'image': 'https://static.toiimg.com/photo/100469199/100469199.jpg'
    },
    'Storm': {
        'text': "1. Stay indoors and avoid travel during severe storms.\n2. Secure windows and doors.\n3. Avoid using electrical appliances during storms.\n4. Have an emergency kit with flashlights and batteries.",
        'image': 'https://thumbs.dreamstime.com/b/strom-columbus-ohio-united-states-usa-42170357.jpg'
    },
    'Drought': {
        'text': "1. Conserve water and use it efficiently.\n2. Support and follow local water restrictions.\n3. Maintain a garden with drought-resistant plants.\n4. Educate yourself on sustainable water practices.",
        'image': 'https://earth.org/wp-content/uploads/2022/05/rsz_sujon_adikary_2-min-1200x675.jpg'
    },
    'Volcano': {
        'text': "1. Follow evacuation orders promptly.\n2. Protect yourself from ashfall with masks and goggles.\n3. Stay indoors and keep windows and doors closed.\n4. Prepare an emergency kit with essentials including masks for ash inhalation.",
        'image': 'https://cdn.britannica.com/64/248964-138-C9CF1DD3/what-are-volcanoes-lava-flows.jpg?w=800&h=450&c=crop'
    }
}
default_booking_form = {
    "name": "",
    "email": "",
    "phone": "",
    "organization": "NGO",
    "training_type": "Disaster Preparedness",
    "preferred_date": date.today(),
    "message": ""
}
booking_form = default_booking_form.copy()

# Add navigation options in the sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Precautions", "Info", "Insights","Book A Training", "About Us"])

# Add a button to enable real-time notifications in the sidebar
st.sidebar.header("Real-Time Notifications")
notifications_enabled = st.sidebar.checkbox('Enable Real-Time Notifications', value=st.session_state.get('notifications_enabled', False))

# Store the notification preference in session state
st.session_state.notifications_enabled = notifications_enabled

# Add a placeholder for notifications
notification_placeholder = st.empty()

# Function to convert string to datetime
def parse_datetime(date_str):
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        return None

# Function to check for new articles and send notifications
def check_for_new_articles(last_fetched_time):
    articles = fetch_data_from_mongo()
    new_articles = []
    
    for article in articles:
        published_at = parse_datetime(article.get('publishedAt', ''))
        if published_at and published_at > last_fetched_time:
            new_articles.append(article)
            notification_placeholder.markdown(f"*New Article Alert!*\n\n**Title:** {article.get('title')}\n**Description:** {article.get('description')}\n**Published At:** {article.get('publishedAt')}")
    
    return new_articles

# Store the last fetch time
if 'last_fetch_time' not in st.session_state:
    st.session_state.last_fetch_time = datetime.now(pytz.utc)

# Define disaster type colors and sizes
disaster_colors = {
    'Flood': [0, 0, 255, 160],       # Blue
    'Landslide': [139, 69, 19, 160],  # Brown
    'Earthquake': [50, 128, 128, 160],   # White
    'Tsunami': [0, 255, 255, 160],    # Cyan
    'Wildfire': [255, 165, 0, 160],   # Orange
    'Hurricane': [0, 128, 0, 160],    # Green
    'Cyclone': [255, 105, 180, 160],  # Pink
    'Storm': [128, 0, 128, 160],      # Purple
    'Drought': [255, 215, 0, 160],    # Gold
    'Volcano': [255, 69, 0, 160]      # Tomato
}

disaster_sizes = {
    'Flood': 18000,
    'Landslide': 18000,
    'Earthquake': 18000,
    'Tsunami': 18000,
    'Wildfire': 18000,
    'Hurricane': 18000,
    'Cyclone': 18000,
    'Storm': 18000,
    'Drought': 18000,
    'Volcano': 18000
}

# Display the content based on the selected page
if page == "Home":
    st.markdown("<h1 style='text-align: center;'>AlertFlow</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Real-Time Disaster Information Aggregation Software</h4>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>This is a web application to monitor and visualize disasters in real-time using news data.</p>", unsafe_allow_html=True)

    # Add a button to fetch the latest news
    if st.button('Fetch Latest News'):
        fetch_and_store_news()

    # Check for new articles and show notifications if enabled
    if st.session_state.notifications_enabled:
        new_articles = check_for_new_articles(st.session_state.last_fetch_time)
        if new_articles:
            st.session_state.last_fetch_time = datetime.now(pytz.utc)

    # Sidebar dropdown for disaster type filtering
    st.sidebar.header("Filter by Disaster Type")
    selected_disaster_types = st.sidebar.multiselect(
        "Select disaster types:",
        disaster_types,
        default=['All']  # Default selects "All"
    )

    # Display Latest News
    if st.button('Display Latest News'):
        articles = fetch_data_from_mongo()
        if articles:
            st.sidebar.header("News Articles")
            for article in articles:
                if 'All' in selected_disaster_types or any(d.lower() in article.get('title', '').lower() for d in selected_disaster_types):
                    st.sidebar.subheader(article.get('title'))
                    st.sidebar.write(article.get('description'))
                    st.sidebar.write(f"Published At: {article.get('publishedAt')}")
                    st.sidebar.write("---")

            # Extract coordinates and related information for the map
            map_data = []
            for article in articles:
                location = article.get('location')
                if location and ('All' in selected_disaster_types or any(d.lower() in article.get('title', '').lower() for d in selected_disaster_types)):
                    disaster_type = article.get('disaster_type', 'Unknown')
                    map_data.append({
                        'lat': location.get('latitude'),
                        'lon': location.get('longitude'),
                        'title': article.get('title'),
                        'description': article.get('description'),
                        'disaster_type': disaster_type,
                        'color': disaster_colors.get(disaster_type, [255, 0, 0, 160]),
                        'size': disaster_sizes.get(disaster_type, 10000)
                    })

            # Display the map
            if map_data:
                # Check if map data is valid and non-empty
                if any([d['lat'] and d['lon'] for d in map_data]):
                    st.pydeck_chart(pdk.Deck(
                        initial_view_state=pdk.ViewState(
                            latitude=map_data[0]['lat'],
                            longitude=map_data[0]['lon'],
                            zoom=3,
                            pitch=0
                        ),
                        layers=[
                            pdk.Layer(
                                'ScatterplotLayer',
                                data=map_data,
                                get_position=['lon', 'lat'],
                                get_color='color',
                                get_radius='size',
                                pickable=True,
                                auto_highlight=True
                            )
                        ],
                        tooltip={"text": "{title}\n{description}\nDisaster Type: {disaster_type}"}
                    ))
                else:
                    st.write("Map data is missing or invalid.")
            else:
                st.write("No data available for the selected disaster types.")
                
elif page == "Precautions":
    st.markdown("<h1 style='text-align: center;'>Disaster Precautions</h1>", unsafe_allow_html=True)
    disaster_type = st.selectbox("Select Disaster Type:", options=disaster_types)
    
    if disaster_type != 'All':
        if disaster_type in precautions:
            st.write(f"**Precautions for {disaster_type}:**")
            st.write(precautions[disaster_type]['text'])
            st.image(precautions[disaster_type]['image'])
        else:
            st.write("No precautions available for the selected disaster type.")
elif page == "Book A Training":
    st.title("Education & Training Portal")
    st.markdown("### Explore training opportunities and book your session today.")

    # Training Options
    st.markdown("#### Training Options")
    col1, col2, col3 = st.columns(3)
    col1.markdown("##### NGO Training\nConnect with NGOs for community-based disaster preparedness training.")
    col2.markdown("##### NSS Programs\nProfessional disaster management and safety training programs.")
    col3.markdown("##### NCC Workshops\nOfficial civil defense and emergency response workshops.")

    # Booking Form
    st.markdown("### Book a Training Session")
    with st.form(key="booking_form"):
        col1, col2 = st.columns(2)
        booking_form["name"] = col1.text_input("Name", value=booking_form["name"])
        booking_form["email"] = col2.text_input("Email", value=booking_form["email"])
        
        col1, col2 = st.columns(2)
        booking_form["phone"] = col1.text_input("Phone", value=booking_form["phone"])
        booking_form["organization"] = col2.selectbox(
            "Organization",
            ["NGO", "NSS", "NCC"],
            index=["NGO", "NSS", "NCC"].index(booking_form["organization"])
        )

        col1, col2 = st.columns(2)
        booking_form["training_type"] = col1.selectbox(
            "Training Type",
            ["Disaster Preparedness", "Emergency Response", "First Aid", "Community Resilience"],
            index=["Disaster Preparedness", "Emergency Response", "First Aid", "Community Resilience"].index(
                booking_form["training_type"]
            )
        )
        booking_form["preferred_date"] = col2.date_input("Preferred Date", value=booking_form["preferred_date"])

        booking_form["message"] = st.text_area("Additional Message", value=booking_form["message"], height=100)

        submit = st.form_submit_button("Book Session")
        if submit:
            st.success("Thank you for booking a session! We will contact you shortly.")
            st.write("Booking Details:")
            st.json(booking_form)
            # Reset form
            booking_form = default_booking_form.copy()
elif page == "Info":
    st.markdown("<h1 style='text-align: center;'>Project Information</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Welcome to the AlertFlow project. Below is some information about this project:</p>", unsafe_allow_html=True)

    st.markdown("""
    Project Name: AlertFlow
    
    \n Description:
    AlertFlow is a web application designed to monitor and visualize real-time disaster information using news data.The application aggregates news articles related to natural disasters, filters them based on user preferences, and visualizes the information on a map.
    """)
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("""\n""")
        st.markdown("""\n""")
        st.image("https://cdn-icons-png.flaticon.com/512/6693/6693772.png", width=130)  
    with col2:
        st.markdown("""
        **Features:**
        - Fetch and display the latest news articles about natural disasters.
        - Filter news articles by disaster type.
        - Display relevant articles and their locations on an interactive map.
        - Provide precautions for various types of disasters to help users prepare and respond effectively.
        """)

    with col1:
        st.markdown("""\n""")
        st.markdown("""\n""")
        st.markdown("""\n""")
        st.markdown("""\n""")
        st.image("https://cdn-icons-png.flaticon.com/512/11485/11485933.png", width=130)  
    with col2:
        st.markdown("""\n""")
        st.markdown("""\n""")
        st.markdown("""\n""")
        st.markdown("""
        **Future Enhancements:**
        - Integrate more data sources for comprehensive disaster information.
        - Improve filtering and search capabilities for better user experience.
        - Add user authentication and personalized features.
        """)
        
elif page == "About Us":
    st.markdown("<h1 style='text-align: center;'>About Us</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Welcome to the AlertFlow project. Below is some information about us.</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <h2 style='text-align: center;'>Team Details</h2>
    <ul style='font-size: 30px;'>
        <li><strong>Mohammed Saad</strong></li>
        <li><strong>Om Prakash Shukla</strong></li>
        <li><strong>Aashi Dhariwal</strong></li>
        <li><strong>Mohammed Touhid</strong></li>
    </ul>
    """, unsafe_allow_html=True)
    st.markdown("""
    <h2 style='text-align: center;'>Tech Stack:</h2>
    <ul style='font-size: 30px;'>
        <li><strong>Python</strong> - <em>(For development and NLP)</em></li>
        <li><strong>News-API</strong> - <em>(For collecting news data)</em></li>
        <li><strong>SpaCy</strong> - <em>(For NLP and Geo-coding)</em></li>
        <li><strong>MongoDB</strong> - <em>(For storing collected news data)</em></li>
        <li><strong>GeoPy</strong> - <em>(For geo-tagging of affected locations)</em></li>
        <li><strong>PlotLy</strong> - <em>(For analysis (graphs and charts))</em></li>
        
    </ul>
    """, unsafe_allow_html=True)
    
elif page == "Insights":
    st.markdown("<h1 style='text-align: center;'>Insights</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>This section will provide insights and visualizations based on the collected data.</h2>", unsafe_allow_html=True)

    articles = fetch_data_from_mongo()

    if articles:
        # Create a DataFrame from the articles
        disaster_data = pd.DataFrame([{'Disaster Type': article['disaster_type'], 'Date': article['publishedAt']} 
                                      for article in articles if 'disaster_type' in article and 'publishedAt' in article])
        
        # Convert the 'Date' to datetime format
        disaster_data['Date'] = pd.to_datetime(disaster_data['Date'])
        
        # Group by Date and Disaster Type, count the occurrences
        disaster_counts = disaster_data.groupby([disaster_data['Date'].dt.strftime('%Y-%m-%d'), 'Disaster Type']).size().reset_index(name='Count')

        # Create a bar chart using Plotly
        fig = px.bar(disaster_counts, x='Date', y='Count', color='Disaster Type', title='Disaster Occurrences Over Time', 
                     labels={'Date': 'Date', 'Count': 'Number of Disasters'})
        
        # Display the chart in Streamlit
        st.plotly_chart(fig)

    articles = fetch_data_from_mongo()
    if articles:
        disaster_counts = pd.DataFrame([article['disaster_type'] for article in articles if 'disaster_type' in article], columns=['Disaster Type'])
        fig = px.pie(disaster_counts, names='Disaster Type', title='Disaster Type Distribution')
        st.plotly_chart(fig)
