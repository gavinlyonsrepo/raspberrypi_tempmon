Version control history:
====================

* Version 1.0-1 020717
	* First version

* Version 1.4-5 290817
	* Code rewritten complete in python3 (from a mixture of bash and python)
	* Graph of realtime CPU data added

* Version 1.5-6 220318
	* Changes to graph modes due to matplotlib upgrade 2.2.2 causing display issues
	* -a data mode and -n notify mode added.

* Version 2.0-1 040418
	* number of graph modes increased to 6 from 2 with menu selection , cli option -G removed
	* csv option added -s which converts log file to csv for third party use.
	* Added CPU,Ram and swap memory usage data
	* mail data now sent as attachment

* Version 2.1-2 210418
	* Epoch unix time added as an alternative to time-date stamp.
	* Graph modes increased from 6 to 12
	* Stress test added with csv file and graph output.
	* Note: old log files from version 1.x.x will no longer work with Version 2,
	  start again with fresh data.

* version 2.2-3 210420
	* For mail mode, replaced ssmtp with msmtp in mail function.
	* ssmtp had to be replaced as apparently ssmtp is deprecated in RPi Buster
	* Users using mail mode option will have to install and configure msmtp.

* version 2.3-4 05-05-2022
	* Added new graph mode option 12 GPU & CPU% & RAM% versus live time
	* Automated creation of config file if missing on startup

* version 2.4-5 12-2023
	* Changed setup.py so it installs RPi.GPIO with pipx tool
	* Fixed GPU data not reporting properly on 64 bit systems

* version 3.0 07-2024
	* Switched from RPi.GPIO to gpiozero so it works on Raspberry Pi 5

* version 3.1.0 03-2026
	* Packaging: migrated from setup.py to pyproject.toml (PEP 517/518)
	* Packaging: renamed PyPI package from rpi-tempmon.py to rpi-tempmon
	* Packaging: matplotlib moved to optional extra, install with pip install rpi-tempmon[graphs]
	* Packaging: added requires-python >= 3.9 constraint
	* Packaging: added lgpio as explicit core dependency for gpiozero pin factory
	* Config: config file restructured from single [MAIN] into [ALARM], [MAIL], [GPIO] sections
	    * Note: existing rpi_tempmon.cfg must be deleted on first run to regenerate in new format
	* Mail: replaced msmtp/mpack system dependencies with Python standard library smtplib
	    * No apt install required for mail mode
	    * Requires Gmail App Password, configured via SMTP_PASSWORD in [MAIL] section
	* Reliability: log rotation added, rotates at 1MB keeping 5 backups
	* Testing: pytest test suite added covering models, config, alarms, sensors, log_writer
	* CI: GitHub Actions workflow added for lint and test on every push
	* CI: pre-commit hook added for pylint on every commit
