#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A demo of the Google CloudSpeech recognizer."""
import argparse
import locale
import logging

from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient

from google.cloud import texttospeech
from pygame import mixer

import time

# -*- encoding: utf-8 -*-
import requests
import json


client = texttospeech.TextToSpeechClient()


def get_answer(text, user_key):

    print("get_answer... start")

    data_send = {
        'query': text,
        'sessionId': user_key,
        'lang': 'ko',
    }

    data_header = {
        'Authorization': 'Bearer 56b4c79017514fb6a27a45ce43bc21a3', ## Client access token 
        'Content-Type': 'application/json; charset=utf-8'
    }

    dialogflow_url = 'https://api.dialogflow.com/v1/query?v=20150910'

    res = requests.post(dialogflow_url, data=json.dumps(data_send), headers=data_header)
    ##  post 방식으로  text = 질문 , user_key = "JP"  

    if res.status_code != requests.codes.ok:
        return '오류가 발생했습니다.'

    data_receive = res.json()   ### JSON 형태로 변환
    answer = data_receive['result']['fulfillment']['speech'] 


    return answer




def tts_answer(answer):

    # Set the text input to be synthesize
    synthesis_input = texttospeech.types.SynthesisInput(text = answer)
    count = len(str(synthesis_input))/70
    print ("count" + str(count))


    voice = texttospeech.types.VoiceSelectionParams(
            language_code='ko-KR',
            ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    # The response's audio_content is binary.
    with open('output.mp3', 'wb') as out:    ##  사운드 파일로 저장 
    # Write the response to the output file.
            out.write(response.audio_content)
            print('Audio content written to file "output.mp3"')

    #os.system("omxplayer -o alsa output.mp3")
    mixer.init()
    mixer.music.load('output.mp3')
    mixer.music.play(0)
    time.sleep(count)

    print ("SOUND GOOD~~")


def get_hints(language_code):
    if language_code.startswith('en_'):
        return ('turn on the light',
                'turn off the light',
                'blink the light',
                'goodbye')
    return None

def locale_language():
    language, _ = locale.getdefaultlocale()
    return language

def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    logging.info('Initializing for language %s...', args.language)
    hints = get_hints(args.language)
    client = CloudSpeechClient()
    tts_answer("지금부터 말해 주세요.")

    with Board() as board:
        while True:
            print ("지금부터 말하기.")
            text = client.recognize(language_code=args.language,
                                    hint_phrases=hints)
            if text is None:
                logging.info('You said nothing.')
                tts_answer('아무 말도 없네요. ㅠㅠㅠㅠ')

            else :
                print('질문:'+text)
                text = get_answer(text,'jp')

                print('답변:"', text, '"')
                tts_answer(text)


if __name__ == '__main__':
    main()
