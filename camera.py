import sys
sys.path.insert(0, 'python-onvif-zeep/onvif')
sys.path.insert(0, 'python-rtsp-client')
wsdl = 'python-onvif-zeep/wsdl'

from client import *
#Use https://github.com/lucaszanella/python-rtsp-client version, other one has bug
from rtsp import RTSPClient
#import socks
import time
import re
import datetime


class Profile(object):
    pass

class Camera():
    ONVIF_HEALTHY = 'ONVIF OK'
    ONVIF_UNHEALTHY = 'ONVIF ERROR'
    RTSP_HEALTHY = 'RTSP OK'
    RTSP_UNHEALTHY = 'RTSP ERROR'
    RTSP_CONNECTING = 'RTSP CONNECTING'
    ONVIF_CONNECTING = 'ONVIF CONNECTING'
    COMPLETE_BUFFER = 'COMPLETE_BUFFER'
    def __init__(self, id=None, name=None, ip=None, onvif=None, rtsp=None, username=None, password=None, socks=None):
        self.id = id
        self.name = name or ''
        self.ip = ip
        self.onvif = onvif
        self.rtsp = rtsp
        self.username = username
        self.password = password
        self.rtsp_uri = None
        self.profiles = []
        self.socks_transport = None
        self.socks = False
        if socks:
            self.socks = True
            self.socks_user = socks['user'] or ''
            self.socks_password = socks['password'] or ''
            self.socks_host = socks['host']
            self.socks_port = socks['port'] or 1080

            proxies = {
                'http': 'socks5://' + self.socks_user + ':' + self.socks_password + '@' + self.socks_host + ':' + str(self.socks_port),
                'https': 'socks5://' + self.socks_user + ':' + self.socks_password + '@' + self.socks_host + ':' + str(self.socks_port)
            }

            self.socks_transport = CustomTransport(timeout=10, proxies=proxies)
        self.camera = ONVIFCamera(self.ip, 
                            self.onvif,
                            self.username, 
                            self.password,
                            wsdl, 
                            transport=self.socks_transport
                            )
    def watchdog(self, observer, disposable):
        #TODO: add a try here and if fail pass observer error
        observer.on_next(self.ONVIF_CONNECTING)
        self.probe_information()
        observer.on_next(self.ONVIF_HEALTHY)
        uri = self.profiles[0].rtsp_uri
        observer.on_next(self.RTSP_CONNECTING)
        rtsp = self.rtsp_connect(uri)
        rtsp.do_describe()
        i = 0
        #print("watchdog whle begin")

        while rtsp.state != 'describe':
            time.sleep(0.1)
            i+=1
            if i==5*10:
                break
        if rtsp.state != 'describe':
            observer.on_next(self.RTSP_UNHEALTHY)
        else:
            observer.on_next(self.RTSP_HEALTHY)
        observer.on_next(self.COMPLETE_BUFFER)
        #print("COMPLETE_BUFFER emitted")

    def log(self, info):
        socks_info = ''
        if self.socks_transport: socks_info = ', socks://' + self.socks_host + ":" + str(self.socks_port)
        print(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ', Camera ' + self.name + ', id: ' + str(self.id) + ', ' + self.ip + ':' + self.onvif + socks_info + ": " + str(info))

