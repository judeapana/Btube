import math
from concurrent.futures.thread import ThreadPoolExecutor
import pytube
from flask import Blueprint, request, jsonify, abort
from urllib import parse

api = Blueprint("api", __name__)


@api.route('/single', methods=["GET"])
def accept_single_video():
    if request.method == 'GET':
        url = request.args.get('url')
        if url is None:
            return jsonify(error="Youtube Link Not Found")
        else:
            if "list" in url:
                return jsonify(
                    error="Only Single Videos Are Allowed In This Section. So Please Goto The Playlist Section")
            if "v" not in url:
                return jsonify(error="Youtube Link You Inserted Is Incorrect")

            with ThreadPoolExecutor(max_workers=20) as executor:
                future = executor.submit(_process_single_video, url)
            return jsonify(future.result())
    abort(status=403)


def _process_video_size(video_size):
    num_bytes_in_megabyte = math.pow(10, 6)
    file_size_in_megabyte = math.ceil(video_size / num_bytes_in_megabyte)
    return file_size_in_megabyte


def _populate_playlist_urls(url):
    res = pytube.Playlist(url)
    res.populate_video_urls()
    return res.video_urls


def _process_single_video(url):
    try:
        res = pytube.YouTube(url)
        videos = res.streams.filter(file_extension='mp4', progressive=True).order_by('resolution').asc().all()
        meta = []
        for video in videos:
            mb_size = _process_video_size(video.filesize)
            mime_type = video.mime_type
            list_video_data = {'url': f'{video.url}&title={parse.quote(res.title)}', 'mime_type': mime_type,
                               'resolution': video.resolution,
                               'size': mb_size}
            meta.append(list_video_data)
        return {'meta': meta, 'title': res.title,
                'thumbnail_url': res.thumbnail_url,
                'length': math.ceil(int(res.length) / 60),
                'descp': res.description,
                'views': res.views,
                'rating': res.rating}
    except Exception as e:
        if "regex" in e.__str__():
            return {'error': "Youtube Url doesnt not match any known format"}
        elif "unavailable" in e.__str__():
            return {'error': "No Youtube video found. Please check URL"}
        else:
            return {'error': e.__str__()}


@api.route('/multiple', methods=["GET"])
def accept_multiple_video():
    if request.method == 'GET':
        url_playlist = request.args.get('playlist')
        url_list = request.args.get('list')
        url = f'{url_playlist}&list={url_list}'
        print(url)
        if url is None:
            return jsonify(error="Youtube Link Not Found")
        if "&list" not in url and "?v" not in url:
            return jsonify(error="You have inserted a wrong playlist url")

        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = []
            list_of_urls = _populate_playlist_urls(url)
            for single_url in list_of_urls:
                future = executor.submit(_process_single_video, single_url)
                futures.append(future)

        with ThreadPoolExecutor(max_workers=20) as executor2:
            def get_all_url_datum():
                all_data = []
                _720p_urls = []
                _320p_urls = []
                for single_future in futures:
                    all_data.append(single_future.result())
                for i in range(0, len(all_data)):
                    _320p_urls.append(all_data[i]['meta'][0]['url'])
                    _720p_urls.append(all_data[i]['meta'][1]['url'])
                all_data.append({'320p_links': _320p_urls})
                all_data.append({'720p_links': _720p_urls})
                return all_data

            future1 = executor2.submit(get_all_url_datum)
        return jsonify(future1.result())
    abort(status=403)
