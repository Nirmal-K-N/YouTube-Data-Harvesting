import streamlit as st
import googleapiclient.discovery
from pymongo import MongoClient
import pandas as pd
from pprint import pprint
import mysql.connector
import certifi
from streamlit_option_menu import option_menu
import time

# This function to fetch channel details
def get_channel_details(channel_id):

    API_KEY = "AIzaSyCCqvz32NgVkl0jDLJ9ULX-a9EXPw0m0tA"

    youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=API_KEY
        )

    request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=channel_id
        )
    response = request.execute()

    channel_details = {
        "Channel_Name": response['items'][0]['snippet']['localized']['title'],
        "Channel_Id": response['items'][0]['id'],
        "Subscription_Count": response['items'][0]['statistics']['subscriberCount'],
        "Channel_Views": response['items'][0]['statistics']['viewCount'],
        "Channel_Description": response['items'][0]['snippet']['description'],
        "Playlist_Id": response['items'][0]['contentDetails']['relatedPlaylists']['uploads'],
        "Video_Count" : response['items'][0]['statistics']['videoCount']
    }

    return channel_details

#This function is to fetch all video ids
def get_video_id(playlist_id): 
    next_page = None
    video_id = []
    while True:

        API_KEY = "AIzaSyCCqvz32NgVkl0jDLJ9ULX-a9EXPw0m0tA"
        
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=API_KEY)
        
        request = youtube.playlistItems().list(part = 
                    'snippet,contentDetails',playlistId=playlist_id,
                    maxResults=50,pageToken = next_page)
        
        response = request.execute()
        
        next_page = response.get('nextPageToken')

        for item in response['items']:
            video_id_details = {
                'channel_id' : item['snippet']['channelId'],
                'video_ids' : item['contentDetails']['videoId']
            }
            
            video_id.append(video_id_details)

        if next_page is None:
            break

    return video_id

#This function is to fetch video details
def get_video_details(video_id):
        video_details = []

        API_KEY = "AIzaSyCCqvz32NgVkl0jDLJ9ULX-a9EXPw0m0tA"

        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=API_KEY
        )
        
        for v_id in video_id:
        
                request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=v_id['video_ids'] 
                )

                response = request.execute()

                
                        
                vdetails = {
                        
                        "Video_Id": response['items'][0]['id'],
                        "Video_Name": response['items'][0]['snippet']['title'],
                        "Video_Description": response['items'][0]['snippet']['description'],
                        "Tags": " ".join(response['items'][0]['snippet'].get('tags',["NA"])),
                        "PublishedAt": response['items'][0]['snippet']['publishedAt'],
                        "View_Count": response['items'][0]['statistics']['viewCount'],
                        "Like_Count": response['items'][0]['statistics']['likeCount'],
                        "Favorite_Count": response['items'][0]['statistics']['favoriteCount'],
                        "Comment_Count": response['items'][0]['statistics']['commentCount'],
                        "Duration": response['items'][0]['contentDetails']['duration'],
                        "Thumbnail": response['items'][0]['snippet']['thumbnails']['default']['url'],
                        "Caption_Status": response['items'][0]['contentDetails']['caption'],
                }
        
                video_details.append(vdetails)   
        
        return video_details

