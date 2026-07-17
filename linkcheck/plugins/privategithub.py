# Copyright (C) 2024 Konrad Weihmann
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
'''
Check private github pages without exposing username/password.
'''
import re
import os

from urllib.parse import urlparse
from . import _ConnectionPlugin
from .. import log, LOG_PLUGIN


class PrivateGithub(_ConnectionPlugin):
    '''To check private github pages, rewrite a URL and check for the existence
       of a link via the Github API instead of base64 encode secrets.
       Like this only a revokable token needs to be used.'''

    def __init__(self, config):
        '''Set everything from config.'''
        super().__init__(config)
        self.prefixes = [x.strip() for x in re.split(
            r'\n|\s', config.get('prefixes', '')) if x]
        self.pat = os.environ.get('GITHUB_TOKEN', '')
        self.avaialable = any(self.prefixes) and any(self.pat)
        self.ratelimitskip = config.get('ratelimitskip', False)
        if not self.pat:
            log.error(
                LOG_PLUGIN, 'No PAT/Token prodived for private github pages')

    def _url_components(self, base_url):
        tmp = urlparse(base_url)
        return (tmp.netloc + tmp.path, tmp.path)

    def applies_to(self, url_data):
        '''Check if passed URL is for us.'''
        url, _ = self._url_components(url_data.base_url)
        res = url_data.is_http() and self.avaialable and any(url.startswith(prefix)
                                                             for prefix in self.prefixes)
        return res

    @staticmethod
    def _run_request_api(url_data, api_url, pat):
        '''Static method to make it easily mockable in test'''
        # for details see https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#get-repository-content
        return url_data.session.get(
            api_url,
            headers={
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28',
                'Authorization': f'bearer {pat}',
            },
        ).status_code
    
    @staticmethod
    def _run_request_release(url_data, api_url, pat, asset):
        '''Static method to make it easily mockable in test'''
        # for details see https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#get-a-release-by-tag-name
        # respectively https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#get-the-latest-release
        res = url_data.session.get(
            api_url,
            headers={
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28',
                'Authorization': f'bearer {pat}',
            },
        ).json()
        if any(x.get('name', '') == asset for x in res.get('assets', [])):
            return 200
        return 404

    def check(self, url_data):
        '''Check content.'''
        log.debug(LOG_PLUGIN, 'checking as private github page')
        try:
            _, path = self._url_components(url_data.base_url)
            chunks = path.lstrip('/').split('/')
            if len(chunks) < 2:
                return
            org = chunks.pop(0)
            repo = chunks.pop(0)
            ref = ''
            rest = ''

            if any(chunks):
                if chunks[0] == 'blob':
                    chunks.pop(0)
                    ref = chunks.pop(0)
                rest = '/'.join(chunks)

            if 'releases' in chunks:
                # possible chunks left
                # latest/download/asset.zip
                # download/1.2.4/asset.zip
                chunks.remove('releases')
                if chunks[0] == 'latest':
                    api_url = f'https://api.github.com/repos/{org}/{repo}/releases/latest'
                else:
                    chunks.pop(0)
                    api_url = f'https://api.github.com/repos/{org}/{repo}/releases/tags/{chunks[0]}'
                asset = chunks[-1]
                log.debug(
                    LOG_PLUGIN, f'Private github API release url {api_url}')
                result = PrivateGithub._run_request_release(url_data, api_url, self.pat, asset)
                log.debug(
                    LOG_PLUGIN, f'Private github API release result {result}')
            else:
                api_url = f'https://api.github.com/repos/{org}/{repo}/contents/{rest}'
                if ref:
                    api_url += f'?ref={ref}'

                log.debug(
                    LOG_PLUGIN, f'Private github API url {api_url}')

                result = PrivateGithub._run_request_api(url_data, api_url, self.pat)
                log.debug(
                    LOG_PLUGIN, f'Private github API result {result}')

            if self.ratelimitskip and result in [429]:
                log.info(
                    LOG_PLUGIN, 'Github API request rate limited, skipping as configured')
            elif result not in [200, 302, 304]:
                url_data.set_result(
                    'Private GitHub page is not accessible', valid=False, overwrite=True)
                return
            url_data.set_result(' ', valid=True, overwrite=True)
        except Exception as e:
            log.info(LOG_PLUGIN, f'Private github page check threw: {e}')
            url_data.set_result(
                    'Private GitHub page is not valid', valid=False, overwrite=True)

    @classmethod
    def read_config(cls, configparser):
        '''Read configuration file options.'''
        config = dict()
        log.debug(LOG_PLUGIN, 'read_config')
        section = cls.__name__
        if configparser.has_option(section, 'prefixes'):
            config['prefixes'] = configparser.get(section, 'prefixes')
        else:
            config['prefixes'] = ''

        if configparser.has_option(section, 'ratelimitskip'):
            config['ratelimitskip'] = configparser.get(
                section, 'ratelimitskip') is not None
        else:
            config['ratelimitskip'] = False
        return config
