import math
from Data_Converter import Point

class Edge:

    def __init__(self, StartPoint, EdgeNum, origin):

        self.points = []
        self.edgeNum = EdgeNum
        self.startPoint = StartPoint
        self.endPoint = StartPoint
        self.ORIGIN = origin
        self.points.append(StartPoint)
        StartPoint.setEdgeNum(self.edgeNum)

    def addPoint(self, newPoint):
        if isinstance(newPoint, Point):
            self.points.append(newPoint)
            self.endPoint = newPoint
            newPoint.setEdgeNum(self.edgeNum)
        else:
            print("wrong type cannot append", type(newPoint))

    def addPoints(self, newPoints):
        for p in newPoints:
            self.points.append(p)
            self.endPoint = p
            p.setEdgeNum(self.edgeNum)

    def sort(self):
        startSearchFrom = 0
        for i in range(len(self.points)):
            minimum = 360
            location = -1
            for j in range(i, len(self.points)):
                if self.points[j].getAngle() < minimum:
                    minimum = self.points[j].getAngle()
                    location = j
            bufer = self.points[i]
            self.points[i] = self.points[location]
            self.points[location] = bufer
        self.startPoint = self.points[0]
        self.endPoint = self.points[len(self.points)-1]

    def findStartAndEndPoints(self):
        if(len(self.points) > 1):
            self.sort()
            zeroToFirst = self.points[0].getAngle()
            maximum = 0
            location = -1
            for i in range(len(self.points) - 1):
                if(abs(self.points[i + 1].getAngle() - self.points[i].getAngle()) > maximum):
                    maximum = abs(self.points[i + 1].getAngle() - self.points[i].getAngle())
                    location = i
            if((360 - self.points[len(self.points) - 1].getAngle()) + zeroToFirst > maximum):
                self.startPoint = self.points[0]
                self.endPoint = self.points[len(self.points) - 1]
            else:
                self.startPoint = self.points[location]
                self.endPoint = self.points[location + 1]

    def findOutsidePoints(self, pointsToCheck):
        minimums = [self.perpendicularDistance(pointsToCheck[0].getX(), pointsToCheck[0].getY(), self.points[0]),
                    self.perpendicularDistance(pointsToCheck[1].getX(), pointsToCheck[1].getY(), self.points[0]),
                    self.perpendicularDistance(pointsToCheck[2].getX(), pointsToCheck[2].getY(), self.points[0]),
                    self.perpendicularDistance(pointsToCheck[3].getX(), pointsToCheck[3].getY(), self.points[0])]
        result = []
        maximum = 0;
        maximumLocation1 = -1
        maximumLocation2 = -1
        for p in self.points:
            for i in range(len(pointsToCheck)):
                if self.perpendicularDistance(pointsToCheck[i].getX(), pointsToCheck[i].getY(), p) < minimums[i]:
                    minimums[i] = self.perpendicularDistance(pointsToCheck[i].getX(), pointsToCheck[i].getY(), p)
        for i in range(len(pointsToCheck)):
            if minimums[i] > maximum:
                maximum = minimums[i]
                maximumLocation1 = i
        maximum = 0
        for i in range(len(pointsToCheck)):
            if minimums[i] > maximum and i != maximumLocation1:
                maximum = minimums[i]
                maximumLocation2 = i
        result.append(pointsToCheck[maximumLocation1])
        result.append(pointsToCheck[maximumLocation2])
        '''print("This is what \"findOutsidePoints\" we found:")
        for i in range(len(result)):
            result[i].printSelf()
        print("end of  \"findOutsidePoints\" findings.")'''
        return result


    def addEdge(self, otherEdge):
        newPoints = otherEdge.getPoints()
        for i in range(len(newPoints)):
            newPoints[i].setEdgeNum(self.edgeNum)
            self.points.append(newPoints[i])
        self.sort()

    def perpendicularDistance(self, x, y, pointA):
        pocketAngle = abs(self.angle(x, y) - pointA.getAngle())
        pocketDistance = self.distancePP(pointA, self.ORIGIN)
        return abs(pocketDistance * math.sin(math.radians(pocketAngle)))

    def getPoints(self):
        return self.points

    def getEndPoint(self):
        return self.endPoint

    def getStartPoint(self):
        return self.startPoint

    def distancePP(self, pointA, pointB):
        return math.sqrt((pointA.getX() - pointB.getX()) ** 2 + (pointA.getY() - pointB.getY()) ** 2)

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

    def printSelf(self):
        for p in self.points:
            p.printSelf()
        print("Start Point: " )
        self.startPoint.printSelf()
        print("End Point: ")
        self.endPoint.printSelf()
        print("Origin: ")
        self.ORIGIN.printSelf()
        print("Edge Number: " + str(self.edgeNum))


