import os
import logging
import sys

from constants import ENV_VARS, SERVICE_NAME
from shutdown import wait_for_stop

class Settings():

	_settings = {}

	def load_settings(self):

		# Load enviroment
		self._settings["env"] = os.environ.get("ENV", "dev")

		# Load env file on dev enviroment
		if self._settings["env"] == "dev":
			from dotenv import load_dotenv
			load_dotenv(dotenv_path="../.env")

		# Set service
		self._settings["service_id"] = f"{SERVICE_NAME}-{self._settings["env"]}"

		# Load env vars
		vars_not_set = []
		for var in ENV_VARS:
			env_var = os.environ.get(var, "no_set")
			if env_var != "no_set":
				try:
					env_var = int(env_var)
				except:
					pass
				self._settings[var.lower()] = env_var
			else:
				vars_not_set.append(var)

		if len(vars_not_set) > 0:
			logging.error(f"The following env vas are not set: {", ".join(vars_not_set)}")
			logging.info("Waiting 30 seconds before exiting.")
			wait_for_stop(30)
			logging.info("Exiting program.")
			sys.exit(1)

	def __getattr__(self, name):
		try:
			return self._settings[name]
		except KeyError:
			raise AttributeError(name)