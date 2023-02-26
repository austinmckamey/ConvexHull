from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.5

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False
		
# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)
		
	def eraseHull(self,polygon):
		self.view.clearLines(polygon)
		
	def showText(self,text):
		self.view.displayStatusText(text)
	

	# This is the method that gets called by the GUI and actually executes
	# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )


		t1 = time.time()
		sorted_points = sorted(points, key= lambda pt: pt.x())
		t2 = time.time()

		t3 = time.time()
		hull = self.recurse_hull(sorted_points, pause, view)
		polygon = [QLineF(hull[i], hull[(i + 1) % len(hull)]) for i in range(len(hull))]
		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

	def recurse_hull( self, points, pause, view):
		l = len(points)
		h = l // 2
		if(l == 1):
			return points
		left = self.recurse_hull(points[:h], pause, view)
		right = self.recurse_hull(points[h:], pause, view)
		hull = self.combine_hull(left, right, pause)
		if pause:
			self.showHull([QLineF(hull[i], hull[(i + 1) % len(hull)]) for i in range(len(hull))], RED)
			self.view.clearLines([QLineF(left[i], left[(i + 1) % len(left)]) for i in range(len(left))])
			self.view.clearLines([QLineF(right[i], right[(i + 1) % len(right)]) for i in range(len(right))])
		return hull

	def combine_hull( self, left, right, pause):

		# clockwise is increasing index, counterclockwise is decreasing
		p = max(left, key=lambda pt: pt.x())
		q = min(right, key=lambda pt: pt.x())

		cp_p = p
		cp_q = q

		prev_p = None
		prev_q = None
		while (True):
			prev_p = p
			prev_q = q
			if pause:
				self.blinkTangent([QLineF(p, q)], BLUE)
			while self.turn_direction(q, p, self.counter_clockwise_point(p, left)) > 0:
				p = self.counter_clockwise_point(p, left)
				if pause:
					self.blinkTangent([QLineF(p, q)], BLUE)
			while self.turn_direction(p, q, self.clockwise_point(q, right)) < 0:
				q = self.clockwise_point(q, right)
				if pause:
					self.blinkTangent([QLineF(p, q)], BLUE)
			if p == prev_p and q == prev_q:
				break
		if pause:
			self.showTangent([QLineF(p, q)], GREEN)
		upper_tan_p = p
		upper_tan_q = q

		prev_cp_p = None
		prev_cp_q = None
		while (True):
			prev_cp_p = cp_p
			prev_cp_q = cp_q
			if pause:
				self.blinkTangent([QLineF(cp_p, cp_q)], BLUE)
			while self.turn_direction(cp_q, cp_p, self.clockwise_point(cp_p, left)) < 0:
				cp_p = self.clockwise_point(cp_p, left)
				if pause:
					self.blinkTangent([QLineF(cp_p, cp_q)], BLUE)
			while self.turn_direction(cp_p, cp_q, self.counter_clockwise_point(cp_q, right)) > 0:
				cp_q = self.counter_clockwise_point(cp_q, right)
				if pause:
					self.blinkTangent([QLineF(cp_p, cp_q)], BLUE)
			if cp_p == prev_cp_p and cp_q == prev_cp_q:
				break
		if pause:
			self.showTangent([QLineF(cp_p, cp_q)], GREEN)
		lower_tan_p = cp_p
		lower_tan_q = cp_q

		result = []

		pt = lower_tan_p
		result.append(lower_tan_p)
		while(True):
			if lower_tan_p == upper_tan_p:
				break
			pt = self.clockwise_point(pt, left)
			if not pt == lower_tan_p:
				result.append(pt)
			if pt == upper_tan_p:
				break

		pt = upper_tan_q
		result.append(upper_tan_q)
		while(True):
			if upper_tan_q == lower_tan_q:
				break
			pt = self.clockwise_point(pt, right)
			if not pt == upper_tan_q:
				result.append(pt)
			if pt == lower_tan_q:
				break

		if pause:
			self.eraseTangent([QLineF(p, q)])
			self.eraseTangent([QLineF(cp_p, cp_q)])
		return result


	# returns 0 if the next point does not turn the line in relation to the origin
	# returns > 0 if the next point turns right
	# returns < 0 if the next point turns left
	def turn_direction(self, pt1, pt2, pt2_next):
		temp1 = QPointF(pt2_next.x() - pt1.x(), pt2_next.y() - pt1.y())
		temp2 = QPointF(pt2.x() - pt1.x(), pt2.y() - pt1.y())
		return temp1.x() * temp2.y() - temp2.x() * temp1.y()

	def clockwise_point(self, pt, points):
		return points[(points.index(pt) + 1) % len(points)]

	def counter_clockwise_point(self, pt, points):
		return points[(points.index(pt) - 1) % len(points)]
