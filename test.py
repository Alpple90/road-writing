import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString, Point
import scipy.interpolate as spInterp

"""
.OSM files are JOSM files. They're a type of XML file. In this case we will be parsing Lanelet2 OSM files.
A Lanelet2 OSM file is a OSM file that has been converted using Lanelet2. The one issue is Lanelet2 requries a linux OS to run.
In theory a normal JOSM file could be used, but the following code would need to be modified.

Node contains point information, e.g. Longitude and Latitude, elvation, etc.
Way are a list of nodes. They represent a list of points along a road.
Realtion contain two ways, the left and right way. They represent the middle and one edge of a road. 
A road will have two relations, one for the left lane and one for the right lane.
"""

"""
Method to resample a list of (x,y) coordinates to a specific interval. 
Maps i have found either do not have evenely spread out points or contain too many points.
This allows me to replciate raised pavemnt markers more accurately.
This method does not provide full control over point placement. It will place points at the start and end of the line, then evenly space points in between. 
"""
def getNodes(root):
    nodes = {}
    
    for node in root.findall('node'):
        x = None
        y = None
        
        nodeID = node.get('id')
        for tag in node.findall('tag'):
            if tag.get('k') == 'local_x':
                x = float(tag.get('v'))
                
            if tag.get('k') == 'local_y':
                y = float(tag.get('v'))
                
        if x is not None and y is not None:
            nodes[nodeID] = (x, y)
    
    return nodes

def getWays(root, nodeDict):
    ways = {}
    
    for way in root.findall('way'):
        nodeList = []
        wayID = way.get('id')
        
        for node in way.findall('nd'):
            if node.get('ref') in nodeDict:
                nodeList.append(nodeDict[node.get('ref')])
                
        ways[wayID] = nodeList
        
    return ways

    
def getLanelets(root, wayDict):
    lanelets = {}
    
    for rel in root.findall('relation'):
        relTags = {tag.get('k'): tag.get('v') for tag in rel.findall('tag')}
        
        if relTags.get('type') == 'lanelet':
            leftWay = None
            rightWay = None
            
            relID = rel.get('id')
            
            for member in rel.findall('member'):
                if member.get('role') == 'left':
                    leftWay = member.get('ref')
                    
                if member.get('role') == 'right':
                    rightWay = member.get('ref')
                    
            if leftWay in wayDict and rightWay in wayDict:
                lanelets[relID] = (wayDict[leftWay], wayDict[rightWay])
                # this dictionary is a tuple that contains two lists of tuples
                # ([(x, y), (x, y)], [(x, y), (x, y)])
                
    return lanelets


def combineWays(laneletDict):
    StartNodes = {}
    EndNodes = {}
    inverseStart = {}
    inverseEnd = {}

    for key, way in laneletDict.items():
        leftWay = way[0]
        StartNodes[key] = leftWay[0]
        EndNodes[key] = leftWay[-1]
        inverseStart[leftWay[0]] = key
        inverseEnd[leftWay[-1]] = key

    startRef = None
    for key in StartNodes:
        if StartNodes[key] not in inverseEnd:
            startRef = key
            break

    if startRef is None:
        startRef = next(iter(laneletDict))

    orderedKeys = []
    currentRef = startRef
    visited = set()

    while currentRef is not None and currentRef not in visited:
        orderedKeys.append(currentRef)
        visited.add(currentRef)
        currentEnd = EndNodes[currentRef]
        currentRef = inverseStart.get(currentEnd, None)

    leftWays = []
    rightWays = []
    for ref in orderedKeys:
        leftWays.extend(laneletDict[ref][0])
        rightWays.extend(laneletDict[ref][1])
        
    return leftWays, rightWays

# can only pass through ways, dictionary needs to been ploted in a for loop which is the plotLaneletDict method.
def getLeftRightXY(left, right):
    leftWay, rightWay = left, right
    
    lx = [node[0] for node in leftWay]
    ly = [node[1] for node in leftWay]
    rx = [node[0] for node in rightWay]
    ry = [node[1] for node in rightWay]
    
    return lx, ly, rx, ry 

def calCenterline(leftWay, rightWay, interval=0.5):
    leftLine  = LineString(leftWay)
    rightLine = LineString(rightWay)

    # Use longer line so we dont miss any points.
    if leftLine.length >= rightLine.length:
        sampleLine, otherLine = leftLine, rightLine
    else:
        sampleLine, otherLine = rightLine, leftLine

    # Ensure num_pts is not empty.
    num_pts = max(2, int(sampleLine.length / interval))
    distances  = np.linspace(0, sampleLine.length, num_pts)

    center_pts = []
    for d in distances:
        pt_a = sampleLine.interpolate(d)
        # Nearest point on the opposite boundary — correct on curves
        pt_b = otherLine.interpolate(otherLine.project(pt_a))
        center_pts.append(((pt_a.x + pt_b.x) / 2, (pt_a.y + pt_b.y) / 2))

    # Numpy array to easily split tuple.
    center = np.array(center_pts)
    return center[:, 0], center[:, 1]

def resample(laneDict, interval):
    leftWay = laneDict
    
    if len(leftWay) < 2:
        return leftWay
    
    # Create a Line from the coordinates, then calculate the length of said line. Lanlet2 Local_x and Local_y are in meters. 
    line = LineString(leftWay)
    length = line.length
    
    # If the length is 0, return the original list.
    if length == 0:
        return leftWay
    
    # Create an array of value from 0 until 'lenght' with an interval of 'interval'. Arange does not include the end value so will need to add later.
    intArray = np.arange(0, length, interval)
    
    # Interpolate points along the line at the specified distances. 
    points = [line.interpolate(d) for d in intArray]
    
    # Add endpoint of the line
    points.append(line.interpolate(length))
    return [(p.x, p.y) for p in points]