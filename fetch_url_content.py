#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright [2017] [Daisuke Miyakawa]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG
import platform
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import sys
import traceback


def main():
    """\
    指定したURLの内容をrequestsにて取得し、
    標準出力で表示可能であれば出力する。
    --out-file (-o) オプションでファイルに書き込むことも可能。
    """
    parser = ArgumentParser(description=(__doc__),
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('url', help='URL to fetch')
    parser.add_argument('--verify', dest='verify',
                        action='store_true',
                        help='Verify TLS Certificate')
    parser.add_argument('--no-verify', '-n',
                        dest='verify', action='store_false',
                        help='Do not verify TLS Certificate')
    parser.set_defaults(verify=True)
    parser.add_argument('-o', '--out-file',
                        help='Write content to the specified file')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Same as --log DEBUG')
    parser.add_argument('-w', '--warning', action='store_true',
                        help='Same as --log WARNING')
    args = parser.parse_args()
    logger = getLogger(__name__)
    handler = StreamHandler()
    logger.addHandler(handler)
    if args.debug:
        logger.setLevel(DEBUG)
        handler.setLevel(DEBUG)
    handler.setFormatter(Formatter('%(asctime)s %(levelname)7s %(message)s'))
    logger.debug('Start running (url: {}, Python-Version: {})'
                 .format(args.url, platform.python_version()))
    try:
        if not args.verify:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        r = requests.get(args.url, verify=args.verify)
    except Exception as e:
        logger.error('Exception raised during fetching content ({})'
                     .format(e))
        for line in traceback.format_exc().rstrip().split('\n'):
            logger.error(line)
        logger.error('Aborting')
        return 1

    logger.debug('status_code: {}'.format(r.status_code))
    logger.debug('headers: ')
    for header, value in r.headers.items():
        logger.debug('  {}: {}'.format(header, value))
    content_type = r.headers.get('Content-Type')
    if args.out_file:
        logger.debug('Writing content to "{}"'.format(args.out_file))
        with open(args.out_file, 'wb') as f:
            f.write(r.content)
    else:
        printed = False
        if content_type and content_type.startswith('text'):
            try:
                print(r.text)
                printed = True
            except Exception as e:
                logger.error('Failed to print to stdout ({})'.format(e))
        else:
            logger.info('Seems not text (Content-Type: {})'
                        .format(content_type))
        if not printed:
            logger.info('Output suppressed. Consider using'
                        ' --out-file (-o) instead')
    logger.debug('Finished running')
    return 0


if __name__ == '__main__':
    sys.exit(main())
