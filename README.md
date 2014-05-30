Build trend
===========

[![Build Status](https://travis-ci.org/ruleant/buildtime-trend.svg)](https://travis-ci.org/ruleant/buildtime-trend)
[![Coverage Status](https://coveralls.io/repos/ruleant/buildtime-trend/badge.png?branch=master)](https://coveralls.io/r/ruleant/buildtime-trend?branch=master)
[![Code Health](https://landscape.io/github/ruleant/buildtime-trend/master/landscape.png)](https://landscape.io/github/ruleant/buildtime-trend/master)
[![status](https://sourcegraph.com/api/repos/github.com/ruleant/buildtime-trend/badges/status.png)](https://sourcegraph.com/github.com/ruleant/buildtime-trend)

Create a trendline of the different stages of a build process

Dependencies
------------

- keen (client for storing build time data as events in keen.io)
- lxml (python wrapper for libxml2 and libxslt)
- matplotlib v1.2.0 or higher (for drawing the trend graph, stackplot is introduced in v1.2.0)

Install using pip :

`pip install keen lxml 'matplotlib>=1.2.0'`

or as a Debian package :

`apt-get install python-lxml python-matplotlib`

Usage
-----

First the timestamp recording needs to be initialised :

`source /path/to/init.sh`

This script will detect the location of the build-trend script folder,
adds it to the PATH and cleans logfiles of previous runs.
Executing the init script with `source` is required to export environment variables to the current shell session.

Because the script dir is added to PATH, no path needs to be added
when logging a timestamp :

`timestamp.sh eventname`

This will log the current timestamp to a file and display it on STDOUT.
Repeat this step as much as needed.

When finished, run 

`analyse.sh`

to analyse the logfile with timestamps and print out the results.
It will calculate the duration between the timestamps and add them to
a file with the analysed data of previous builds.
When Keen.io is enabled, the data will be sent to your Keen.io project for analysis.
When run on Travis CI, it will automatically add build/job related info.

To generate a graph from previous builds, run

`generate_trend.py`

It will take the file with analysed data generated by the analyse script and turn it into a trend graph and saves this graph.

Use the `sync-buildtime-trend-with-gh-pages.sh` script when you run it as part of a Travis CI build. See below for details.

Store build time data in Keen.io
--------------------------------

Next to storing your build time data in xml, it can be sent to Keen.io for storage, analysis and generating graphs.

Follow these steps to enable using Keen.io :

1. [Create a Keen.io account](https://keen.io/signup), if you haven't already done so.
2. [Create a project](https://keen.io/add-project) in you keen.io account.
3. Look up the `project ID` and `Write Key` and assign them to environmental variables : 
- `export KEEN_PROJECT_ID=<Project ID>`
- `export KEEN_WRITE_KEY=<Write Key>`

If these environment variables are set, the scripts will detect this and use Keen.io to store data and do analysis.

Integrate with Travis CI
------------------------

You can integrate Buildtime Trend with your build process on Travis CI :
install and initialise the buildtime trend scripts, add timestamp labels, generate the trend
and synchronise it with your gh-pages branch.

All you need is a github repo, a travis account for your repo and a gh-pages branch to publish the results.

You also need to create an encrypted GH_TOKEN to get write access to your repo (publish results on gh-pages branch) :
- [create](https://github.com/settings/applications) the access token for your github repo, `repo` scope is sufficient
- encrypt the environment variable using the [travis tool](http://docs.travis-ci.com/user/encryption-keys/) :
`travis encrypt GH_TOKEN=github_access_token`
- add the encrypted token to your .travis.yml file (see below)

To enable integration with Keen.io, `KEEN_PROJECT_ID` and `KEEN_WRITE_KEY` should be set (see above):

1. Follow the steps above to create a Keen.io account and project and look up the Project ID
2. Encrypt the project ID using the [travis tool](http://docs.travis-ci.com/user/encryption-keys/) :
`travis encrypt KEEN_PROJECT_ID=<Project ID>` and add it to .travis.yml (see below)
3. For the Write key, the master key of your Keen.io project should be used, because the Write key is too long to encrypt using the Travis encryption tool :
`travis encrypt KEEN_WRITE_KEY=<Master Key>`
 
The generated trend graph and build-data will be put in folder `buildtime-trend` on your `gh-pages` branch.
The trend is available on http://{username}.github.io/{repo_name}/buildtime-trend/trend.png

Example `.travis.yml` file :

    language: python
    env:
      global:
        - secure: # your secure GH_TOKEN goes here (required to share trend on gh-pages)
        - secure: # your secure KEEN_PROJECT_ID goes here (required to store data on Keen.io)
        - secure: # your secure KEEN_WRITE_KEY goes here (required to store data on Keen.io)
    before_install:
      # install and initialise build-trend scripts
      - if [[ -d $HOME/buildtime-trend/.git ]]; then cd $HOME/buildtime-trend; git pull; cd ..; else git clone https://github.com/ruleant/buildtime-trend.git $HOME/buildtime-trend; fi
      # initialise buildtime-trend scripts
      - source $HOME/buildtime-trend/init.sh
    install:
      # generate timestamp with label 'install'
      - timestamp.sh install
      # install buildtime-trend dependencies
      - CFLAGS="-O0" pip install -r ${BUILD_TREND_HOME}/requirements.txt
      # install dependencies
    script:
      # generate timestamp with label 'tests'
      - timestamp.sh tests
      # run your tests
    after_success:
      # generate timestamp with label 'after_success'
      - timestamp.sh after_success
      # after_success scripts
    after_script:
      # synchronise buildtime-trend result with gh-pages
      - sync-buildtime-trend-with-gh-pages.sh

Bugs and feature requests
-------------------------

Please report bugs and add feature requests in the Github [issue tracker](https://github.com/ruleant/buildtime-trend/issues).


License
-------

Copyright (C) 2014 Dieter Adriaenssens <ruleant@users.sourceforge.net>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
