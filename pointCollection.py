import math
import Data_Converter
from Data_Converter import Point
import Edge
from Edge import Edge

class pointCollection:

    def __init__(self, margin, points):
        self.points = points
        self.edges = []
        self.origin = Point(0,0,0,0, 0)
        self.margin = margin

    def setNewPoints(self, newPoints):
        self.points = newPoints

    def findDirectionTo(self, dx, dy):
        closestPoints = []
        pathPoints = []
        self.edgeEnds = []
        closestPointsToTangentPaths = []
        selectedWayPoint = None
        self.edges = []
        for i in range(len(self.points)-1,-1,-1):
            if self.distancePP(self.points[i], self.origin) <= self.margin:
                self.points.pop(i)
        #print('0')
        self.findEdges()
        #print('1')
        self.findEndPointsAll()
        #print('2')
        closestPoints = self.findClosestTo(dx, dy)
        #print('3')
        if len(closestPoints) == 0 and self.distanceCP(dx, dy, self.origin) <= self.margin:
            return self.origin
        elif len(closestPoints) == 0:
            return Point(0,0,0,dx, dy)
        #print('5')
        edgeToAvoid = closestPoints[0].getEdgeNum()
        self.edgeEnds = [self.edges[edgeToAvoid].getStartPoint(), self.edges[edgeToAvoid].getEndPoint()]
        pathPoints.append(self.edges[edgeToAvoid].findOutsidePoint(self.findAvoidancePoints(self.edges[edgeToAvoid].getStartPoint())))
        pathPoints.append(self.edges[edgeToAvoid].findOutsidePoint(self.findAvoidancePoints(self.edges[edgeToAvoid].getEndPoint())))
        if(self.distanceCP(dx, dy, pathPoints[0]) < self.distanceCP(dx, dy, pathPoints[1])):
            selectedWayPoint = pathPoints[0]
        else:
            selectedWayPoint = pathPoints[1]
        closestPoint = self.findClosestPoint()
        '''print(self.distancePP(closestPoint, self.origin))'''

        if self.distancePP(closestPoint, self.origin) <= self.margin * 1.5:
            #print("close")
            AngularDiffrence = 0.0
            coefficient = 0.0
            result = 0.0
            length = 5

            AngularDiffrence = selectedWayPoint.getAngle() - ((closestPoint.getAngle() + 180) % 360)
            coefficient = 1 - ((self.distancePP(closestPoint, self.origin) - self.margin) / (self.margin * 0.5))
            if coefficient > 1:
                coefficient = 1

            if AngularDiffrence >= -180 and AngularDiffrence <= 180:
                result = selectedWayPoint.getAngle() - (AngularDiffrence * coefficient)
            if AngularDiffrence > 180:
                result = ((selectedWayPoint.getAngle() + ((360 - AngularDiffrence) * coefficient)) + 360) % 360
            if AngularDiffrence < -180:
                result = ((selectedWayPoint.getAngle() - ((360 + AngularDiffrence) * coefficient)) + 360) % 360

            return Point(0,0,0,math.cos(math.radians(result)) * length, math.sin(math.radians(result)) * length)
        else:
            return selectedWayPoint


    def findAvoidancePoints(self, aPoint):
        result = []
        gamma = (180 + aPoint.getAngle()) % 360
        print("aPoint is:")
        print(aPoint)
        diviationAngle = math.degrees(math.acos((self.margin)/self.distancePP(self.origin, aPoint)))
        angle1 = gamma + diviationAngle
        angle2 = gamma - diviationAngle
        result.append(Point(0,0,0,aPoint.getX() + self.margin * 1.05 * math.cos(math.radians(angle1)), aPoint.getY() + self.margin * 1.05 * math.sin(math.radians(angle1))))
        result.append(Point(0,0,0,aPoint.getX() + self.margin * 1.05 * math.cos(math.radians(angle2)), aPoint.getY() + self.margin * 1.05 * math.sin(math.radians(angle2))))
        return result

    def findEndPointsAll(self):
        for e in self.edges:
            e.findStartAndEndPoints()

    def calculateTangents(self, point):
        result = []
        result.append(Point(0,0,0,self.margin * math.cos(math.radians(((point.getAngle() + 90)%360 + 360) % 360)), self.margin * math.sin(math.radians(((point.getAngle() + 90)%360 + 360) % 360))))
        result.append(Point(0,0,0,self.margin * math.cos(math.radians(((point.getAngle() - 90)%360 + 360) % 360)), self.margin * math.sin(math.radians(((point.getAngle() - 90)%360 + 360) % 360))))
        return result

    def findClosestTo(self, x, y):
        straightLinePathLength = self.distanceCP(x, y, self.origin)
        closestPoints = []
        minimum = 1000.0
        for p in self.points:
            perpendicularDistanceVar = self.perpendicularDistance(x, y, p)
            if self.distancePP(p, self.origin) > straightLinePathLength and self.distanceCP(x, y, p) <= self.margin:
                closestPoints.append(p)
                if minimum > self.distanceCP(x, y, p):
                    bufer = closestPoints[0]
                    closestPoints[0] = closestPoints[len(closestPoints) - 1]
                    closestPoints[len(closestPoints) - 1] = bufer
                    minimum = self.distanceCP(x, y, p)
            elif perpendicularDistanceVar <= self.margin and perpendicularDistanceVar != -1:
                closestPoints.append(p)
                if minimum > self.distanceCP(x, y, p):
                    bufer = closestPoints[0]
                    closestPoints[0] = closestPoints[len(closestPoints) - 1]
                    closestPoints[len(closestPoints) - 1] = bufer
                    minimum = self.distanceCP(x, y, p)
        return closestPoints

    def findClosestToEdge(self, x, y, edgeNum):
        straightLinePathLength = self.distanceCP(x, y, self.origin)
        closestPoints = []
        minimum = 1000.0
        for p in self.edges[edgeNum].getPoints():
            perpendicularDistanceVar = self.perpendicularDistance(x, y, p)
            if self.distancePP(p, self.origin) > straightLinePathLength and self.distanceCP(x, y, p) <= self.margin:
                closestPoints.append(p)
                if minimum > self.distanceCP(x, y, p):
                    bufer = closestPoints[0]
                    closestPoints[0] = closestPoints[len(closestPoints) - 1]
                    closestPoints[len(closestPoints) - 1] = bufer
                    minimum = self.distanceCP(x, y, p)
            elif perpendicularDistanceVar <= self.margin and perpendicularDistanceVar != -1:
                closestPoints.append(p)
                if minimum > self.distanceCP(x, y, p):
                    bufer = closestPoints[0]
                    closestPoints[0] = closestPoints[len(closestPoints) - 1]
                    closestPoints[len(closestPoints) - 1] = bufer
                    minimum = self.distanceCP(x, y, p)
        return closestPoints

    def findEdges(self):
        edgeNum = 0
        pointsCopy = self.points[:]
        print(len(self.points))
        if(len(self.points)==0):
            return
        self.edges.append(Edge(self.points[0], 0, self.origin))
        pointsCopy.pop(0)
        pointsToAdd = self.findPointsAround(pointsCopy, self.points[0])
        '''for p in pointsToAdd:
            print(p)'''
        while len(pointsCopy) > 0:
            '''print("----------------------------------------------------------------------------")
            for p in pointsCopy:
                print(p)'''
            if len(pointsToAdd) > 0:
                self.edges[edgeNum].addPoints(pointsToAdd)
                pointsToAdd = self.findPointsAroundList(pointsCopy, pointsToAdd)
            else:
                edgeNum += 1
                self.edges.append(Edge(pointsCopy[0], edgeNum, self.origin))
                pointsCopy.pop(0)
                pointsToAdd = self.findPointsAround(pointsCopy, self.edges[edgeNum].getStartPoint())
            '''for p in pointsToAdd:
                print(p)'''
        self.edges[edgeNum].addPoints(pointsToAdd)
        '''for e in self.edges:
            print('????????????????????????????????????????????????????')
            print(e)'''

    def findPointsAround(self, array, centerPoint):
        result = []
        for i in range(len(array) - 1, -1, -1):
            if self.distancePP(centerPoint, array[i]) <= self.margin * 2.15 and (centerPoint.getX() != array[i].getX() or centerPoint.getY() != array[i].getY()):
                result.append(array[i])
                array.pop(i)
        return result

    def removeAllTakenPoints(self, arrayToButcher):
        for i in range(len(arrayToButcher) - 1, -1, -1):
            if arrayToButcher[i].getEdgeNum() != -1:
                arrayToButcher.pop(i)

    def findClosestPoint(self):
        minimum = self.distancePP(self.points[0], self.origin)
        closestPoint = self.points[0]
        for p in self.points:
            if self.distancePP(p, self.origin) < minimum:
                closestPoint = p
                minimum = self.distancePP(self.points[0], self.origin)
        return closestPoint

    def getEdgeEnds(self):
        return self.edgeEnds

    def findPointsAroundList(self, array, centerPoints):
        result = []
        for p in centerPoints:
            result.extend(self.findPointsAround(array, p))
        return result
    """
    def extendEdge(self, extendingEdge, newPoints):
        for p in newPoints:
            extendingEdge.addPoint(p)
    """
    def AnyFreePoints(self):
        for p in self.points:
            if p.getEdgeNum() == -1:
                return True
        return False

    def findFreePoint(self):
        for p in self.points:
            if p.getEdgeNum() == -1:
                return p
        return None


    def perpendicularDistance(self, x, y, pointA):
        pocketAngle = ((self.angle(x, y) - pointA.getAngle())%360 + 360) % 360
        if pocketAngle > 90 and pocketAngle < 270:
            return -1
        pocketDistance = self.distancePP(pointA, self.origin)
        return abs(pocketDistance * math.sin(math.radians(pocketAngle)))

    def angle(self, x, y):
        if(x>0.0 and y>=0.0):
            return(math.degrees(math.atan(y/x)))
        if(x>0.0 and y<0.0):
            return(math.degrees(math.atan(y/x))+360)
        if(x<0.0):
            return(math.degrees(math.atan(y/x))+180)
        if(x==0.0):
            if(y<0.0):
                return(270.0)
            if(y>0.0):
                return(90.0)
            if(y == 0.0):
                return(0.0)

    def distancePP(self, pointA, pointB):
        return math.sqrt((pointA.getX() - pointB.getX()) ** 2 + (pointA.getY() - pointB.getY()) ** 2)

    def distanceCP(self, x, y, pointA):
        return math.sqrt((pointA.getX() - x) ** 2 + (pointA.getY() - y) ** 2)

    def distanceCC(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)