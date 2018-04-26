"""
This example shows how to use ALTracker with red objects and faces.
"""

import time
import argparse
from naoqi import ALProxy


def determineState(motion, tracker, targetDistanceThreshold):
    success = False
    position = tracker.getTargetPosition()
    print "Target position: ", position    # Print distance from target
    # If Nao has found a target
    if position:
        # If Nao is close enough, stop moving and exit loop
        if (position[0] < targetDistanceThreshold and position[1] < targetDistanceThreshold):
            success = targetReached(tracker)   # Sets success to true, stops moving
        # Otherwise, keep following
        else:
            following(tracker)
        # If Nao loses the target, rotate in place
        lost = tracker.isTargetLost()
        if lost is True:
            targetLost(motion)
    # If Nao hasn't found a target yet, keep looking while rotating in place
    else:
        findTarget(motion, tracker)
    return success


def findTarget(motion, tracker):
    tracker.track(targetType)
    motion.moveToward(0, 0, -.3)
    return


def targetReached(tracker):
    # Head mode tracks using only the head
    tracker.setMode("Head")
    success = True
    return success


def following(tracker):
    # Move mode tracks with head and follows
    tracker.setMode("Move")
    return


def targetLost(motion):
    motion.moveToward(0, 0, -.3)
    return


def setTargetParameters(targetType, tts):
    # Set parameters and announce tracking type, values should probably be adjusted
    if (targetType == "RedBall"):
        targetSize = 0.06   # Diameter of ball. Default 0.06
        targetDistanceThreshold = 0.15
        tts.say("Tracking red objects")
    elif (targetType == "Face"):
        targetSize = 0.2    # Width of face. Default is 0.1
        targetDistanceThreshold = 1.0
        tts.say("Tracking people")
    else:
        raise NameError('Invalid Target Type')
    return targetSize, targetDistanceThreshold


def main(IP, PORT, targetType):
    print "Connecting to", IP, "with port", PORT
    motion = ALProxy("ALMotion", IP, PORT)
    posture = ALProxy("ALRobotPosture", IP, PORT)
    tracker = ALProxy("ALTracker", IP, PORT)
    tts = ALProxy("ALTextToSpeech", IP, PORT)

    # First, wake up.
    motion.wakeUp()
    motion.setFallManagerEnabled(True)

    # Go to posture stand
    fractionMaxSpeed = 0.8
    posture.goToPosture("StandInit", fractionMaxSpeed)

    # Set target parameters
    targetParameters = setTargetParameters(targetType, tts)
    targetSize = targetParameters[0]
    targetDistanceThreshold = targetParameters[1]

    # Add target to track
    tracker.registerTarget(targetType, targetSize)

    # Has Nao reached the target
    #success = False

    print "ALTracker successfully started, now show a target to robot!"
    print "Use Ctrl+c to stop this script."

    try:
        while True:
            success = determineState(motion, tracker, targetDistanceThreshold)
            if success is True:
                tts.say("I made it.")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        print
        print "Interrupted by user"
        print "Stopping..."

    if success is False:
        tts.say("Unable to reach target.")
    # Stop tracker, go to posture Sit.
    tracker.stopTracker()
    tracker.unregisterAllTargets()
    tts.say("Stopping")
    posture.goToPosture("Crouch", fractionMaxSpeed)
    motion.rest()

    print "ALTracker stopped."


if __name__ == "__main__":

    IP = "192.168.1.153"  # 192.168.1.2, 192.168.1.153
    PORT = 9559
    targetType = "RedBall"  # RedBall or Face

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default=IP,
                        help="Robot ip address.")
    parser.add_argument("--port", type=int, default=PORT,
                        help="Robot port number.")
    parser.add_argument("--targettype", type=str, default=targetType,
                        help="Type of target to track.")

    args = parser.parse_args()
    main(args.ip, args.port, args.targettype)
