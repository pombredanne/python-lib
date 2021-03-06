# vim: set expandtab sw=4 ts=4:
#
# Unit tests for BuildJob class
#
# Copyright (C) 2014-2016 Dieter Adriaenssens <ruleant@users.sourceforge.net>
#
# This file is part of buildtimetrend/python-lib
# <https://github.com/buildtimetrend/python-lib/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import buildtimetrend
from buildtimetrend.settings import Settings
from buildtimetrend.buildjob import BuildJob
from buildtimetrend.stages import Stage
from buildtimetrend.stages import Stages
from formencode.doctest_xml_compare import xml_compare
from buildtimetrend.test import constants
from lxml import etree
import unittest


class TestBuildJob(unittest.TestCase):

    """Unit tests for BuildJob class"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixture."""
        # show full diff in case of assert mismatch
        cls.maxDiff = None

    def setUp(self):
        """Initialise test environment before each test."""
        self.build = BuildJob()
        # reinitialise settings
        Settings().__init__()

    def test_novalue(self):
        """Test freshly initialised Buildjob object."""
        # number of stages should be zero
        self.assertEqual(0, len(self.build.stages.stages))
        self.assertEqual(0, self.build.properties.get_size())

        # get properties should return zero duration
        self.assertDictEqual({'duration': 0}, self.build.get_properties())

        # dict should be empty
        self.assertDictEqual(
            {'duration': 0, 'stages': []},
            self.build.to_dict()
        )

        # list should be empty
        self.assertListEqual([], self.build.stages_to_list())

        # xml shouldn't contain items
        self.assertEqual(
            b'<build><stages/></build>', etree.tostring(self.build.to_xml()))
        self.assertEqual(
            b'<build>\n'
            b'  <stages/>\n'
            b'</build>\n', self.build.to_xml_string())

    def test_nofile(self):
        """Test creating BuildJob instance with invalid filename."""
        # number of stages should be zero when file doesn't exist
        self.build = BuildJob('nofile.csv')
        self.assertEqual(0, len(self.build.stages.stages))

        self.build = BuildJob('')
        self.assertEqual(0, len(self.build.stages.stages))

    def test_end_timestamp(self):
        """Test setting end timestamp"""
        self.assertEqual(0, self.build.stages.end_timestamp)

        self.build = BuildJob('', 123)
        self.assertEqual(123, self.build.stages.end_timestamp)

    def test_set_started_at(self):
        """Test setting started_at timestamp"""
        self.assertEqual(None, self.build.properties.get_item("started_at"))

        self.build.set_started_at(None)
        self.assertEqual(None, self.build.properties.get_item("started_at"))

        # set as int, isotimestamp string expected
        self.build.set_started_at(constants.TIMESTAMP_STARTED)
        self.assertEqual(None, self.build.properties.get_item("started_at"))

        # set as isotimestamp string
        self.build.set_started_at(constants.ISOTIMESTAMP_STARTED)
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_STARTED,
            self.build.properties.get_item("started_at")
        )

    def test_set_finished_at(self):
        """Test setting finished_at timestamp"""
        self.assertEqual(None, self.build.properties.get_item("finished_at"))

        self.build.set_finished_at(None)
        self.assertEqual(None, self.build.properties.get_item("finished_at"))

        # set as int, isotimestamp string expected
        self.build.set_finished_at(constants.TIMESTAMP_FINISHED)
        self.assertEqual(None, self.build.properties.get_item("finished_at"))

        # set as isotimestamp string
        self.build.set_finished_at(constants.ISOTIMESTAMP_FINISHED)
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_FINISHED,
            self.build.properties.get_item("finished_at")
        )

    def test_add_stages(self):
        """Test adding stages"""
        self.build.add_stages(None)
        self.assertEqual(0, len(self.build.stages.stages))

        self.build.add_stages("string")
        self.assertEqual(0, len(self.build.stages.stages))

        stages = Stages()
        stages.read_csv(constants.TEST_SAMPLE_TIMESTAMP_FILE)
        self.build.add_stages(stages)
        self.assertEqual(3, len(self.build.stages.stages))

        # stages should not change when submitting an invalid object
        self.build.add_stages(None)
        self.assertEqual(3, len(self.build.stages.stages))

        self.build.add_stages("string")
        self.assertEqual(3, len(self.build.stages.stages))

        self.build.add_stages(Stages())
        self.assertEqual(0, len(self.build.stages.stages))

    def test_add_stage(self):
        """Test adding a stage"""
        # error is thrown when called without parameters
        self.assertRaises(TypeError, self.build.add_stage)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, self.build.add_stage, None)
        self.assertRaises(TypeError, self.build.add_stage, "string")

        # add a stage
        stage = Stage()
        stage.set_name("stage1")
        stage.set_started_at(constants.TIMESTAMP_STARTED)
        stage.set_finished_at(constants.TIMESTAMP1)
        stage.set_duration(235)

        self.build.add_stage(stage)

        # test number of stages
        self.assertEqual(1, len(self.build.stages.stages))

        # test started_at
        self.assertEqual(
            constants.SPLIT_TIMESTAMP_STARTED,
            self.build.stages.started_at
        )

        # test finished_at
        self.assertEqual(
            constants.SPLIT_TIMESTAMP1,
            self.build.stages.finished_at
        )

        # test stages (names + duration)
        self.assertListEqual(
            [{
                'duration': 235,
                'finished_at': constants.SPLIT_TIMESTAMP1,
                'name': 'stage1',
                'started_at': constants.SPLIT_TIMESTAMP_STARTED
            }],
            self.build.stages.stages)

        # add another stage
        stage = Stage()
        stage.set_name("stage2")
        stage.set_started_at(constants.TIMESTAMP1)
        stage.set_finished_at(constants.TIMESTAMP_FINISHED)
        stage.set_duration(136.234)

        self.build.add_stage(stage)

        # test number of stages
        self.assertEqual(2, len(self.build.stages.stages))

        # test started_at
        self.assertEqual(
            constants.SPLIT_TIMESTAMP_STARTED,
            self.build.stages.started_at
        )

        # test finished_at
        self.assertEqual(
            constants.SPLIT_TIMESTAMP_FINISHED,
            self.build.stages.finished_at
        )

        # test stages (names + duration)
        self.assertListEqual([
            {
                'duration': 235,
                'finished_at': constants.SPLIT_TIMESTAMP1,
                'name': 'stage1',
                'started_at': constants.SPLIT_TIMESTAMP_STARTED
            },
            {
                'duration': 136.234,
                'finished_at': constants.SPLIT_TIMESTAMP_FINISHED,
                'name': 'stage2',
                'started_at': constants.SPLIT_TIMESTAMP1
            }],
            self.build.stages.stages)

    def test_add_property(self):
        """Test adding a property"""
        self.build.add_property('property1', 2)
        self.assertEqual(1, self.build.properties.get_size())
        self.assertDictEqual(
            {'property1': 2},
            self.build.properties.get_items()
        )

        self.build.add_property('property2', 3)
        self.assertEqual(2, self.build.properties.get_size())
        self.assertDictEqual(
            {'property1': 2, 'property2': 3},
            self.build.properties.get_items()
        )

        self.build.add_property('property2', 4)
        self.assertEqual(2, self.build.properties.get_size())
        self.assertDictEqual(
            {'property1': 2, 'property2': 4},
            self.build.properties.get_items()
        )

    def test_get_property(self):
        """Test getting a property"""
        self.build.add_property('property1', 2)
        self.assertEqual(2, self.build.get_property('property1'))

        self.build.add_property('property1', None)
        self.assertEqual(None, self.build.get_property('property1'))

        self.build.add_property('property2', 3)
        self.assertEqual(3, self.build.get_property('property2'))

        self.build.add_property('property2', 4)
        self.assertEqual(4, self.build.get_property('property2'))

    def test_get_property_does_not_exist(self):
        """Test getting a nonexistant property"""
        self.assertEqual(None, self.build.get_property('no_property'))

    def test_get_properties(self):
        """Test getting properties"""
        self.build.add_property('property1', 2)
        self.assertDictEqual(
            {'duration': 0, 'property1': 2},
            self.build.get_properties())

        self.build.add_property('property2', 3)
        self.assertDictEqual(
            {'duration': 0, 'property1': 2, 'property2': 3},
            self.build.get_properties())

        self.build.add_property('property2', 4)
        self.assertDictEqual(
            {'duration': 0, 'property1': 2, 'property2': 4},
            self.build.get_properties())

    def test_load_properties(self):
        """Test loading properties"""
        self.build.load_properties_from_settings()

        self.assertDictEqual(
            {'duration': 0, "repo": buildtimetrend.NAME},
            self.build.get_properties())

        settings = Settings()
        settings.add_setting("ci_platform", "travis")
        settings.add_setting("build", "123")
        settings.add_setting("job", "123.1")
        settings.add_setting("branch", "branch1")
        settings.add_setting("result", "passed")
        settings.add_setting("build_trigger", "push")
        settings.add_setting(
            "pull_request",
            {
                "is_pull_request": False,
                "title": None,
                "number": None
            }
        )
        settings.set_project_name("test/project")

        self.build.load_properties_from_settings()
        self.assertDictEqual(
            {
                'duration': 0,
                'ci_platform': "travis",
                'build': "123",
                'job': "123.1",
                'branch': "branch1",
                'result': "passed",
                'build_trigger': "push",
                'pull_request': {
                    "is_pull_request": False,
                    "title": None,
                    "number": None},
                'repo': "test/project"
            },
            self.build.get_properties())

    def test_set_duration(self):
        """Test calculating and setting a duration"""
        self.build.add_property("duration", 20)
        self.assertDictEqual({'duration': 20}, self.build.get_properties())

        # read and parse sample file
        self.build = BuildJob(constants.TEST_SAMPLE_TIMESTAMP_FILE)

        # test dict
        self.assertDictEqual({
            'duration': 17,
            'started_at': constants.SPLIT_TIMESTAMP1,
            'finished_at': constants.SPLIT_TIMESTAMP4,
            'stages': [
                {
                    'duration': 2,
                    'finished_at': constants.SPLIT_TIMESTAMP2,
                    'name': 'stage1',
                    'started_at': constants.SPLIT_TIMESTAMP1
                },
                {
                    'duration': 5,
                    'finished_at': constants.SPLIT_TIMESTAMP3,
                    'name': 'stage2',
                    'started_at': constants.SPLIT_TIMESTAMP2
                },
                {
                    'duration': 10,
                    'finished_at': constants.SPLIT_TIMESTAMP4,
                    'name': 'stage3',
                    'started_at': constants.SPLIT_TIMESTAMP3
                }
            ]},
            self.build.to_dict())

        # setting duration, overrides total stage duration
        self.build.add_property("duration", 20)

        # test dict
        self.assertDictEqual({
            'duration': 20,
            'started_at': constants.SPLIT_TIMESTAMP1,
            'finished_at': constants.SPLIT_TIMESTAMP4,
            'stages': [
                {
                    'duration': 2,
                    'finished_at': constants.SPLIT_TIMESTAMP2,
                    'name': 'stage1',
                    'started_at': constants.SPLIT_TIMESTAMP1
                },
                {
                    'duration': 5,
                    'finished_at': constants.SPLIT_TIMESTAMP3,
                    'name': 'stage2',
                    'started_at': constants.SPLIT_TIMESTAMP2
                },
                {
                    'duration': 10,
                    'finished_at': constants.SPLIT_TIMESTAMP4,
                    'name': 'stage3',
                    'started_at': constants.SPLIT_TIMESTAMP3
                }
            ]},
            self.build.to_dict())

    def test_to_dict(self):
        """Test exporting as a dictonary."""
        # read and parse sample file
        self.build = BuildJob(constants.TEST_SAMPLE_TIMESTAMP_FILE)

        # test dict
        self.assertDictEqual({
            'duration': 17,
            'started_at': constants.SPLIT_TIMESTAMP1,
            'finished_at': constants.SPLIT_TIMESTAMP4,
            'stages': [
                {
                    'duration': 2,
                    'finished_at': constants.SPLIT_TIMESTAMP2,
                    'name': 'stage1',
                    'started_at': constants.SPLIT_TIMESTAMP1
                },
                {
                    'duration': 5,
                    'finished_at': constants.SPLIT_TIMESTAMP3,
                    'name': 'stage2',
                    'started_at': constants.SPLIT_TIMESTAMP2
                },
                {
                    'duration': 10,
                    'finished_at': constants.SPLIT_TIMESTAMP4,
                    'name': 'stage3',
                    'started_at': constants.SPLIT_TIMESTAMP3
                }
            ]},
            self.build.to_dict())

        # add properties
        self.build.add_property('property1', 2)
        self.build.add_property('property2', 3)
        # started_at property should override default value
        self.build.set_started_at(constants.ISOTIMESTAMP_STARTED)
        # finished_at property should override default value
        self.build.set_finished_at(constants.ISOTIMESTAMP_FINISHED)
        # test dict
        self.assertDictEqual({
            'duration': 17,
            'started_at': constants.SPLIT_TIMESTAMP_STARTED,
            'finished_at': constants.SPLIT_TIMESTAMP_FINISHED,
            'property1': 2, 'property2': 3,
            'stages': [
                {
                    'duration': 2,
                    'finished_at': constants.SPLIT_TIMESTAMP2,
                    'name': 'stage1',
                    'started_at': constants.SPLIT_TIMESTAMP1},
                {
                    'duration': 5,
                    'finished_at': constants.SPLIT_TIMESTAMP3,
                    'name': 'stage2',
                    'started_at': constants.SPLIT_TIMESTAMP2},
                {
                    'duration': 10,
                    'finished_at': constants.SPLIT_TIMESTAMP4,
                    'name': 'stage3',
                    'started_at': constants.SPLIT_TIMESTAMP3}
            ]},
            self.build.to_dict())

    def test_stages_to_list(self):
        """Test exporting stages as a list."""
        # read and parse sample file
        self.build = BuildJob(constants.TEST_SAMPLE_TIMESTAMP_FILE)

        # test list
        self.assertListEqual([
            {
                'stage': {
                    'duration': 2,
                    'finished_at': constants.SPLIT_TIMESTAMP2,
                    'name': 'stage1',
                    'started_at': constants.SPLIT_TIMESTAMP1},
                'job': {
                    'duration': 17,
                    'started_at': constants.SPLIT_TIMESTAMP1,
                    'finished_at': constants.SPLIT_TIMESTAMP4}
            },
            {
                'stage': {
                    'duration': 5,
                    'finished_at': constants.SPLIT_TIMESTAMP3,
                    'name': 'stage2',
                    'started_at': constants.SPLIT_TIMESTAMP2},
                'job': {
                    'duration': 17,
                    'started_at': constants.SPLIT_TIMESTAMP1,
                    'finished_at': constants.SPLIT_TIMESTAMP4}
            },
            {
                'stage': {
                    'duration': 10,
                    'finished_at': constants.SPLIT_TIMESTAMP4,
                    'name': 'stage3',
                    'started_at': constants.SPLIT_TIMESTAMP3},
                'job': {
                    'duration': 17,
                    'started_at': constants.SPLIT_TIMESTAMP1,
                    'finished_at': constants.SPLIT_TIMESTAMP4}
            }],
            self.build.stages_to_list())

        # add properties
        self.build.add_property('property1', 2)
        self.build.add_property('property2', 3)
        # started_at property should override default value
        self.build.set_started_at(constants.ISOTIMESTAMP_STARTED)
        # finished_at property should override default value
        self.build.set_finished_at(constants.ISOTIMESTAMP_FINISHED)
        # test dict
        self.assertListEqual([
            {
                'stage': {
                    'duration': 2,
                    'finished_at': constants.SPLIT_TIMESTAMP2,
                    'name': 'stage1',
                    'started_at': constants.SPLIT_TIMESTAMP1},
                'job': {
                    'duration': 17,
                    'started_at': constants.SPLIT_TIMESTAMP_STARTED,
                    'finished_at': constants.SPLIT_TIMESTAMP_FINISHED,
                    'property1': 2, 'property2': 3}
            },
            {
                'stage': {
                    'duration': 5,
                    'finished_at': constants.SPLIT_TIMESTAMP3,
                    'name': 'stage2',
                    'started_at': constants.SPLIT_TIMESTAMP2},
                'job': {
                    'duration': 17,
                    'started_at': constants.SPLIT_TIMESTAMP_STARTED,
                    'finished_at': constants.SPLIT_TIMESTAMP_FINISHED,
                    'property1': 2, 'property2': 3}
            },
            {
                'stage': {
                    'duration': 10,
                    'finished_at': constants.SPLIT_TIMESTAMP4,
                    'name': 'stage3',
                    'started_at': constants.SPLIT_TIMESTAMP3},
                'job': {
                    'duration': 17,
                    'started_at': constants.SPLIT_TIMESTAMP_STARTED,
                    'finished_at': constants.SPLIT_TIMESTAMP_FINISHED,
                    'property1': 2, 'property2': 3}
            }],
            self.build.stages_to_list())

    def test_to_xml(self):
        """Test exporting in XML format."""
        # read and parse sample file
        self.build = BuildJob(constants.TEST_SAMPLE_TIMESTAMP_FILE)

        # test xml output
        expected_xml = etree.fromstring(
            b'<build><stages><stage duration="2.0" name="stage1"/>'
            b'<stage duration="5.0" name="stage2"/>'
            b'<stage duration="10.0" name="stage3"/></stages></build>'
        )
        self.assertTrue(xml_compare(expected_xml, self.build.to_xml()))

        # add properties
        self.build.add_property('property1', 2)
        self.build.add_property('property2', 3)
        # test xml output
        expected_xml = etree.fromstring(
            b'<build property1="2" property2="3">'
            b'<stages><stage duration="2.0" name="stage1"/>'
            b'<stage duration="5.0" name="stage2"/>'
            b'<stage duration="10.0" name="stage3"/></stages></build>'
        )
        self.assertTrue(xml_compare(expected_xml, self.build.to_xml()))

    def test_to_xml_string(self):
        """Test exporting in XML string format."""
        # read and parse sample file
        self.build = BuildJob(constants.TEST_SAMPLE_TIMESTAMP_FILE)

        # test xml string output
        self.assertEqual(
            b'<build>\n'
            b'  <stages>\n'
            b'    <stage duration="2.0" name="stage1"/>\n'
            b'    <stage duration="5.0" name="stage2"/>\n'
            b'    <stage duration="10.0" name="stage3"/>\n'
            b'  </stages>\n'
            b'</build>\n',
            self.build.to_xml_string())

        # add properties
        self.build.add_property('property1', 2)
        self.build.add_property('property2', 3)
        # test xml string output
        expected_xml = etree.fromstring(
            b'<build property1="2" property2="3">\n'
            b'  <stages>\n'
            b'    <stage duration="2.0" name="stage1"/>\n'
            b'    <stage duration="5.0" name="stage2"/>\n'
            b'    <stage duration="10.0" name="stage3"/>\n'
            b'  </stages>\n'
            b'</build>\n'
        )
        self.assertTrue(
            xml_compare(
                expected_xml, etree.fromstring(self.build.to_xml_string())
            )
        )
