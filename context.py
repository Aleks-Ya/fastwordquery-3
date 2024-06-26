# -*- coding:utf-8 -*-
#
# Copyright (C) 2018 sthoo <sth201807@gmail.com>
#
# Support: Report an issue at https://github.com/sth2018/FastWordQuery/issues
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version; http://www.gnu.org/copyleft/gpl.html.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import json
import logging
import os
from pathlib import Path

from anki.hooks import runHook
from aqt import mw

from .constants import VERSION
from .utils import get_icon

__all__ = ['APP_ICON', 'config']

APP_ICON = get_icon('wqicon.png')  # Addon Icon


class Config(object):
    """Addon Config"""

    def __init__(self, window):
        self.log = logging.getLogger(__class__.__name__)
        self.window = window
        self.version = '0'
        self.data = None
        user_home_dir: Path = Path.home()
        config_file_name = 'fastwqcfg.json'
        self.path: Path = user_home_dir.joinpath(u'_' + config_file_name)
        self.path_legacy: Path = user_home_dir.joinpath(u'.' + config_file_name)
        self.log.info(f"User home dir: {user_home_dir}")
        self.log.info(f"Config path: {self.path}")
        self.log.info(f"Config path (legacy): {self.path_legacy}")
        self.read()

    @property
    def pmname(self):
        return self.window.pm.name

    def update(self, data):
        """Update && Save"""
        data['version'] = VERSION
        data['%s_last' % self.pmname] = data.get('last_model', self.last_model_id)
        self.data.update(data)
        self.log.debug(f"Update file: {self.path}")
        self.log.debug(f"Update data: {self.data}")
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, sort_keys=True, ensure_ascii=False)
            f.close()
        runHook('config.update')

    def read(self):
        """Load from config file"""
        if self.data:
            return self.data
        try:
            path = self.path if os.path.exists(self.path) else self.path_legacy
            if os.path.exists(path):
                self.log.debug(f"Reading file: {path}")
                with open(path, 'r', encoding="utf-8") as f:
                    self.data = json.load(f)
                    f.close()
            else:
                self.data = dict()
            if not os.path.exists(self.path):
                self.update(self.data)
        except IOError:
            self.log.exception('can not find config file')
            self.data = dict()
        self.log.debug(f"Config file was read: {self.data}")

    def get_maps(self, model_id):
        """Query fields map"""
        return self.data.get(str(model_id), list())

    @property
    def last_model_id(self):
        return self.data.get('%s_last' % self.pmname, 0)

    @property
    def dirs(self):
        return self.data.get('dirs', list())

    @property
    def dicts(self):
        return self.data.get('dicts', dict())

    @property
    def use_filename(self):
        return self.data.get('use_filename', True)

    @property
    def export_media(self):
        return self.data.get('export_media', False)

    @property
    def force_update(self):
        return self.data.get('force_update', False)

    @property
    def ignore_mdx_wordcase(self):
        return self.data.get('ignore_mdx_wordcase', False)

    @property
    def thread_number(self):
        """Query Thread Number"""
        return self.data.get('thread_number', 16)

    @property
    def last_folder(self):
        """last file dialog open path"""
        return self.data.get('last_folder', '')

    @property
    def ignore_accents(self):
        """ignore accents of field in querying"""
        return self.data.get('ignore_accents', False)

    @property
    def cloze_str(self):
        """Cloze formatter string"""
        tmpstr = self.data.get('cloze_str', '{{c1::%s}}')
        if len(tmpstr.split('%s')) != 2:
            tmpstr = '{{c1::%s}}'
        return tmpstr

    @property
    def sound_str(self):
        """Sound formatter string"""
        # 设置音频播放按钮大小
        # <span style="width:24px;height:24px;">[sound:{0}]</span>
        tmpstr = self.data.get('sound_str', u'[sound:{0}]')
        if len(tmpstr.split('{0}')) != 2:
            tmpstr = u'[sound:{0}]'
        return tmpstr


config = Config(mw)
