#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json, re
from lxml import html
from .entity import Entity
from .config import *
from .database import DB
import os, os.path, sys, time, datetime
import click
import tempfile
import subprocess
import shutil
import distutils.spawn

DEBUG = False
ENTITY_DB = DB(get_db_path())
FAKE_HEADERS = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6',
    'dnt': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}


def _parse_video_entity_from_js(url):
    host = re.search(r'https?://([^/]+)/', url).group(1)
    assert 'acfun.cn' in host

    response = requests.get(url, headers = FAKE_HEADERS)
    if response.status_code != 200:
        return None

    # Inspired by https://stackoverflow.com/a/23896879/1677041
    m = re.search(r"(?s)videoInfo\s*=\s*(\{.*?\});", response.text)

    if m is None:
        return None

    json_text = m.group(1)
    json_data = json.loads(json_text)

    entity = Entity()
    entity.id = json_data.get('currentVideoInfo').get('id')
    entity.title = json_data.get('title')
    entity.url = url
    entity.date = json_data.get('createTimeMillis')
    entity.cover = json_data.get('coverUrl')
    entity.channel = json_data.get('channel').get('parentName') + " / " + json_data.get('channel').get('name')
    entity.poster_id = json_data.get('user').get('id')
    entity.poster_name = json_data.get('user').get('name')
    entity.banana = json_data.get('bananaCount')
    entity.stow = json_data.get('stowCount')

    return entity


def fetch_user_page(user_id, page):
    url = "https://www.acfun.cn/space/next?uid=%s&type=video&orderBy=2&pageNo=%d" % (
        user_id, page)
    response = requests.get(url, headers = FAKE_HEADERS)

    if response.status_code != 200:
        return []

    dict_result = json.loads(response.text)
    errmsg = dict_result['errmsg'] if dict_result['errno'] != 0 else None
    data = dict_result['data']
    html_text = data['html'] if data['success'] else None

    if html_text is None:
        if errmsg is not None:
            click.echo(errmsg)

        return []

    tree = html.fromstring(html_text)
    a_items = tree.xpath('./a[starts-with(@href, "/v/ac")]/figure')
    entities = []

    for item in a_items:
        entity = _parse_video_entity_from_js('https://www.acfun.cn' + item.get('data-url'))
        entity is None or entities.append(entity)

    return entities


def fetch_user_list(user_id, start_page = 1, end_page = sys.maxint, urlPrinter = None, verbosePrinter = None):
    total_entities = []
    page = start_page

    while True:
        entities = fetch_user_page(user_id, page)
        if len(entities) <= 0:
            break

        if urlPrinter or verbosePrinter:
            verbosePrinter and verbosePrinter("Fetched %ld entities from page %d" % (len(entities), page))

            for entity in entities:
                urlPrinter and urlPrinter(entity.url)
                verbosePrinter and verbosePrinter("ID: %s, URL: %s, title: %s" %
                    (entity.id, entity.url, entity.title))
            else:
                verbosePrinter and verbosePrinter("")

        total_entities.extend(entities)
        page += 1

        if page >= end_page:
            break

    return total_entities, page - 1


def print_video_info(url):
    entity = _parse_video_entity_from_js(url)

    if entity is None:
        click.echo("Empty entity received!")
    else:
        click.echo(entity.output())


