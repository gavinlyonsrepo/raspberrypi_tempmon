Version control history:
====================

* Version 1.0-1 020717
	* First version

* Version 1.1-2 220717
	* CPU Alarm function added

* Version 1.2-3 040817
	* GPIO LED feature added.

* Version 1.3-4 140817
	* Graph of logfile function added.

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
	* Note: old logs files from version 1.x.x will no longer work with Version 2
	start again with fresh data.

* version 2.2-3 210420
	* For mail mode, replaced ssmpt with msmtp in mail function.
	* ssmtp had to be replaced as apparently ssmtp is deprecated in RPi [Buster](https://raspberrypi.stackexchange.com/questions/99968/cannot-send-mail-from-buster), 
	* and is considered obsolete, users where reporting issues via mail.
	* Users using mail mode option will have to install and configure msmtp.
	* Details in Readme. 
	
