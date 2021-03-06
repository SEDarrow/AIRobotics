from __future__ import print_function
import sys
import motion
import time
import Image
import math
import random
#from naoqi import ALProxy

#IP = "192.168.1.2"
#PORT = 9559
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
#def getBoxPosition(IP, PORT):
def getBoxPosition():
  #camProxy = ALProxy("ALVideoDevice", IP, PORT)
  camProxy = ALProxy("ALVideoDevice")
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

# Make Nao's head follow a red box
if __name__ == '__main__':
  # Setup for motion
  #motionProxy = ALProxy("ALMotion", IP, PORT)
  #postureProxy = ALProxy("ALRobotPosture", IP, 9559)
  motionProxy = ALProxy("ALMotion")
  motionProxy = ALProxy("ALRobotPosture")
  motionProxy.stiffnessInterpolation("Body", 1.0, 1.0)
  
  yaw = 0
  pitch = 0
  motionProxy.setAngles("HeadYaw", 0, 0.1)
  
  postureProxy.goToPosture("StandInit", 0.5)
  motionProxy.setWalkArmsEnabled(True, True)
  motionProxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])
  X = 0.3 
  Y = 0.0
  Theta = 0.0
  Frequency =0.0 # low speed
  motionProxy.setWalkTargetVelocity(X, Y, Theta, Frequency)
  
  JointNames = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"]
  Arm1 = [-40,  25, 0, -40]
  Arm1 = [ x * motion.TO_RAD for x in Arm1]
  
  Arm2 = [-40,  50, 0, -80]
  Arm2 = [ x * motion.TO_RAD for x in Arm2]
  
  pFractionMaxSpeed = 0.6
  
  motionProxy.angleInterpolationWithSpeed(JointNames, Arm1, pFractionMaxSpeed)
  motionProxy.angleInterpolationWithSpeed(JointNames, Arm2, pFractionMaxSpeed)
  motionProxy.angleInterpolationWithSpeed(JointNames, Arm1, pFractionMaxSpeed)  
      
  while (True):
    X = 0.3  
    #size, center = getBoxPosition(IP, PORT)
    size, center = getBoxPosition()
    print(size)
    
    # Calculate new angle to look at 
    yaw -= (center[0] - .5) * SENSITIVITY
    pitch += (center[1] - .5) * SENSITIVITY
    
    # Make sure values are valid
    if (yaw > 1):
      yaw = 1
    elif (yaw < -1):
      yaw = -1
      
    if (pitch > .5):
      pitch = .5
    elif (pitch < -.5):
      pitch = -.5

    
    # Move head    
    motionProxy.setAngles("HeadYaw", yaw, 0.1)
    motionProxy.setAngles("HeadPitch", pitch, 0.1)  
    
    #if (size > 160):
      #motionProxy.setWalkTargetVelocity(0, Y, 0, Frequency) 
    #else:
      #motionProxy.setWalkTargetVelocity(X, Y, yaw/3, Frequency) 
