# bgpstreamAlertReader

Python snippet to generate logfile with current BGP hijack information from the live BGPstream
  twitter feed for later processing.

Authentication information needs to be provided by the user in the form of environmental variables:

        export CONSUMER_KEY="xxxxxxxxxxxxxxxxxxxxxxxxx"
        export CONSUMER_SECRET="yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
        export ACCESS_KEY="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        export ACCESS_SECRET="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

Output is in two forms - informational junk to stdout which will report both outages and
  general hijacking info to stdout.  A structured breakdown of hijack data will also be
  provided to "LOGFILE" written to the same directory as $0 is run from.  The form of the
  data will look like:

  2018-11-26T09:24:05.174489,17:23:59,17639,119.28.165.0/24

  current time (clock),hijack time (UTC),offending AS, hijacked netblock

create bgpstream database
table:

