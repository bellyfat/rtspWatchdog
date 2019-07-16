#Lucas Zanella

import rx
from rx import operators as ops
import time

#https://github.com/runtheops/rtsp-rtp/
#from rtspclient import RTSPClient

from camera import Camera

cam = Camera(id = '1',
             name = 'Cam1',
             ip = '192.168.0.103',
             onvif = '10080',
             #rtsp = '10554',
             username = 'admin',
             password = '19929394',
             socks = None
#             socks = {'user': '', 
#                      'password': '', 
#                      'host': '127.0.0.1', 
#                      'port': 1080}
             )

cam.probe_information()
uri = cam.profiles[0].rtsp_uri
rtsp = cam.rtsp_connect(uri)
rtsp.do_describe()
while rtsp.state != 'describe':
    time.sleep(0.1)
    print('sleep')
print('end')
