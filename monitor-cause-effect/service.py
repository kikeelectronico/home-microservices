from rules import evaluate_rules as evaluate_rule_set


class MonitorCauseEffectService:

  def __init__(self, homeware, mqtt_client, rules):
    self.homeware = homeware
    self.mqtt_client = mqtt_client
    self.rules = rules
    self.asserted_state = {}

  def evaluate_rules(self):
    evaluate_rule_set(
      self.homeware,
      self.mqtt_client,
      self.rules,
      self.asserted_state
    )
