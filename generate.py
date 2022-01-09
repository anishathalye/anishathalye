#!/usr/bin/env python3

import yaml
from github import Github
import argparse


DATA_FILE = 'data.yml'
LANGUAGE_FILE = 'languages.yml'
OUTPUT_FILE = 'README.md'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--default-user', type=str, required=True, help='Default username')
    parser.add_argument('--token', type=str, help='GitHub personal access token (to avoid rate limiting)')
    args = parser.parse_args()

    with open(LANGUAGE_FILE) as fin:
        languages = yaml.safe_load(fin)
    with open(DATA_FILE) as fin:
        data = yaml.safe_load(fin)

    g = Github(args.token)

    with open(OUTPUT_FILE, 'w') as fout:
        for i, section in enumerate(data):
            # header
            fout.write('<h3 align="center">{}</h3>\n\n'.format(section['name']))
            # table header
            fout.write('| | | |\n')
            fout.write('|---|---|---|\n')
            for repo_name in section['repos']:
                display_name = repo_name
                if '/' not in repo_name:
                    repo_name = '{}/{}'.format(args.default_user, repo_name)
                repo = g.get_repo(repo_name)
                # prevent breaking on '-' and '/'
                display_name = display_name.replace('-', '\u2060-\u2060')
                display_name = display_name.replace('/', '\u2060/\u2060')
                link = '[**{}**](https://github.com/{})'.format(display_name, repo_name)
                language_logo = '![{}]({})'.format(repo.language, languages[repo.language]) if repo.language else ''
                stars = repo.watchers
                if stars >= 1000:
                    stars = '{:.1f}k'.format(round(stars/100)/10)
                fout.write('| {} <br /> \u2605\u2060 \u2060{} | {} | {} |\n'.format(
                    link,
                    stars,
                    language_logo,
                    repo.description
                ))
            if i < len(data)-1:
                fout.write('\n')


def is_dark(color):
    l = 0.2126 * int(color[0:2], 16) + 0.7152 * int(color[2:4], 16) + 0.0722 * int(color[4:6], 16)
    return False if l / 255 > 0.65 else True


if __name__ == '__main__':
    main()

