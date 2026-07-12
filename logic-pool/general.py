# Do several task when leaving and arriving at home
def atHome(homeware, topic, payload):
  if topic == "device/switch_at_home/on":
    if payload:
      homeware.execute("switch_prepare_home", "on", False)