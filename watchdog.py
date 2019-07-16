#Lucas Zanella

import rx
from rx import operators as ops
import time

#https://github.com/runtheops/rtsp-rtp/
#from rtspclient import RTSPClient

from camera import Camera
cams = []
cams.append(Camera(id = '1',
             name = 'Cam1',
             ip = '192.168.0.103',
             onvif = '10080',
             #rtsp = '10554',
             username = 'admin',
             password = '19929394',
             socks = None
             ))

cam = cams[0]
source = rx.of(cam).pipe(
ops.do_action(lambda x: x.probe_information()),
ops.do_action(lambda cam: cam.rtsp_connect(cam.profiles[0].rtsp_uri))
)

source.subscribe(
    on_next = lambda i: print(i),
    on_error = lambda e: print("Error Occurred: {0}".format(e)),
    on_completed = lambda: print("Done!"),
)

'''
for cam in cams:
    cam.probe_information()
    uri = cam.profiles[0].rtsp_uri
    rtsp = cam.rtsp_connect(uri)
    rtsp.do_describe()
    while rtsp.state != 'describe':
        time.sleep(0.1)
        print('sleep')
print('end')
'''
