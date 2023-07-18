from flask import Flask
from flask import request
from flask import make_response
from flask import send_from_directory
from flask import Response
import re
import os
import json
import logging
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
fileStr = "JWSmall.mp4"
filePrev = fileStr

@app.after_request
def disable_caching(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Expires'] = '-1'
    response.headers['Pragma'] = 'no-cache'
    return response

@app.route('/page/getCurMp4')
def getCurMp4():
    global fileStr
    return json.dumps({'cur':fileStr})

@app.route('/page/files', methods=['POST', 'GET'])
def getSupportedFile():
    fileList = os.listdir("D:/迅雷下载/mp4ToServer")
    mp4List = [file for file in fileList if file.endswith(".mp4")]
    mp4Dict = {}
    mp4Dict['list'] = mp4List
    return json.dumps(mp4Dict)


@app.route('/page/setFile', methods=['POST', 'GET'])
def setMp4File():
    global fileStr
    print(request.get_data())
    fileStr = json.loads(request.get_data())['mp4File']
    return json.dumps("{}")


def get_chunk(byte1=None, byte2=None):
    global fileStr
    # full_path = "JWSmall.mp4"
    file_size = os.stat("D:/迅雷下载/mp4ToServer/"+fileStr).st_size
    start = 0

    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open("D:/迅雷下载/mp4ToServer/"+fileStr, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size


@app.route('/page/video')
def streamVideo():
    global fileStr
    global filePrev
    # if fileStr != filePrev:
    #     filePrev = fileStr
    #     print("stopping loading")
    #     return json.dumps("{}")
    print("loading video: %s"%fileStr)
    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    chunk, start, length, file_size = get_chunk(byte1, byte2)
    resp = Response(chunk, 206, mimetype='video/mp4',
                    content_type='video/mp4', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp


@app.route('/page')
def returnPage():
    return send_from_directory('', 'main.html')


# def count_chunks(fname):
#     count = 0
#     with open(fname, 'rb') as fp:
#         for chunk in chunked_file_reader(fp):
#             count += 1
#     return count

if __name__ == '__main__':
    # print(count_chunks("F:/JohnWick.mp4"))
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.run(host="0.0.0.0", port=8080, threaded=True)
