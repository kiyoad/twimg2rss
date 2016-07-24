# (WIP)twimg2rss
Make a RSS2.0 XML file from your Twitter timeline that contains the images.

## Requirements
twimg2rss requires the following to run:
- Python 3.4.3+
- Some PyPI packages(see requirements.txt)

If you want to use the online feed reader(such as Feedly), you must prepare an http server like Nginx in order to publish the RSS2.0 XML file in the Internet.

## Usage
### Get your Twitter Consumer Key, Consumer Secret, Access Token and Access Token Secret
Since twimg2rss is to use the Twitter API, you must obtain a consumer key, etc. that correspond to your Twitter account from [apps.twitter.com](https://apps.twitter.com/).

The settings are as follows.
- Access level: Read-only
- Callback URL: None
- Callback URL Locked: No
- Sign in with Twitter: No

### Modify config.ini
The config.ini and the *.py files are placed in the same directory.
<dl>
<dt>tw_consumer_key</dt>
<dd>Your Twitter Consumer Key (API Key).</dd>

<dt>tw_consumer_secret</dt>
<dd>Your Twitter Consumer Secret (API Secret).</dd>

<dt>tw_access_token</dt>
<dd>Your Twitter Access Token.</dd>

<dt>tw_access_token_secret</dt>
<dd>Your Twitter Access Token Secret.</dd>

<dt>log_file</dt>
<dd>The twimg2rss log file.</dd>

<dt>max_parsed_id_file</dt>
<dd>The maximum number of processed Twitter ID savedfile. Automatically savedfile will be created if it does not exist.</dd>

<dt>timeline_json_file</dt>
<dd>Your Twitter timeline savedfile. Use Twitter API [GET statuses/home_timeline](https://dev.twitter.com/rest/reference/get/statuses/home_timeline).</dd>

<dt>log_timeline_json_dir</dt>
<dd>The backup directory for Twitter timeline savedfile. filename format: timeline_YYYYmmdd-HHMMSS.json.</dd>

<dt>rss_xml_file</dt>
<dd>The RSS2.0 XML file(temporary) that is created by twimg2rss.</dd>

<dt>release_rss_xml_file</dt>
<dd>The RSS2.0 XML file that is provided by the http server. It is copied from the rss_xml_file.</dd>

<dt>rss_xml_limit</dt>
<dd>Limit of the number of RSS2.0 XML items in the rss_xml_file.</dd>

<dt>timeline_db_file</dt>
<dd>The Twitter timeline DB(sqlite3) file that updates by the timeline_json_file. The rss_xml_file is created based on this.</dd>

<dt>timeline_db_period</dt>
<dd>The period(sec.) that maintain the timeline DB data. Of your Twitter time line data, from the most recent ones, toward the past, to have the data for that time period. However, the number of items can not be a more than the rss_xml_limit.</dd>

<dt>rss_xml_url</dt>
<dd>The RSS2.0 XML URL that you publish in the Internet.</dd>

<dt>homepage_url</dt>
<dd>The homepage URL related to rss_xml_url. But where there is no need to provide the content. It may be left in the default sample index.html.</dd>

<dt>time_difference_from_utc</dt>
<dd>Time difference from UTC(Ex. JST: 9).</dd>

<dt>url_db_file</dt>
<dd>The DB(sqlite3) file of the URL contained in the text field of tweets. Tweets with any URLs contained in this DB is ignored. That does not create an RSS feed from this tweets. This is used when the same tweet more than one person was retweets, to leave the first one.</dd>

<dt>url_db_period</dt>
<dd>The period(sec.) that maintain the URL DB data. After the unique URL appears during this period, tweets containing the same URL is ignored.</dd>

<dt>ng_word_list_file</dt>
<dd>The NG word list file. It is a file of the UTF-8 format, and includes a one-by-one NG word on a single line. Tweets including the NG words are ignored.</dd>
</dl>

### Run twimg2rss
After the modified config.ini and *.py was confirmed to be in the same directory, run the twimg2rss.py.
```bash
$ ./twimg2rss.py
```

If there is no error, the following files are created.
<dl>
<dt>max_parsed_id_file</dt>
<dd>ASCII text file. Ex. : 757209410032676864</dd>

<dt>timeline_db_file</dt>
<dd>sqlite3 database file.</dd>

<dt>url_db_file</dt>
<dd>sqlite3 database file.</dd>

<dt>rss_xml_file</dt>
<dd>The RSS2.0 formatted XML file.</dd>

<dt>release_rss_xml_file</dt>
<dd>Same as the rss_xml_file.</dd>

<dt>log_file</dt>
<dd>UTF-8 text file.</dd>
</dl>

And the backup file of Twitter timeline savedfile is created in the log_timeline_json_dir. This file is not particularly necessary if is created the rss_xml_file. Therefore, the old files can be deleted by the crontab.
```crontab
0 * * * * find /your/log_timeline_json_dir/directory -mtime +7 -exec rm {} \;
```

### Notes
Since twimg2rss is using the Twitter API that 'GET statuses / home_timeline', it can run up to 15 times in 15 minutes. If you are using a different Twitter client on the same Twitter account, this limit will be more tightly. In the API you can get tweets of up to 200. So that the new tweet does not exceed the 200 items, please adjust the interval of twimg2rss. The remaining number of times of the Twitter API is output to log_file as follows.
```
2016-07-24 23:43:02,895 INFO get_timeline "Number of tweets: 26"
2016-07-24 23:43:02,895 INFO get_timeline "API remain: 13"
2016-07-24 23:43:02,896 INFO get_timeline "API reset: Sun, 24 Jul 2016 14:53:02 +0000"
2016-07-24 23:43:03,415 INFO make_xml "max_parsed_id = 757224560877895680"
2016-07-24 23:43:03,415 INFO make_xml "newest_created_at = 2016/07/24 14:42:58"
2016-07-24 23:43:03,415 INFO make_xml "obtained raw timeline count = 26"
2016-07-24 23:43:03,416 INFO make_xml "added media timeline count  = 10"
2016-07-24 23:43:03,416 INFO make_xml "total media timeline count  = 999"
```

The remaining 13 times in this example.

twimg2rss also might be more convenient to run in crontab if you want to use the online feed reader.
```crontab
8,23,38,53 * * * * /your/twimg2rss/directory/twimg2rss.py
```

In this case, of course, you are already built a http server like Nginx. And the release_rss_xml_file shall file path corresponding to rss_xml_url is specified.


## License

twimg2rss is licensed under the MIT license.
Copyright (c) 2016, kiyoad
