# rtspWatchdog

Reboots an ONVIF/RTSP camera if RTSP is down. VStarcam cameras suffer from this problem.

# Usage

```
git clone https://github.com/lucaszanella/rtspWatchdog
cd dev
sudo docker build -t rtspwatchdog .
sudo docker run -v $(pwd)/..:/home --restart unless-stopped rtspwatchdog
```