#Just to see things
    def probe_information(self):
        #self.log('loading information...')
        
        mycam = ONVIFCamera(self.ip, 
                            self.onvif,
                            self.username, 
                            self.password,
                            wsdl, 
                            transport=self.socks_transport
                            )
        #self.log('getting capabilities...')
        resp = mycam.devicemgmt.GetCapabilities()
        if resp["Imaging"]:
            #self.log('supports imaging services')
            #self.imaging_url = resp["Imaging"]["XAddr"]
            pass
        if resp["Media"]:
            #self.log('supports media services')
            #self.log('querying media services...')
            media_service = mycam.create_media_service()
            #self.log('querying profiles...')
            profiles = media_service.GetProfiles()
            for profile in profiles:
                p = Profile()
                p.name = profile.Name
                p.token = profile.token
                p.encoding = profile.VideoEncoderConfiguration.Encoding
                p.resolution_W = profile.VideoEncoderConfiguration.Resolution.Width
                p.resolution_H = profile.VideoEncoderConfiguration.Resolution.Height
                p.quality = profile.VideoEncoderConfiguration.Quality
                p.framerate_limit = profile.VideoEncoderConfiguration.RateControl.FrameRateLimit
                p.encoding_interval = profile.VideoEncoderConfiguration.RateControl.EncodingInterval
                p.bitrate_limit = profile.VideoEncoderConfiguration.RateControl.BitrateLimit
                self.profiles.append(p)

            for profile in self.profiles:
                #self.log('getting system uri for profile ' + profile.name + " ...")
                params = mycam.devicemgmt.create_type('GetSystemUris')
                resp = mycam.media.GetStreamUri({'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}}, 'ProfileToken': profile.token})
                if resp['Uri']:
                    profile.rtsp_uri = resp['Uri']
                    profile.InvalidAfterConnect = resp['InvalidAfterConnect']
                    profile.InvalidAfterReboot = resp['InvalidAfterReboot']
                    profile.Timeout = resp['Timeout']

    def choose_transport(self, rtsp_body):
        #self.log('rtsp body: ')
        #self.log(rtsp_body)
        m = re.findall(r'm=.+', rtsp_body)
        a = re.findall(r'a=.+', rtsp_body)
        m_video = [i.replace('m=', '') for i in m if 'video' in i.lower()]
        m_audio = [i.replace('m=', '') for i in m if 'audio' in i.lower()]
        #print('m_video: ' + str(m_video))
        #print('m_audio: ' + str(m_audio))
        #for video in m_video:
            #print(video.split(' '))
        chosen_video = m_video[0].split(' ')
        chosen_video_port = chosen_video[1]
        chosen_video_protocol = chosen_video[2]
        chosen_video_fmt = chosen_video[3]    
        chosen_audio = m_audio[0].split(' ')
        chosen_audio_port = chosen_audio[1]
        chosen_audio_protocol = chosen_audio[2]    
        #print('chosen_video_protocol: ' + chosen_video_protocol)
        #print('chosen_video_port: ' + chosen_video_port)
        #print('chosen_video_fmt: ' + chosen_video_fmt)
        return ['rtp_avp_tcp']
        #print(re.findall(r'm=.+', rtsp_body))
        #print('decide between these: ' + rtsp_body())

    def rtsp_uri_ensure_username(self, uri):
        if '@' not in uri: #Simple test. Does it cover all cases?
            return uri.replace('rtsp://', 'rtsp://' + self.username + ":" + self.password + '@')

    def rtsp_connect(self, uri):
        #self.log('rtsp connection to uri ' + uri)
        RTSP_timeout = 10
        uri = self.rtsp_uri_ensure_username(uri)
        #uri = self.rtsp_uri#.replace('554\/11', '10554')
        #self.log('opening RTSP connection to url ' + uri + ' ...')
        callback = lambda x: self.log('\n' + x) 
        sock = None
        if self.socks:
            sock = socks.socksocket() # Same API as socket.socket in the standard lib
            #The true is for remote dns resolution
            sock.set_proxy(socks.SOCKS5, self.socks_host, self.socks_port, True, self.socks_user, self.socks_password) # (socks.SOCKS5, "localhost", 1234)

        myrtsp = RTSPClient(url=uri, callback=None, socks=None)#, timeout=RTSP_timeout)
        return myrtsp
'''
        try:
            myrtsp.do_describe()
            while myrtsp.state != 'describe':
                time.sleep(0.1)
            myrtsp.do_setup('track0')
            while myrtsp.state != 'setup':
                time.sleep(0.1)
            #Open socket to capture frames here
            myrtsp.do_play(myrtsp.cur_range, myrtsp.cur_scale)
        except Exception as e:
            print('EXCEPTION ------------------------------')
            print(e)
            myrtsp.do_teardown()
        #return camera
'''