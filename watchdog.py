#!/usr/bin/env python3
#Lucas Zanella

import rx
from rx import operators as ops
import time

#https://github.com/runtheops/rtsp-rtp/
#from rtspclient import RTSPClient

from camera import Camera

import signal,sys,time
def signal_handling(signum,frame):           
    sys.exit()                        

signal.signal(signal.SIGINT,signal_handling) 

QUERY_INTERVAL = 12

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

def list_accumulator(old,new):
    old.append(new)
    return old 

for cam in cams:
    #watchdog = rx.create(cam.watchdog)
    watchdog = rx.subject.Subject()
    
    #buffer_end = rx.(lambda observer, disposable: observer.on_next(None)).pipe(
    buffer_signal = rx.create(lambda observable, d: watchdog.subscribe(observable)).pipe(
        ops.filter(lambda x: x==Camera.COMPLETE_BUFFER)
    )

    stream = rx.create(lambda observable, d: watchdog.subscribe(observable)).pipe(
        ops.buffer_when(lambda: buffer_signal)
    )

    stream.subscribe(
        on_next = lambda i: print(i),
        on_error = lambda e: print("Error Occurred: {0}".format(e)),
        on_completed = lambda: print("--- end of source ---"),
    )

    buffer_signal.subscribe(
        on_next = lambda i: print('//' + i),
        on_error = lambda e: print("Error Occurred: {0}".format(e)),
        on_completed = lambda: print("--- end of source ---"),
    )

    watchdog.on_next(Camera.ONVIF_HEALTHY)
    watchdog.on_next(Camera.RTSP_UNHEALTHY)
    watchdog.on_next(Camera.COMPLETE_BUFFER)
    watchdog.on_next(Camera.ONVIF_HEALTHY)
    watchdog.on_next(Camera.RTSP_UNHEALTHY)
    watchdog.on_next(Camera.COMPLETE_BUFFER)
    watchdog.on_next(Camera.ONVIF_HEALTHY)
    watchdog.on_next(Camera.RTSP_UNHEALTHY)
    watchdog.on_next(Camera.COMPLETE_BUFFER)



while True:
    pass

'''
    #interval = rx.create(lambda observer, disposable: observer.on_next(None)).pipe(
    interval = rx.interval(QUERY_INTERVAL).pipe(
        ops.flat_map(watchdog),
        #ops.scan(list_accumulator, []),
        #ops.buffer_when(lambda: buffer_end)
        #ops.buffer_when(lambda x: Camera.COMPLETE_BUFFER in x)
    )
'''

'''
def cameraObservable(observer):


cam = cams[0]
source = rx.of(cam).pipe(
ops.do_action(lambda x: x.probe_information()),
ops.do_action(lambda cam: cam.rtsp_connect(cam.profiles[0].rtsp_uri)),
ops.do_action(lambda cam
)

source.subscribe(
    on_next = lambda i: print(i),
    on_error = lambda e: print("Error Occurred: {0}".format(e)),
    on_completed = lambda: print("--- end of source ---"),
)
'''
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
