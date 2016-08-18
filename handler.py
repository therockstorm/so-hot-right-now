import os
import sys
import boto3
sys.path.append(os.path.join("venv", "lib", "python2.7", "site-packages"))

from billboard import ChartData
from itertools import chain
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth


class BillboardFetcher(object):
    CHARTS = ["hot-100", "youtube", "spotify-viral-50", "spotify-velocity", "digital-songs",
        "radio-songs", "streaming-songs", "twitter-top-tracks", "twitter-emerging-artists",
        "on-demand-songs", "lyricfind-us"]

    def get_debut_ids(self):
        return set(chain.from_iterable([self._get_debut_ids(chart) for chart in self.CHARTS]))

    def _get_debut_ids(self, chart):
        return [track.spotifyID for track in ChartData(chart) if track.weeks == 1 and track.spotifyID]


class SpotifyPlaylistUpdater(object):
    USERNAME_KEY = "username"
    TOKEN_INFO_KEY = "token_info"
    SPOTIFY_SCOPE = "playlist-modify-public"
    MAX_TRACKS = 200

    def __init__(self, client_id, client_secret, redirect_uri):
        dynamo = boto3.resource("dynamodb", endpoint_url="https://dynamodb.us-west-2.amazonaws.com")
        self.table = dynamo.Table("spotify")
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def update(self, user, playlist_id):
        spotify = Spotify(auth=self._get_token(user))
        existing_ids = self._get_existing_ids(user, playlist_id, spotify)
        add_ids = self._get_ids_to_add(existing_ids, BillboardFetcher().get_debut_ids())

        if add_ids:
            print("Adding {0} tracks.".format(len(add_ids)))
            spotify.user_playlist_add_tracks(user, playlist_id, add_ids)
        else:
            print("No tracks to add.")

        remove_ids = self._get_ids_to_remove(existing_ids, len(existing_ids) + len(add_ids))

        if remove_ids:
            spotify.user_playlist_remove_all_occurrences_of_tracks(user, playlist_id, remove_ids)

    def _get_existing_ids(self, user, playlist_id, spotify):
        playlist = spotify.user_playlist_tracks(user, playlist_id, "items.track.id")
        return [item["track"]["id"] for item in playlist["items"] if item]

    def _get_ids_to_add(self, existing_ids, debut_ids):
        return [id for id in debut_ids if id not in existing_ids]

    def _get_ids_to_remove(self, existing_ids, size):
        remove_cnt = size - self.MAX_TRACKS if size > self.MAX_TRACKS else 0
        print("Removing {0} of {1} tracks.".format(remove_cnt, size))
        return existing_ids[:remove_cnt]

    def _get_token(self, user):
        res = self.table.get_item(Key={self.USERNAME_KEY: user})
        oauth = SpotifyOAuth(client_id=self.client_id, client_secret=self.client_secret,
            redirect_uri=self.redirect_uri, scope=self.SPOTIFY_SCOPE)
        token_info = oauth._refresh_access_token(res["Item"][self.TOKEN_INFO_KEY]["refresh_token"])
        self._update_token_info(user, token_info)
        return token_info["access_token"]

    def _update_token_info(self, user, token):
        replacement = ":e"
        self.table.update_item(
            Key={self.USERNAME_KEY: user},
            UpdateExpression="SET {0} = {1}".format(self.TOKEN_INFO_KEY, replacement),
            ExpressionAttributeValues={replacement : token})


def handle(event, context):
    SpotifyPlaylistUpdater(
        client_id="",
        client_secret="",
        redirect_uri="").update(
            user="", playlist_id="")


if __name__ == "__main__":
    handle(None, None)
