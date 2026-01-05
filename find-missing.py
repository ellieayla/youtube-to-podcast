#!/usr/bin/env python

from pathlib import Path
import argparse
import logging
import yaml


logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("postsdir", default=Path("_posts"), help="Container of _post/ markdown files", type=Path)
    parser.add_argument("--only-channel", action='extend', nargs='*')
    parser.add_argument("--id", action="store_true")
    parser.add_argument("-v", default=False, action="store_true")
    n = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if n.v else logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    logging.debug(f"arguments {n}")
    if not n.postsdir.exists() or not n.postsdir.is_dir():
        raise NotADirectoryError(n.postsdir)

    markdown_directory: Path = n.postsdir

    logging.info(f"Only considering channels: {n.only_channel}")
    for markdown_file in markdown_directory.glob("*.markdown"):

        with open(markdown_file, 'r') as f:
            yaml_docs = yaml.safe_load_all(f)
            yaml_frontmatter = next(yaml_docs)

            audio_path = Path(yaml_frontmatter['audio'])

        if n.only_channel:
            channel_id = yaml_frontmatter['channel_id']
            if channel_id not in n.only_channel:
                continue

        if not audio_path.exists():
            if n.id:
                print(yaml_frontmatter['id'])
            else:
                print(yaml_frontmatter['webpage_url'])


if __name__ == '__main__':
    main()
