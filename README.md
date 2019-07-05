## acfun-joker

This script tools is used to play with [acfun](https://www.acfun.cn) videos, it supports to parse video info and videos from specified user, download and list the videos, currently.

#### Environment

* Python 2.7 or later.
* [you-get](https://github.com/soimort/you-get) for video downloading.

#### Installation

```shell
pip install acfun -U
```

There is a configuration file located `~/.config/acfun-joker/config` for user preferences, the `entity.sqlite3` database file in the same directory stores all the downloaded videos' meta data including the corresponding video downloaded path, it defaults to the `~/Downloads/acfun-joker/` and could be changed via the `config` file.

#### Usage

```shell
➜ acfun --help
Usage: acfun [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug
  --help                Show this message and exit.

Commands:
  download  Download the video via you-get
  info      Parse the video detail page's info
  list      Download the video via you-get
  user      Parse the user page's videos

➜ acfun user --help
Usage: acfun user [OPTIONS] USER_ID

  Parse the user page's videos

Options:
  --exist-abort / --no-exist-abort
  --url-only / --verbose
  --download / --no-download
  -p, --page INTEGER
  --help                          Show this message and exit.
```

#### Author

Will Han, [xingheng.hax@qq.com](mailto:xingheng.hax@qq.com)

#### License

[MIT license](./LICENSE.txt).
