from twisted.internet import protocol
from twisted.internet import reactor
import re

class MyPP(protocol.ProcessProtocol):
    def __init__(self, verses):
        self.verses = verses
        self.data = ""
    def connectionMade(self):
        print("connectionMade!")
        # for i in range(self.verses):
        #     self.transport.write("Aleph-null bottles of beer on the wall,\n" +
        #                          "Aleph-null bottles of beer,\n" +
        #                          "Take one down and pass it around,\n" +
        #                          "Aleph-null bottles of beer on the wall.\n")
        # self.transport.closeStdin() # tell them we're done
    def outReceived(self, data):
        print("outReceived! with %d bytes!" % len(data))
        # self.data = self.data + data
    def errReceived(self, data):
        print("errReceived! with %d bytes!" % len(data))
    def inConnectionLost(self):
        print("inConnectionLost! stdin is closed! (we probably did it)")
    def outConnectionLost(self):
        print("outConnectionLost! The child closed their stdout!")
        # now is the time to examine what they wrote
        #print "I saw them write:", self.data
        # (dummy, lines, words, chars, file) = re.split(r'\s+', self.data)
        # print "I saw %s lines" % lines
    def errConnectionLost(self):
        print("errConnectionLost! The child closed their stderr.")
    def processExited(self, reason):
        print("process exited!")
        reactor.spawnProcess(pp, "wc", ["wc"], {})
        # print("processExited, status %d" % (reason.value.exitCode,))
    def processEnded(self, reason):
        # print "processEnded, status %d" % (reason.value.exitCode,)
        print("quitting")
        # reactor.stop()
# import os, subprocess

cmd = "gst-launch-1.0 udpsrc port=5600 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' \
               ! rtph264depay ! avdec_h264 ! clockoverlay valignment=bottom ! autovideosink fps-update-interval=1000 sync=false".split()

# pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    #    shell=True, preexec_fn=os.setsid)
pp = MyPP(10)
reactor.spawnProcess(pp, "gst-recv", cmd, {})
reactor.run()