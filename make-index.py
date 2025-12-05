#!/usr/bin/env python

import json

import logging.config
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime

import argparse
import logging
import re


logger = logging.getLogger(__name__)


@dataclass(order=True, eq=True)
class Audio:
    date: datetime  # first so can be sorted
    channel_id: str
    id: str
    author: str
    title: str
    audio: Path
    length: int = field(repr=False)  # bytes
    info_json: Path = field(repr=False)
    description: str = field(repr=False)
    transcript: Path
    duration: int = field(repr=False)  # seconds
    thumbnail: Path = field(repr=False)
    webpage_url: str = field(repr=False)

    def as_dict(self):
        d = asdict(self)
        del d["description"]
        return d
    
    def as_frontmatter(self):
        return "---\n\n" + json.dumps(self.as_dict(), default=str) + "\n\n---\n\n"


@dataclass(order=True, eq=True)
class Channel:
    channel_id: str
    author: str
    thumbnail: Path = field(repr=False)
    webpage_url: str = field(repr=False)
    info_json: Path = field(repr=False)
    description: str = field(repr=False)

    def as_dict(self):
        d = asdict(self)
        del d["description"]
        return d
    
    def as_frontmatter(self):
        return "---\n\n" + json.dumps(self.as_dict(), default=str) + "\n\n---\n\n"


def parse_info_json(info_file: Path) -> Audio:
    logger.debug(f"Parsing {info_file}")

    with open(info_file) as f:
        i = json.load(f)
        
        audio_file = find_file_beside_info_json(info_file, [".m4a", ".mp4"])
        
        if not audio_file:
            logger.warning(f"Skipping {info_file} - no matching m4a")
            return None

        thumbnail_file = find_file_beside_info_json(info_file, (".png",))
        length = audio_file.stat().st_size

        transcript_file = find_file_beside_info_json(info_file, possible_suffix=[".en.vtt", ".en-orig.vtt"])

        description_file = find_file_beside_info_json(info_file, (".description",))
        with open(description_file) as df:
            description = df.read()
            description = re.sub(r'^-+$', "", description, flags=re.MULTILINE)  # remove ^----$ heading rows

        if not 'channel_id' in i:
            if 'playlist_channel_id' in i:
                i['channel_id'] = i['playlist_channel_id']
        if not 'channel' in i:
            if 'playlist_channel' in i:
                i['channel'] = i['playlist_channel']

        # duration_string
        return Audio(
            date= datetime.strptime(i["upload_date"], "%Y%m%d").date(),
            channel_id=i["channel_id"],
            author=i["channel"],
            id=i["id"],
            title=i["title"],
            audio=audio_file,
            length=length,
            info_json=info_file,
            transcript=transcript_file,
            description=description,
            duration=i["duration"],
            thumbnail=thumbnail_file,
            webpage_url=i["webpage_url"],
        )

def find_file_beside_info_json(info_file: Path, possible_suffix: list):
    root = info_file.with_suffix("")

    for _ in possible_suffix:
        candidate = root.with_suffix(_)
        print(f"Looking for {candidate=}")
        if candidate.exists():
            return candidate
    return None

def parse_info_json_channel(info_file: Path):
    if not info_file.stem.startswith("Unknown"):
        return None
    assert info_file.with_suffix("").with_suffix("").stem == 'Unknown'

    parent_directory_maybe_channel_slug = info_file.parent.stem

    if info_file.with_suffix("").stem != 'Unknown.' + parent_directory_maybe_channel_slug:
        return None
    
    # match, this info.json file is a channel
    thumbnail = find_file_beside_info_json(info_file, possible_suffix=(".png", ".jpg"))
    logger.info(f"Found thumbnail {thumbnail=}")

    with open(info_file) as f:
        i = json.load(f)
    
    return Channel(
        channel_id=i["channel_id"],
        author=i["channel"],
        thumbnail=thumbnail,
        webpage_url=i["channel_url"],
        info_json=info_file,
        description=i["description"],
    )


def read_source_files(source_directory, using=parse_info_json):

    for info_file in Path(source_directory).rglob("*.info.json"):
        try:
          a = using(info_file)
          if a:
            yield(a)
        except:
          logger.exception(f"Failed to parse {info_file=}")
          raise

def write_markdown_file(o: dataclass, markdown_file: Path, overwrite=False):

    proposed_string = o.as_frontmatter() + o.description

    if markdown_file.exists() and not overwrite:
        #logger.warning(f"Skipping {markdown_file}, already exists")

        with open(markdown_file, "r") as f:
            if proposed_string != f.read():
                logger.warning(f"File {markdown_file=} should be updated, but {overwrite=}")

        return    

    with open(markdown_file, "w") as f:
        f.write(o.as_frontmatter())
        f.write(o.description)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="Container of .info.json files", type=Path)
    parser.add_argument("--overwrite", default=False, action="store_true")
    parser.add_argument("-v", default=False, action="store_true")
    n = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if n.v else logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    logging.debug(f"arguments {n}")
    for _ in n.paths:
        if not _.exists() or not _.is_dir():
            raise NotADirectoryError(_)

    audio = []
    for _ in n.paths:
        for a in read_source_files(_):
            audio.append(a)

    audio.sort(reverse=True)

    for _ in audio:
        markdown_file = Path("_posts") / f"{_.date.isoformat()}-{_.id}.markdown"
        write_markdown_file(_, markdown_file, overwrite=n.overwrite)

    channels = []
    for _ in n.paths:
        for c in read_source_files(_, using=parse_info_json_channel):

            original_thumbnail = Path(c.thumbnail)
            image_file = (Path("_channels") / c.channel_id).with_suffix(original_thumbnail.suffix)
            image_file.write_bytes(original_thumbnail.read_bytes())
            c.thumbnail = image_file.relative_to(Path("_channels"))

            markdown_file = (Path("_channels") / c.channel_id).with_suffix(".md")
            write_markdown_file(c, markdown_file, overwrite=n.overwrite)
            

if __name__ == '__main__':
    main()
