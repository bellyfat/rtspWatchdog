#!/usr/bin/env python3
#Lucas Zanella
#Reboots an ONVIF/RTSP camera if RTSP is down. VStarcam cameras suffer from this problem.

import rx
from rx import operators as ops
import time

import signal,sys,time
def signal_handling(signum,frame):           
    sys.exit()                        

signal.signal(signal.SIGINT,signal_handling) 

QUERY_INTERVAL = 38

import datetime

print(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ----------- rtspWatchdog started')

from cameras import cams, Camera

for cam in cams:
    def process_camera_condition(condition):
        if cam.RTSP_UNHEALTHY in condition and cam.ONVIF_HEALTHY in condition:
            cam.log("REBOOTING CAMERA THROUGH ONVIF NOW")
            cam.camera.create_devicemgmt_service()
            cam.camera.devicemgmt.SystemReboot()
        if cam.RTSP_UNHEALTHY in condition and cam.ONVIF_UNHEALTHY in condition:
            cam.log("Both ONVIF and RTSP are down!")
        if cam.RTSP_HEALTHY in condition and cam.ONVIF_UNHEALTHY in condition:
            cam.log("Very strange, RTSP is ok but not ONVIF")

    watchdog = rx.subject.Subject()
    
    buffer_signal = rx.create(lambda observable, _: watchdog.subscribe(observable)).pipe(
        ops.filter(lambda x: x==Camera.COMPLETE_BUFFER)
    )

    stream = rx.create(lambda observable, _: watchdog.subscribe(observable)).pipe(
        ops.buffer_when(lambda: buffer_signal)
    )

    stream.subscribe(
        on_next = lambda i: process_camera_condition(i),
        on_error = lambda e: cam.log(e),
        on_completed = lambda: None,
    )

    buffer_signal.subscribe(
        on_next = lambda i: None,
        on_error = lambda e: cam.log(e),
        on_completed = lambda: None,
    )

    repeater = rx.interval(QUERY_INTERVAL).pipe(
        ops.do_action(lambda x: cam.watchdog(watchdog,None))
    )

    repeater.subscribe(
        on_next = lambda i: None,
        on_error = lambda e: cam.log(e),
        on_completed = lambda: None,
    )


while True:
    pass