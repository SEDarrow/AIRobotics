# -*- encoding: UTF-8 -*-

"""
This example shows how to use ALTracker with red ball.
"""

import time
import argparse
from naoqi import ALProxy

IP = "192.168.1.2"
PORT = 9559
targetName = "RedBall" #RedBall or Face. Face sometimes thinks it reached the target as soon as it starts
targetDistanceThreshold = 0.15 #0.15 for RedBall, 1.0 for Face? Could be tweaked

def main(IP, PORT, ballSize, faceSize):
    print "Connecting to", IP, "with port", PORT
    motion = ALProxy("ALMotion", IP, PORT)
    posture = ALProxy("ALRobotPosture", IP, PORT)
    tracker = ALProxy("ALTracker", IP, PORT)
    tts = ALProxy("ALTextToSpeech", IP, PORT)

    # First, wake up.
    motion.wakeUp()

    fractionMaxSpeed = 0.8
    # Go to posture stand
    posture.goToPosture("StandInit", fractionMaxSpeed)

    # Add target to track
    if (targetName == "Face"):
        faceWidth = faceSize
        tracker.registerTarget(targetName, faceWidth)
    else: #RedBall
        diameterOfBall = ballSize
        tracker.registerTarget(targetName, diameterOfBall)

    # set mode
    mode = "Move"
    tracker.setMode(mode)

    # Then, start tracker.
    tracker.track(targetName)
    if (targetName == "Face"):
        tts.say("Tracking people!")
    else:
        tts.say("Tracking red objects")

    print "ALTracker successfully started, now show a red ball to robot!"
    print "Use Ctrl+c to stop this script."

    success = False
    try:
        while True:
            position = tracker.getTargetPosition()
            print "Target position: ", position

            if position:
                if (position[0] < targetDistanceThreshold and position[1] < targetDistanceThreshold):
                    mode = "Head"
                    success = True
                    break
                else: 
                    mode = "Move"
                tracker.setMode(mode)

                lost = tracker.isTargetLost()
                if(lost == True):
                    motion.moveToward(0, 0, -.3)
            else:
                tracker.track(targetName)
                motion.moveToward(0, 0, -.3)
            time.sleep(1)

    except KeyboardInterrupt:
        print
        print "Interrupted by user"
        print "Stopping..."

    if (success == True):
        tts.say("I made it.")
    else:
        tts.say("Unable to reach target.")
    # Stop tracker, go to posture Sit.
    tracker.stopTracker()
    tracker.unregisterAllTargets()    
    tts.say("Stopping")
    posture.goToPosture("Sit", fractionMaxSpeed)
    motion.rest()

    print "ALTracker stopped."


if __name__ == "__main__" :

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default=IP,
                        help="Robot ip address.")
    parser.add_argument("--port", type=int, default=PORT,
                        help="Robot port number.")
    parser.add_argument("--ballsize", type=float, default=0.06,
                        help="Diameter of ball.")
    parser.add_argument("--faceSize", type=float, default=0.2,
                        help="Face width.")

    args = parser.parse_args()

    main(args.ip, args.port, args.ballsize, args.faceSize)