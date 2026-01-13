import base64
# genai.configure(api_key='AIzaSyBL3-CdPGqYHk6VON_i9yL49pV5FaXDJGY')
import os
import re
import shutil
import time
import xml.etree.cElementTree as ET
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.wait import WebDriverWait
import requests
import speech_recognition as sr
from os import path
from pydub import AudioSegment
import uuid
from webdriver_manager.chrome import ChromeDriverManager
import requests
import google.generativeai as genai
import subprocess

ffmpeg_path = r"C:\Users\Samiksha Shinde\Desktop\web scraping project\ffmpeg-7.1-full_build\bin\ffmpeg.exe"

def recognize_speech_from_wav(driver,wav_file):
    # Initialize recognizer class (for recognizing the speech)
    recognizer = sr.Recognizer()

    try:
        # Load the .wav file
        with sr.AudioFile(wav_file) as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise in the environment
            print("Listening to the audio...")
            audio_data = recognizer.record(source)  # Record the audio from the file

            # Recognize speech using Google Web Speech API
            print("Recognizing speech...")
            text = recognizer.recognize_google(audio_data)

            print("Recognized Text: " + text)
            return text

    except sr.UnknownValueError:
        print("Speech Recognition could not understand the audio.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")


def captcha_filling_fun(driver,Selector):

    while True:
        try:
            iframe = driver.find_element(By.XPATH,'//iframe[@title="reCAPTCHA"]')
            driver.switch_to.frame(iframe)
            time.sleep(2)

            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="recaptcha-anchor"]'))).click()
            time.sleep(3)

            driver.switch_to.default_content()
            time.sleep(2)
            
            #try:
                #iframe = driver.find_element(By.XPATH,'//*[@id="OpportunityDetailModal_iframe"]')
                #driver.switch_to.frame(iframe)
                #time.sleep(2)
            #except:
                #pass

            iframe = driver.find_element(By.XPATH,'//iframe[@title="recaptcha challenge expires in two minutes"]')
            driver.switch_to.frame(iframe)
            time.sleep(2)
            

            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="recaptcha-audio-button"]'))).click()
            time.sleep(3)

            audio_src = driver.find_element(By.CSS_SELECTOR,'#audio-source').get_attribute('src')
            print("audio_src::",audio_src)


        #   Step 1: Download the audio file from the URL
            response = requests.get(audio_src)

            # Save the audio to a temporary file
            audio_file = "captcha_audio.mp3"
            with open(audio_file, "wb") as file:
                file.write(response.content)

            # Convert MP3 to WAV for SpeechRecognition compatibility
            mp3_file = "C:/Users/Samiksha Shinde/Desktop/web scraping project/"+audio_file
            output_wav_file = "output.wav"
            command = [ffmpeg_path, "-i", mp3_file, "-ac", "1", output_wav_file]
            subprocess.run(command)

            wav_file = "C:/Users/Samiksha Shinde/Desktop/web scraping project/"+output_wav_file

            # Call the function to extract text from the WAV file
            
            try:
                extract_text = recognize_speech_from_wav(driver,wav_file)
                
                if extract_text  == '' or extract_text == None:
                    print("extract_text:", extract_text)
                    print("Failed to extract text.")
                    os.remove(wav_file)
                    os.remove(mp3_file)
                    return 
            except:
                pass 
                
            try:
                driver.find_element(By.XPATH,'//*[@id="audio-response"]').send_keys(extract_text)
            except:
                print("didn't understand audio")
                return 
          

            #click on verify button
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="recaptcha-verify-button"]'))).click()
            time.sleep(3)
            

            try:
                error_text = driver.find_element(By.XPATH,'//div[@class="rc-audiochallenge-error-message"]').text
                driver.switch_to.default_content()
                time.sleep(2)
                print(error_text)
                driver.refresh()                   
                time.sleep(5)
            except:
                driver.switch_to.default_content()
                time.sleep(2)
                table_data = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, Selector)))
                print("captcha solved successfully")
                break

            os.remove(wav_file)
            os.remove(mp3_file)
            
        except:
            error_text = driver.find_element(By.XPATH,' //*[@class="rc-doscaptcha-header-text"]').text
            print('please try after sometime')
            os.remove(wav_file)
            os.remove(mp3_file)
            break
