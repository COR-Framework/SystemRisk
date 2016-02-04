from cor.api import Message, CORModule
import datetime


class Risk:
	def __init__(self, time, staticweight):
		super().__init__()
		self.time = time
		self.staticweight = staticweight


class SystemRisk(CORModule):

	def compute_risk(self, host):
		total_risk = 0

		ctime = datetime.datetime.now()
		for risk in self.recent_risks[host]:
			if (risk.time + self.longterm) < ctime:
				self.recent_risks[host].remove(risk)

		for risk in self.recent_risks[host]:
			dweight = 1 - (ctime - risk.time) / self.longterm
			weight = dweight * risk.staticweight
			total_risk += weight

		return total_risk

	def receiver(self, message):
		try:
			host = message.payload["host"]
			timestamp = message.payload["timestamp"]
			staticweight = message.payload["weight"]
			messagetime = datetime.datetime.fromtimestamp(timestamp)
			if host in self.recent_risks:
				self.recent_risks[host].append(Risk(messagetime, staticweight))
			else:
				self.recent_risks[host] = [Risk(messagetime, staticweight)]
			total_risk = self.compute_risk(host)
			self.messageout(Message("SYSTEMRISK", {"host": host, "timestamp": timestamp, "risk": total_risk}))
		except KeyError:
			print("Message did not conform to required protocol " + str(message))

	def __init__(self, network_adapter=None, days="7", *args, **kwargs):
		super().__init__(network_adapter, *args, **kwargs)
		self.recent_risks = {} # map host -> [time]
		self.longterm = datetime.timedelta(days=days)