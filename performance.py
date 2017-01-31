class Performance:
	"""Handles perfomance and timing"""

	def __init__(self):
		import datetime as dt
		self.datetime = dt
		self.enabled = False
		self.profilerStart = 0

	def mark(self, markName):
		if self.enabled:
			marks[markName] = self.datetime.now()
			self.counts[markName] = 0 if markName not in self.counts else self.counts[markName]+1

	def measure(self, measureName, startMarkName=None, endMarkName=None):
		if self.enabled:
			end = marks[endMarkName] if endMarkName and endMarkName in marks else self.datetime.now()
			start = marks[startMarkName] if startMarkName and startMarkName in marks else self.profilerStart
			measures[measureName] = 0 if measureName not in measures else measures[measureName] + (end - start)

	def forEachMeasure(self, cb):
		for key in self.measures:
			cb(key, self.measures[key])

	def enable(self):
		self.counts = dict()
		self.marks = dict()
		self.measures = dict()
		self.enabled = True
		self.profilerStart = self.datetime.now()

	def disable(self):
		self.disabled = False

performance = Performance()