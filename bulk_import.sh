#!/bin/bash

KEY=093D38CA-C527-400E-8D2A-B414E21B9E04

rm charts.db

python import_vchart_1.py http://www.vmusic.com.au/api/1.0/chart/v-music-video-chart?apikey=$KEY
python import_vchart_1.py http://www.vmusic.com.au/api/1.0/chart/australian-singles-chart?apikey=$KEY
#python import_vchart_1.py http://www.vmusic.com.au/api/1.0/chart/itunes-top-40-singles-chart?apikey=$KEY
#python import_vchart_1.py http://www.vmusic.com.au/api/1.0/chart/billboard-top-40-singles-chart?apikey=$KEY
#python import_vchart_1.py http://www.vmusic.com.au/api/1.0/chart/uk-top-40-singles-chart?apikey=$KEY
#python import_vchart_1.py http://www.vmusic.com.au/api/1.0/mostplayed/chv?apikey=$KEY
#python import_vchart_1.py http://www.vmusic.com.au/api/1.0/mostplayed/max?apikey=$KEY
#python import_vchart_1.py http://www.vmusic.com.au/api/1.0/mostplayed/cmc?apikey=$KEY
