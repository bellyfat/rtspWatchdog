#Lucas Zanella

import rx
from rx import operators as ops

#https://github.com/runtheops/rtsp-rtp/
#from rtspclient import RTSPClient

from camera import Camera

cam = Camera(id = '1',
             name = 'Cam1',
             ip = '192.168.0.101',
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
