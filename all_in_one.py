"""
This example shows how to use ALTracker with red objects and faces.
"""

import time
import argparse
from naoqi import ALProxy

IP = "192.168.1.2"
PORT = 9559

# Variables, values could be tweaked
targetName = "RedBall" #RedBall or Face.

# Set targetSize according to target type
if (targetName == "RedBall"):
    targetSize = 0.06   # Diameter of ball. Default value 0.06.
elif (targetName == "Face"):
    targetSize = 0.2    # Width of face. Default value 0.1.
else:
    raise NameError('Invalid Target Name')

# Set targetDistanceThreshold according to target type
if (targetName == "RedBall"):
    targetDistanceThreshold = 0.15 
elif (targetName == "Face"):
    targetDistanceThreshold = 1.0

def main(IP, PORT):
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
    tracker.registerTarget(targetName, targetSize)

    # set mode
    mode = "Move"
    tracker.setMode(mode)

    # Then, start tracker.
    tracker.track(targetName)
    if (targetName == "RedBall"):
        tts.say("Tracking red objects")
    elif (targetName == "Face"):
        tts.say("Tracking people")

    print "ALTracker successfully started, now show a target to robot!"
    print "Use Ctrl+c to stop this script."

    success = False # Has Nao reached the target
    try:
        while True:
            position = tracker.getTargetPosition()
            print "Target position: ", position     # Print distance from target

            # If Nao has found a target
            if position:
                # If Nao is close enough, stop moving and exit loop
                if (position[0] < targetDistanceThreshold and position[1] < targetDistanceThreshold):
                    mode = "Head"
                    success = True
                    break
                # Otherwise, keep following
                else: 
                    mode = "Move"
                tracker.setMode(mode)

                # If Nao loses the target, rotate in place
                lost = tracker.isTargetLost()
                if(lost == True):
                    motion.moveToward(0, 0, -.3)

            # If Nao hasn't found a target yet, keep looking while rotating in place
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
    '''
    parser.add_argument("--ballsize", type=float, default=0.06,
                        help="Diameter of ball.")
    parser.add_argument("--faceSize", type=float, default=0.2,
                        help="Face width.")'''

    args = parser.parse_args()

    #main(args.ip, args.port, args.ballsize, args.faceSize)
    main(args.ip, args.port)