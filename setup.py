#!/usr/bin/env python

# Copyright (c) 2020 SUSE LLC
#
# This file is part of azuremetadata.
#
# azuremetadata is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# azuremetadata is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with azuremetadata.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

version = open('lib/azuremetadata/VERSION').read().strip()

setup(
    name='azuremetadata',
    description=(
        'Command-line tool to collect Azure instance meta data'
    ),
    url='https://github.com/SUSE-Enceladus/azuremetadata',
    license='GPL-3.0+',
    author='SUSE',
    author_email='public-cloud-dev@susecloud.net',
    version=version,
    packages=find_packages('lib'),
    package_data={'azuremetadata': ['VERSION']},
    package_dir={
        '': 'lib',
    },
    scripts=['azuremetadata']
)
