#WIP
import time
import argparse
from naoqi import ALProxy
from naoTest import *
import motion
import Image
import math
import random
IP = "192.168.1.2"
PORT = 9559
RED_THRESHOLD = .5
SENSITIVITY = .5

def filterImageForRedCells(image, imageWidth):
  red = []
  row = 0
  col = 0
  for cell in image:
    if (cell[0] + cell[1] + cell[2]) > 0:
      if (float(cell[0]) / float(cell[0] + cell[1] + cell[2]) > RED_THRESHOLD):
        red.append((row, col))
    
    col += 1
    if col >= imageWidth:
      row += 1
      col = 0  
  return red

def clusterCells(cellCoordinates):
  adjacency = []
  for cell in cellCoordinates:
    found = False
    
    # check surrounding coordinates to see if they
    # are also in the list (so they are the same color)
    for xChange in range(-1, 2):
      if found:
        continue
      for yChange in range(-1, 2):
        if found:
          continue
        x = cell[0] + xChange
        y = cell[1] + yChange
      
        for cluster in adjacency:
          if found:
            continue
          for clusterCell in cluster:
            # if a neighboring cell is already in a cluster, 
            # add the new cell to that cluster
            if x == clusterCell[0] and y == clusterCell[1]:
              found = True
              cluster.append(cell)
              continue
    # if a cell is not in another cluster, start it's own cluster
    if not found:
      adjacency.append([cell]) 
  return adjacency 

def findLargestCluster(clusters):
  maxLength = 0
  maxCluster = []
  for cluster in clusters:
    if len(cluster) > maxLength:
      maxLength = len(cluster)
      maxCluster = cluster 
  return maxCluster

def findClusterCenter(cluster, height, width):
  xTotal = 0
  yTotal = 0
  for cell in cluster:
    xTotal += cell[0]
    yTotal += cell[1]
      
  try:
    center = (yTotal / float(len(cluster)) / float(width), xTotal / float(len(cluster)) / float(height)) 
  except:
    center = (.5, .5)
  return center
      
# Returns the size and position of the largest red item it sees
# Returns it in the form (size, position[x, y])
def getBoxPosition(IP, PORT):
  camProxy = ALProxy("ALVideoDevice", IP, PORT)
  resolution = 8 # 30 x 40 pixels
  colorSpace = 11  # RGB

  # Take a picture
  videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)
  naoImage = camProxy.getImageRemote(videoClient)

  camProxy.unsubscribe(videoClient)
  imageWidth = naoImage[0]
  imageHeight = naoImage[1]
  array = naoImage[6]
  im = Image.fromstring("RGB", (imageWidth, imageHeight), array)
  im = list(im.getdata())
  
  red = filterImageForRedCells(im, imageWidth)
  clusters = clusterCells(red)
  maxCluster = findLargestCluster(clusters)
  
  center = findClusterCenter(maxCluster, imageWidth, imageHeight)
  size = len(maxCluster)
  return (size, center)

def main(IP, PORT, ballSize):
    print "Connecting to", IP, "with port", PORT
    motion = ALProxy("ALMotion", IP, PORT)
    posture = ALProxy("ALRobotPosture", IP, PORT)
    tracker = ALProxy("ALTracker", IP, PORT)

    # First, wake up.
    motion.wakeUp()

    fractionMaxSpeed = 0.8
    # Go to posture stand
    posture.goToPosture("StandInit", fractionMaxSpeed)

    # Add target to track.
    targetName = "RedBall"
    diameterOfBall = ballSize
    tracker.registerTarget(targetName, diameterOfBall)

    # set mode
    mode = "Move"
    tracker.setMode(mode)

    # Then, start tracker.
    tracker.track(targetName)

    print "ALTracker successfully started, now show a red ball to robot!"
    print "Use Ctrl+c to stop this script."

    tracking = True
    stopped = False
    try:
        while True:
            time.sleep(1)
            size, center = getBoxPosition(IP, PORT)

            if size > 200 and tracking:
                tracker.stopTracker()
                tracking = False
            elif size < 200 and not tracking:
                tracker.track(targetName)
                tracking = True

            if size < 20 and not stopped:
                motion.moveToward(0, 0, .3)
            if size > 20 and stopped:
                motion.moveToward(0, 0, 0)

    except KeyboardInterrupt:
        print
        print "Interrupted by user"
        print "Stopping..."

    # Stop tracker, go to posture Sit.
    tracker.stopTracker()
    tracker.unregisterAllTargets()
    posture.goToPosture("Sit", fractionMaxSpeed)
    motion.rest()

    print "ALTracker stopped."


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default=IP,
                        help="Robot ip address.")
    parser.add_argument("--port", type=int, default=PORT,
                        help="Robot port number.")
    parser.add_argument("--ballsize", type=float, default=0.06,
                        help="Diameter of ball.")

    args = parser.parse_args()

    main(args.ip, args.port, args.ballsize)