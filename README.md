# So Hot Right Now

Manages a Spotify playlist updated weekly of only debut tracks on Billboard charts. Available on [Spotify](https://play.spotify.com/user/therockstorm/playlist/5bzZgrRBufw9laiTsYM8rJ).

Ran from the command line or as a scheduled [AWS Lambda](https://aws.amazon.com/lambda/) function, it gathers only tracks newly added to Billboard charts and adds them to a Spotify playlist. The oldest are removed once the playlist exceeds 100 tracks. Uses [serverless](http://serverless.com), [billboard-charts](https://github.com/guoguo12/billboard-charts), and [spotipy](https://github.com/plamere/spotipy).

## License
Copyright (c) 2016 Rocky Warren  
Licensed under the MIT license.
