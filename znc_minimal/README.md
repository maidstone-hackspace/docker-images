docker build -t olymk2/znc .

client buffer plugin has been added, it does not seem to show in the web admin for some reason.

you can use this to try it out

    /msg *status LoadMod clientbuffer


run this to configure your server

    docker run -it --rm -v /etc/znc:/etc/znc olymk2/znc znc --datadir=/etc/znc --makeconf

once configured you can start with the below command using your config file

    docker run -d -p 8000:8000 -v /etc/znc:/etc/znc --name=znc olymk2/znc
