# Copyright (C) 2020 Dmitry Marakasov <amdmi3@amdmi3.ru>
#
# This file is part of repology
#
# repology is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# repology is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with repology.  If not, see <http://www.gnu.org/licenses/>.

from typing import Iterable

from repology.package import LinkType
from repology.packagemaker import NameType, PackageFactory, PackageMaker
from repology.parsers import Parser
from repology.parsers.json import iter_json_list
from repology.transformer import PackageTransformer


# see `jq '.[].info.project_urls' < pypicache.json` for all of them
_url_types = {
    'bug reports': LinkType.UPSTREAM_ISSUE_TRACKER,
    'bug tracker': LinkType.UPSTREAM_ISSUE_TRACKER,
    'change log': LinkType.UPSTREAM_CHANGELOG,
    'changelog': LinkType.UPSTREAM_CHANGELOG,
    'ci': LinkType.UPSTREAM_CI,
    'chat': LinkType.UPSTREAM_DISCUSSION,
    'coverage': LinkType.UPSTREAM_COVERAGE,
    'discord': LinkType.UPSTREAM_DISCUSSION,
    'discussions': LinkType.UPSTREAM_DISCUSSION,
    'documentation': LinkType.UPSTREAM_DOCUMENTATION,
    'docs': LinkType.UPSTREAM_DOCUMENTATION,
    'donation': LinkType.UPSTREAM_DONATION,
    'download': LinkType.UPSTREAM_DOWNLOAD,
    'forum': LinkType.UPSTREAM_DISCUSSION,
    'funding': LinkType.UPSTREAM_DONATION,
    'history': LinkType.UPSTREAM_CHANGELOG,
    'homepage': LinkType.UPSTREAM_HOMEPAGE,
    'issue tracker': LinkType.UPSTREAM_ISSUE_TRACKER,
    'issues': LinkType.UPSTREAM_ISSUE_TRACKER,
    'release notes': LinkType.UPSTREAM_CHANGELOG,
    'repository': LinkType.UPSTREAM_REPOSITORY,
    'source code': LinkType.UPSTREAM_REPOSITORY,
    'source': LinkType.UPSTREAM_REPOSITORY,
    'sources': LinkType.UPSTREAM_REPOSITORY,
    'tracker': LinkType.UPSTREAM_ISSUE_TRACKER,
    'website': LinkType.UPSTREAM_HOMEPAGE,
    'wiki': LinkType.UPSTREAM_WIKI,
}


class PyPiCacheJsonParser(Parser):
    def iter_parse(self, path: str, factory: PackageFactory, transformer: PackageTransformer) -> Iterable[PackageMaker]:
        for pkgdata in iter_json_list(path, (None,)):
            with factory.begin() as pkg:
                info = pkgdata['info']

                pkg.add_name(info['name'], NameType.PYPI_NAME)
                pkg.set_version(info['version'])

                pkg.add_links(LinkType.PROJECT_HOMEPAGE, info['project_url'])
                if (url := info.get('home_page')) and url != 'UNKNOWN':
                    pkg.add_links(LinkType.UPSTREAM_HOMEPAGE, url)

                if info['project_urls']:
                    for key, url in info['project_urls'].items():
                        if (link_type := _url_types.get(key.lower())) and url != 'UNKNOWN':
                            pkg.add_links(link_type, url)

                for item in pkgdata['releases'][info['version']]:
                    pkg.add_links(LinkType.PROJECT_DOWNLOAD, item['url'])

                if info['author_email']:
                    pkg.add_maintainers(map(str.strip, info['author_email'].split(',')))

                if info['summary']:
                    pkg.set_summary(info['summary'])

                yield pkg
