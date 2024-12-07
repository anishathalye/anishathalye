#!/usr/bin/env python3

from github import Github
import yaml

from datetime import datetime
import argparse


WATCH_FILE = 'watch.yml'
LANGUAGE_FILE = 'languages.yml'
OUTPUT_MD = 'README.md'
OUTPUT_DATA = 'data.yml'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--default-user', type=str, required=True, help='Default username')
    parser.add_argument('--token', type=str, help='GitHub personal access token (to avoid rate limiting)')
    args = parser.parse_args()

    with open(LANGUAGE_FILE) as fin:
        languages = yaml.safe_load(fin)
    with open(WATCH_FILE) as fin:
        watch = yaml.safe_load(fin)

    g = Github(args.token)

    raw_data = {
        'date': datetime.utcnow().isoformat(),
        'user': {},
        'repositories': {}
    }

    with open(OUTPUT_MD, 'w') as fout:
        for i, section in enumerate(watch):
            hidden = section['name'] == 'Hidden'
            if not hidden:
                # header
                fout.write('<h3 align="center">{}</h3>\n\n'.format(section['name']))
                # table header
                fout.write('| | | |\n')
                fout.write('|---|---|---|\n')
            for repo_name in section['repos']:
                display_name = repo_name
                raw_display_name = repo_name
                if '/' not in repo_name:
                    repo_name = '{}/{}'.format(args.default_user, repo_name)
                repo = g.get_repo(repo_name)
                raw_data['repositories'][raw_display_name] = {
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'watching': repo.subscribers_count
                }
                if hidden:
                    continue
                # prevent breaking on '-' and '/'
                display_name = display_name.replace('-', '\u2060-\u2060')
                display_name = display_name.replace('/', '\u2060/\u2060')
                link = '[**{}**](https://github.com/{})'.format(display_name, repo_name)
                language_logo = '![{}]({})'.format(repo.language, languages[repo.language]) if repo.language else ''
                if repo.stargazers_count >= 1000:
                    stars = '{:.1f}k'.format(round(repo.stargazers_count/100)/10)
                    if stars.endswith('.0k'):
                        stars = '{}k'.format(stars[:-3])
                else:
                    stars = '{:d}'.format(repo.stargazers_count)
                fout.write('| {} <br /> \u2605\u2060 \u2060{} | {} | {} |\n'.format(
                    link,
                    stars,
                    language_logo,
                    repo.description
                ))
            if not hidden:
                fout.write('\n')
        user = g.get_user(args.default_user)
        raw_data['user'] = {
            'name': args.default_user,
            'followers': user.followers,
            'following': user.following,
            'repos': user.public_repos,
            'gists': user.public_gists,
        }
    with open(OUTPUT_DATA, 'w') as fout:
        yaml.safe_dump(raw_data, fout, sort_keys=False)


if __name__ == '__main__':
    main()
