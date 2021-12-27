import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import smtplib
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

YOUTUBE_TRENDNG_URL = 'https://www.youtube.com/feed/trending'


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def get_videos(driver):
    VIDEO_DIVS_TAG = 'ytd-video-renderer'
    driver.get(YOUTUBE_TRENDNG_URL)
    videos = driver.find_elements(By.TAG_NAME, VIDEO_DIVS_TAG)
    return videos


def parse_video(video):
    # title, url, thumbnail_url, channel, views, uploaded, description.
    title_tag = video.find_element(By.ID, 'video-title')
    title = title_tag.text

    url = title_tag.get_attribute('href')

    thumbnail_tag = video.find_element(By.TAG_NAME, 'img')
    thumbnail_url = thumbnail_tag.get_attribute('src')

    channel_div = video.find_element(By.CLASS_NAME, 'ytd-channel-name')
    channel_name = channel_div.text

    description = video.find_element(By.ID, 'description-text').text
    return {
        "title": title,
        "url": url,
        "thumbnail_url": thumbnail_url,
        'channel': channel_name,
        'description': description

    }


def dict_to_googlesheets(api_key, spread_sheet, data):
    # define the scope
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name(api_key, scope)

    client = gspread.authorize(creds)

    # get the instance of the Spreadsheet
    sheet = client.open(spread_sheet).sheet1

    data_df = pd.DataFrame(data)

    final_sheet = sheet.insert_rows(data_df.values.tolist())

    return final_sheet

def send_email(body):
    try:
        server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server_ssl.ehlo()

        SENDER_EMAIL = "yash.iyengar.project@gmail.com"
        RECEIVER_EMAIL = "iyengar2589@gmail.com"
        SENDER_PASSWORD = os.environ['GMAIL_PASSWORD']

        # print('password', SENDER_PASSWORD)

        subject = 'YouTube Trending Videos'

        email_text = f"""\
    From: {SENDER_EMAIL}
    To: {RECEIVER_EMAIL}
    Subject: {subject}

    {body}
    """
        server_ssl.login(SENDER_EMAIL, SENDER_PASSWORD)
        server_ssl.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, email_text)
        server_ssl.close()

    except Exception as e:
        print("Something went wrong...", e)


if __name__ == "__main__":
    print("Creating Driver...")
    driver = get_driver()

    print('Fetching trending videos...')
    videos = get_videos(driver)

    print(f'Found {len(videos)} videos')

    print('Parsing the top 10 videos ')
    videos_data = [parse_video(video) for video in videos[:10]]

    print('Saving the data to Google Spreadsheets')
    dict_to_googlesheets('scrapping-practice-11696e2cdf5c.json', 'Youtube Trending Data', videos_data)

    #print("Save the data to CSV")
    # videos_df = pd.DataFrame(videos_data)
    # print(videos_df)
    # videos_df.to_csv("trending.csv", index=None)

    print("Send the results over email")

    body = {
        "link to data": "https://docs.google.com/spreadsheets/d/16psRhOF8onOjVPHi8-AALGUnrhppGjH9USDl5hrHdFs/edit#gid=0"}

    send_email(body)

    print('Finished.')


