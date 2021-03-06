# vim: set expandtab sw=4 ts=4:
"""
Gather build related data.

Copyright (C) 2014-2016 Dieter Adriaenssens <ruleant@users.sourceforge.net>

This file is part of buildtimetrend/python-lib
<https://github.com/buildtimetrend/python-lib/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import copy
from lxml import etree
from buildtimetrend import logger
from buildtimetrend.settings import Settings
from buildtimetrend.stages import Stages
from buildtimetrend.collection import Collection
from buildtimetrend.tools import split_isotimestamp


class BuildJob(object):

    """Gather build job related data."""

    def __init__(self, csv_filename=None, end_timestamp=None):
        """Initialize instance."""
        self.properties = Collection()
        self.stages = Stages()
        if end_timestamp is not None:
            self.stages.set_end_timestamp(end_timestamp)
        if csv_filename is not None:
            self.stages.read_csv(csv_filename)

    def add_stages(self, stages):
        """
        Add a Stages instance.

        Parameters :
        - stages : Stages instance
        """
        if isinstance(stages, Stages):
            self.stages = stages

    def add_stage(self, stage):
        """
        Add a Stage instance.

        Parameters :
        - stage : Stage instance
        """
        self.stages.add_stage(stage)

    def add_property(self, name, value):
        """
        Add a build property.

        Parameters :
        - name : Property name
        - value : Property value
        """
        self.properties.add_item(name, value)

    def get_property(self, name):
        """
        Get a build property value.

        Parameters :
        - name : Property name
        """
        return self.properties.get_item(name)

    def get_properties(self):
        """Return build properties."""
        # copy values of properties
        data = self.properties.get_items()

        # add total duration
        # use total stage duration if it is defined
        # else, calculate duration from stage duration
        if "duration" not in data:
            data["duration"] = self.stages.total_duration()

        # add started_at of first stage if it is defined
        # and if it is not set in properties
        if self.stages.started_at is not None and "started_at" not in data:
            data["started_at"] = self.stages.started_at

        # add finished_at of last stage if it is defined
        # and if it is not set in properties
        if self.stages.finished_at is not None and "finished_at" not in data:
            data["finished_at"] = self.stages.finished_at

        return data

    def set_started_at(self, isotimestamp):
        """
        Set timestamp when build started.

        Parameters :
        - isotimestamp : timestamp in iso format when build started
        """
        try:
            self.add_property("started_at", split_isotimestamp(isotimestamp))
        except (TypeError, ValueError) as msg:
            logger.warning(
                "isotimestamp expected when setting started_at : %s", msg
            )

    def set_finished_at(self, isotimestamp):
        """
        Set timestamp when build finished.

        Parameters :
        - isotimestamp : timestamp in iso format when build started
        """
        try:
            self.add_property("finished_at", split_isotimestamp(isotimestamp))
        except (TypeError, ValueError) as msg:
            logger.warning(
                "isotimestamp expected when setting finished_at : %s", msg
            )

    def load_properties_from_settings(self):
        """Load build properties from settings."""
        self.load_property_from_settings("build")
        self.load_property_from_settings("job")
        self.load_property_from_settings("branch")
        self.load_property_from_settings("ci_platform")
        self.load_property_from_settings("build_trigger")
        self.load_property_from_settings("pull_request")
        self.load_property_from_settings("result")
        self.load_property_from_settings("build_matrix")
        self.add_property("repo", Settings().get_project_name())

    def load_property_from_settings(self, property_name, setting_name=None):
        """
        Load the value of a setting and set it as a build property.

        Parameters
        - property_name : name of the build property
        - setting_name : name of the setting (takes property_name if not set)
        """
        if setting_name is None:
            setting_name = property_name

        value = Settings().get_setting(setting_name)

        if value is not None:
            self.add_property(property_name, value)

    def to_dict(self):
        """Return object as dictionary."""
        # get build properties
        data = self.get_properties()

        # add stages
        if isinstance(self.stages, Stages):
            data["stages"] = self.stages.stages

        return data

    def stages_to_list(self):
        """Return list of stages, all containing the build properties."""
        if isinstance(self.stages, Stages):
            # create list to be returned
            data = []

            # get build properties
            build_properties = self.get_properties()

            # iterate all stages
            for stage in self.stages.stages:
                temp = {}
                # copy stage data
                temp["stage"] = copy.deepcopy(stage)
                # copy values of properties
                # check if collection is empty
                if build_properties:
                    temp["job"] = build_properties
                data.append(temp)

        return data

    def to_xml(self):
        """Generate XML object of a BuildJob instance."""
        root = etree.Element("build")

        # add properties
        for key in self.properties.get_items():
            root.set(str(key), str(self.properties.get_item(key)))

        # add stages
        if isinstance(self.stages, Stages):
            root.append(self.stages.to_xml())

        return root

    def to_xml_string(self):
        """Generate XML string of a BuildJob instance."""
        return etree.tostring(self.to_xml(), pretty_print=True)