#This function is to fetch comment details
def get_comment_details(video_id):    

        comment_details = []
        API_KEY = "AIzaSyCCqvz32NgVkl0jDLJ9ULX-a9EXPw0m0tA"

        youtube = googleapiclient.discovery.build(
                "youtube", "v3", developerKey=API_KEY
                )

        for i in video_id:
                try:

                        request = youtube.commentThreads().list(
                                part="snippet,replies",
                                maxResults=100,
                                videoId= i['video_ids'] 
                                )
                        response = request.execute()
                        
                        for j in range(len(response['items'])):

                                c_details = { 
                                        "video_id" : response['items'][0]['snippet']['topLevelComment']['snippet']['videoId'],
                                        "comment_id" : response['items'][0]['snippet']['topLevelComment']['snippet']['authorChannelId']['value'],
                                        "comment_text" : response['items'][0]['snippet']['topLevelComment']['snippet']['textDisplay'],
                                        "comment_author" : response['items'][0]['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                        "comment_published_at" : response['items'][0]['snippet']['topLevelComment']['snippet']['updatedAt']
                                        }

                                comment_details.append(c_details)
                except:pass

        return comment_details

#This function is to get complete channel details
def complete_data(channel_id):
    c = get_channel_details(channel_id)
    p = get_video_id(c['Playlist_Id'])
    v = get_video_details(p)
    cm = get_comment_details(p)

    data = {
        'channel details' : c,
        'playlist details' : p,
        'video details' : v,
        'comment details' : cm
    }
    
    return data

#Creating Streamlit 
st.set_page_config(
    page_title="YouTube Data Harvesting",
    page_icon="▶️",
    layout="wide",
    initial_sidebar_state="expanded")

#Creating a sidebar
with st.sidebar:
    selected = option_menu("Main Menu", ["Home","To Add Channel Details","Frequently Asked Questions"], 
                icons=['house','plus', 'question'], menu_icon="cast", default_index=0)
    
    if selected == "Frequently Asked Questions":
         QN = st.radio(
                    "**Questions?**",
                    ["Question1", "Question2", "Question3","Question4","Question5",
                     "Question6", "Question7", "Question8","Question9","Question10"],
                    index=None)

#To Add Channel Details Sidebar
if selected == "Home":
    st.title("YouTube Data Harvesting")
    st.divider()
    st.write("""**This project aims to develop a user-friendly Streamlit application that utilizes the Google API 
            to extract information on a YouTube channel, stores it in a MongoDB database, migrates it 
            to a SQL data warehouse, and enables users to search for channel details and join tables 
            to view data in the Streamlit app.**""")
    st.subheader(":orange[Skills Takeaway From This Project]")
    st.text("> Python scripting,")
    st.text("> Data Collection,")
    st.text("> MongoDB,")
    st.text("> Streamlit,")
    st.text("> API integration,")
    st.text("> Data Management using MongoDB (Atlas), &")
    st.text("> SQL")
    st.subheader('',divider='orange')
    
elif selected == "To Add Channel Details":
    st.subheader(':orange[Enter the Channel ID]')
    channel_id = st.text_input('')
    c_data= {}
    if channel_id and st.button('SCRAP & ADD'):
        con = MongoClient("mongodb://localhost:27017/")
        db = con['Project_1']
        col = db['youtube_data_harvesting']
    #Checking if the channel already exists
        try:
            check_existing_document = col.find_one({"channel details.Channel_Id": channel_id})
            if check_existing_document is None:
                c_data = complete_data(channel_id)
                col.insert_one(c_data)
                #Fetching the data from MongoDB and converting into DataFrame 
                c_d = []
                for data in col.find({"channel details.Channel_Id": channel_id}):
                    c_d.append(data['channel details'])
                CD = pd.DataFrame(c_d)

                p_id = []
                for data in col.find({"channel details.Channel_Id": channel_id}):
                    for i in range(int(data['channel details']['Video_Count'])):
                        p_id.append(data['playlist details'][i])
                PD = pd.DataFrame(p_id)

                v_d = []
                for data in col.find({"channel details.Channel_Id": channel_id}):
                    for i in range(int(data['channel details']['Video_Count'])):
                        v_d.append(data['video details'][i])
                VD = pd.DataFrame(v_d)

                #Converting the Time and Duration into the required format in Video Details
                VD['PublishedAt'] = pd.to_datetime(VD['PublishedAt'], format='%Y-%m-%dT%H:%M:%SZ', utc=True)
                VD['Duration'] = pd.to_timedelta(VD['Duration'])
                VD['Duration'] = VD['Duration'].astype(str)
                VD['Duration'] = [i[-1] for i in (VD['Duration'].str.split())]

                cm_d = []
                for data in col.find({"channel details.Channel_Id": channel_id}):
                        for i in range(len(data['comment details'])):
                                cm_d.append(data['comment details'][i])
                CMD = pd.DataFrame(cm_d)

                #Converting the Time into the required format in Comment Details
                CMD['comment_published_at'] = pd.to_datetime(CMD['comment_published_at'], format='%Y-%m-%dT%H:%M:%SZ', utc=True)

                #Creating MYSql Connection
                db = mysql.connector.connect(
                    host = 'localhost',
                    user = 'root',
                    password = 'Nirmal9699',
                    database = 'youtube_data'
                )
                cur = db.cursor()
                db.commit()

                #Adding the DataFrame into SQL
                sql_cd = "insert into channel_details values(%s,%s,%s,%s,%s,%s,%s)"
                for i in CD.to_records().tolist():
                    cur.execute(sql_cd,i[1:])
                db.commit()

                sql_vid = "insert into video_ids values(%s,%s)"
                for i in PD.to_records().tolist():
                    cur.execute(sql_vid,i[1:])
                db.commit()

                sql_vd = "insert into video_details values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                for i in VD.to_records().tolist():
                    cur.execute(sql_vd,i[1:])
                db.commit()

                sql_cmd = "insert into comment_details values(%s,%s,%s,%s,%s)"
                for i in CMD.to_records().tolist():
                    cur.execute(sql_cmd,i[1:])
                db.commit()
                st.success('Successfully uploaded ',icon='✔️')

            else:
                st.warning(f'OOPS! Document already exists for channel ID: {channel_id}', icon="❗")
        except Exception as e:
            st.error("Error occurred while uploading channel information")   

#Frequently Asked Questions Sidebar
elif selected == "Frequently Asked Questions":

    #MYSql Connection
    db = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = 'Nirmal9699',
        database = 'youtube_data'
    )
    cur = db.cursor()

    #Question 1
    if QN == "Question1":
        st.write("**1. What are the names of all the videos and their corresponding channels?**")
        with st.spinner('Fetching information...'):
            time.sleep(2)
        def qust_1():
            sql = """WITH SQ AS (
                    SELECT *
                    FROM video_ids vi
                    JOIN video_details vd
                    ON vi.Video_Ids = vd.Video_Id )
                    SELECT cd.Channel_Name, sq.Video_Name
                    FROM channel_details cd
                    JOIN SQ sq USING (Channel_Id)"""
            cur.execute(sql)
            data = cur.fetchall()
            data_df = pd.DataFrame(data, columns=['CHANNEL_NAME', 'VIDEO_NAME']).reset_index(drop=True)
            data_df.index += 1
            return data_df
        Q1 = qust_1()
        st.table(Q1)

    #Question 2
    elif QN == "Question2":
        st.write("**2. Which channels have the most number of videos, and how many videos do they have?**")
        with st.spinner('Fetching information...'):
            time.sleep(2)
        def qust_2():
            sql = """WITH SQ AS (
                    SELECT *
                    FROM video_ids vi
                    JOIN video_details vd
                    ON vi.Video_Ids = vd.Video_Id )
                    SELECT cd.Channel_Name, COUNT(sq.Video_Id) AS video_count 
                    FROM channel_details cd JOIN SQ sq
                    ON cd.Channel_Id = sq.Channel_Id 
                    GROUP BY cd.Channel_Name 
                    ORDER BY video_count DESC"""
            cur.execute(sql)
            data = cur.fetchall()
            data_df = pd.DataFrame(data, columns=['CHANNEL_NAME', 'VIDEO_COUNT']).reset_index(drop=True)
            data_df.index += 1
            return data_df
        Q2 = qust_2()
        st.table(Q2)

    #Question 3
    elif QN == "Question3":
        st.write("**3. What are the top 10 most viewed videos and their respective channels?**")
        with st.spinner('Fetching information...'):
            time.sleep(2)
        def qust_3():
            print("TOP 10 CHANNEL VIEWS")
            sql = """WITH SQ AS (
                    SELECT *
                    FROM video_ids vi
                    JOIN video_details vd
                    ON vi.Video_Ids = vd.Video_Id )
                    SELECT cd.Channel_Name,sq.Video_Name,sq.View_Count 
                    FROM SQ sq JOIN channel_details cd 
                    ON sq.Channel_Id = cd.Channel_Id
                    ORDER BY sq.View_Count DESC 
                    LIMIT 10"""
            cur.execute(sql)
            data = cur.fetchall()
            data_df = pd.DataFrame(data, columns=['CHANNEL_NAME', 'VIDEO_NAME', 'VIEW_COUNT']).reset_index(drop=True)
            data_df.index += 1
            return data_df
        Q3=qust_3()
        st.table(Q3)

    #Question 4
    elif QN == "Question4":
        st.write("**4. How many comments were made on each video, and what are their corresponding video names?**")
        with st.spinner('Fetching information...'):
            time.sleep(2)
        def qust_4():
            sql = """SELECT Video_Name, Comment_Count 
                    from video_details 
                    ORDER BY comment_count DESC"""
            cur.execute(sql)
            data = cur.fetchall()
            data_df = pd.DataFrame(data, columns=['VIDEO_NAME', 'COMMENT_COUNT']).reset_index(drop=True)
            data_df.index += 1
            return data_df
        Q4=qust_4()
        st.table(Q4)
    
    #Question 5
    elif QN == "Question5":
        st.write("**5. Which videos have the highest number of likes, and what are their corresponding channel names?**")
        with st.spinner('Fetching information...'):
            time.sleep(2)
        def qust_5():
            sql = """WITH SQ AS (
                    SELECT *
                    FROM video_ids vi
                    JOIN video_details vd
                    ON vi.Video_Ids = vd.Video_Id )
                    SELECT cd.Channel_Name, sq.Video_Name, sq.Like_Count 
                    FROM SQ sq JOIN channel_details cd 
                    ON sq.Channel_Id = cd.Channel_Id 
                    ORDER BY sq.Like_Count DESC"""
            cur.execute(sql)
            data = cur.fetchall()
            data_df = pd.DataFrame(data, columns=['CHANNEL_NAME', 'VIDEO_NAME','LIKE_COUNT']).reset_index(drop=True)
            data_df.index += 1
            return data_df
        Q5 = qust_5()
        st.table(Q5)

    #Question 6
    elif QN == "Question6":
        st.write("**6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?**")
        with st.spinner('Fetching information...'):
            time.sleep(2)
        def qust_6():
            sql = """SELECT Video_Name, Like_Count 
                    FROM video_details
                    ORDER BY Like_Count DESC"""
            cur.execute(sql)
            data = cur.fetchall()
            data_df = pd.DataFrame(data, columns=['VIDEO_NAME', 'LIKE_COUNT']).reset_index(drop=True)
            data_df.index += 1
            return data_df
        Q6 = qust_6()
        st.table(Q6)

    #Question 7
    elif QN == "Question7":
        st.write("**7. What is the total number of views for each channel, and what are their corresponding channel names?**")
        with st.spinner('Fetching information...'):
            time.sleep(2)
        def qust_7():
            sql = """SELECT Channel_Name, Channel_views
                    FROM channel_details
                    ORDER BY Channel_Views DESC"""
            cur.execute(sql)
            data= cur.fetchall()
            data_df = pd.DataFrame(data, columns=['CHANNEL_NAME', 'CHANNEL_VIEWS']).reset_index(drop=True)
            data_df.index += 1
            return data_df
        Q7 = qust_7()
        st.table(Q7)
        
    #Question 8
    elif QN == "Question8":
        st.write("**8. What are the names of all the channels that have published videos in the year 2022?**")
        with st.spinner('Fetching information...'):
            time.sleep(2)
        def qust_8():
            sql = """WITH SQ AS (
                    SELECT *
                    FROM video_ids vi
                    JOIN video_details vd
                    ON vi.Video_Ids = vd.Video_Id )
                    SELECT cd.Channel_Name, sq.Video_Name, sq.PublishedAt 
                    FROM channel_details cd JOIN SQ sq 
                    ON cd.Channel_Id = sq.Channel_Id
                    WHERE EXTRACT(YEAR FROM sq.PublishedAt) = 2022"""
            cur.execute(sql)
            data= cur.fetchall()
            data_df = pd.DataFrame(data, columns=['CHANNEL_NAME', 'VIDEO_NAME', 'VIDEO_2022']).reset_index(drop=True)
            data_df.index += 1
            return data_df
        Q8 = qust_8()
        st.table(Q8)
        
    #Question 9
    elif QN == "Question9":
        st.write("**9. What is the average duration of all videos in each channel, and what are their corresponding channel names?**")
        with st.spinner('Fetching information...'):
            time.sleep(2)
        def qust_9():
            sql = """WITH SQ AS (
                    SELECT *
                    FROM video_ids vi
                    JOIN video_details vd
                    ON vi.Video_Ids = vd.Video_Id )
                    SELECT cd.Channel_Name, ROUND(AVG(sq.Duration),2) AS average_duration 
                    FROM channel_details cd JOIN SQ sq 
                    ON cd.Channel_Id = sq.Channel_Id 
                    GROUP BY cd.channel_name 
                    ORDER BY average_duration DESC"""
            cur.execute(sql)
            data = cur.fetchall()
            data_df = pd.DataFrame(data, columns=['CHANNEL_NAME', 'AVERAGE_DURATION']).reset_index(drop=True)
            data_df.index += 1
            return data_df
        Q9 = qust_9()
        st.table(Q9)

    #Question 10
    elif QN == "Question10":
        st.write("**10. Which videos have the highest number of comments, and what are their corresponding channel names?**")
        with st.spinner('Fetching information...'):
            time.sleep(2)
        def qust_10():
            sql = """WITH SQ AS (
                    SELECT *
                    FROM video_ids vi
                    JOIN video_details vd
                    ON vi.Video_Ids = vd.Video_Id )
                    SELECT cd.Channel_Name, sq.Video_Name, sq.Comment_Count 
                    FROM SQ sq 
                    JOIN channel_details cd 
                    ON cd.Channel_Id = sq.Channel_Id
                    ORDER BY comment_count DESC"""
            cur.execute(sql)
            data = cur.fetchall()
            data_df = pd.DataFrame(data, columns=['CHANNEL_NAME', 'VIDEO_NAME','COMMENT_COUNT']).reset_index(drop=True)
            data_df.index += 1
            return data_df
        Q10 = qust_10()
        st.table(Q10)        


    