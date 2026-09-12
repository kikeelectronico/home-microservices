asserted_state = {}

def evaluateEffect(homeware_value, operator, effect_value):
  match operator:
    case "==":
      return homeware_value == effect_value
    case ">":
      return homeware_value > effect_value

def evaluateRule(homeware, mqtt_client, rule):
  global asserted_state
  homeware_value = homeware.get(rule["device_id"], rule["param"])
  counter_id = f"{rule["device_id"]}/{rule["param"]}/{rule["value"]}"
  if rule["value"] == homeware_value:
    asserted = True
    for effect in rule["effects"]:
      asserted = asserted and evaluateEffect(homeware.get(effect["device_id"], effect["param"]), effect["operator"], effect["value"])
    state = asserted_state.get(counter_id, None)
    if not asserted:
      if state is None:
        asserted_state[counter_id] = 1
      else:
        match state:
          case 0:
            asserted_state[counter_id] = 1
          case 1:
            mqtt_client.publish(f"cause-effect/{counter_id}", "set")
            asserted_state[counter_id] = 2
    else:
      if state is not None and state != 0:
        mqtt_client.publish(f"cause-effect/{counter_id}", "reset")
        asserted_state[counter_id] = 0
  elif rule["reset_value"] == homeware_value:
    state = asserted_state.get(counter_id, None)
    if state is not None and state != 0:
      mqtt_client.publish(f"cause-effect/{counter_id}", "reset")
      asserted_state[counter_id] = 0

def evaluateRules(homeware, mqtt_client, rules):
  for rule in rules:
    evaluateRule(homeware, mqtt_client, rule)