def download_video(entity):
    if entity is None:
        return None

    executable = distutils.spawn.find_executable('you-get')

    if executable is None:
        click.secho('you-get is required!\n\n'
                    'Go to install it first and make sure it could be found in your $PATH.\n'
                    'https://github.com/soimort/you-get', fg='red')
        return False

    filedir, filename = get_download_path(), entity.poster_id + '-' + entity.id
    cmd = u'{} {} -O "{}" -o "{}" {}'.format(executable, get_download_options(), filename, filedir, entity.url)
    cur_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')

    try:
        if DEBUG:
            click.echo('\nCommand:\n%s\n' % cmd)

        start_time = datetime.datetime.now()
        p = subprocess.Popen(['/bin/sh', '-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        ret_code = None
        file_type = ''
        click.echo('-' * 20 + ' BEGIN ' + '-' * 20)

        while True:
            output = p.stdout.readline().strip()
            ret_code = p.poll()

            # Type:       MPEG-4 video (video/mp4)
            m = re.search(r'\(video/.*\)', output)
            if m and m.group(0):
                type_text = m.group(0)
                file_type = type_text.split('/')[1][:-1]

            if ret_code is not None:
                break
            if len(output) > 0:
                click.echo(output)

        end_time = datetime.datetime.now()
        click.echo('-' * 21 + ' END ' + '-' * 21)

        if len(file_type) > 0:
            filename += '.' + file_type

        if ret_code == 0:
            click.echo(click.style('Completed!\nTime elapsed: %s' % str(end_time - start_time), fg='green'))
            entity.download_url = os.path.join(filedir, filename) # forget about the path extension

            if entity is not None:
                if ENTITY_DB.get_entity_by_id(entity.id) is None:
                    ENTITY_DB.save_entity(entity)
                else:
                    ENTITY_DB.update_entity(entity)
            else:
                click.echo("Skip the existing entity for saving!")
        elif ret_code > 0:
            click.echo(click.style('Completed with error! Code is %s' % ret_code, fg='yellow'))
        else:
            pass # siglal, suppressed by click

        str_error = p.stderr.read()

        if len(str_error) > 0:
            click.echo(click.style('\nError:\n%s' % str_error, fg='red'))

        return ret_code == 0

    except subprocess.CalledProcessError, e:
        click.echo('Exception:\ncode:%s\noutput:%s' % (str(e.returncode), e.output))
        return False


def _validate_page_range(ctx, param, value):
    try:
        if '...' in value:
            start, end = map(int, value.split('...', 1))
            end += 1
        elif '..' in value:
            start, end = map(int, value.split('..', 1))
        else:
            start, end = 0, 0

        if start < end:
            return start, end
        else:
            raise ValueError()
    except ValueError:
        raise click.BadParameter('Page range need to be in format 1..10 or 1...10')


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    global DEBUG
    DEBUG = debug
    debug and click.echo('Debug mode is on')
    pass

@cli.command()
@click.argument('user-id', type=click.STRING)
@click.option('--exist-abort/--no-exist-abort', default=False)
@click.option('--url-only/--verbose', default=False)
@click.option('--download/--no-download', default=False)
@click.option('--page-range', '-p', callback=_validate_page_range, default='1...1000000')
@click.pass_context
def user(ctx, user_id, exist_abort, url_only, download, page_range):
    '''
    Parse the user page's videos
    '''

    if url_only:
        total_entities, page = fetch_user_list(user_id, start_page=page_range[0], end_page=page_range[1], urlPrinter=click.echo)
    else:
        total_entities, page = fetch_user_list(user_id, start_page=page_range[0], end_page=page_range[1], verbosePrinter=click.echo)

    if not url_only:
        click.echo("Fetched %d entities - %d pages in total." % (len(total_entities), page))

    if download:
        for entity in total_entities:
            result = download_video(entity)
            result or click.echo("Failed to download %s!" % entity.url)

@cli.command()
@click.argument('url', type=click.STRING)
@click.pass_context
def info(ctx, url):
    '''
    Parse the video detail page's info
    '''
    print_video_info(url)

@cli.command()
@click.argument('url', type=click.STRING)
@click.pass_context
def download(ctx, url):
    '''
    Download the video via you-get
    '''
    entity = _parse_video_entity_from_js(url)
    result = download_video(entity)
    result or click.echo("Failed to download %s!" % url)

@cli.command()
@click.pass_context
def list(ctx):
    '''
    Download the video via you-get
    '''
    total_entities = ENTITY_DB.get_all_entities()

    for entity in total_entities:
        click.echo(entity.output() + '\n')

