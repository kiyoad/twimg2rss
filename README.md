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
<dd>The period that maintain the timeline DB data. Of your Twitter time line data, from the most recent ones, toward the past, to have the data for that time period. However, the number of items can not be a more than the rss_xml_limit.</dd>

<dt>rss_xml_url</dt>
<dd>The RSS2.0 XML URL that you publish in the Internet.</dd>

<dt>homepage_url</dt>
<dd>The homepage URL related to rss_xml_url. But where there is no need to provide the content. It may be left in the default sample index.html.</dd>

<dt>time_difference_from_utc</dt>
<dd>Time difference from UTC(Ex. JST: 9).</dd>

<dt>url_db_file</dt>
<dd>The DB(sqlite3) file of the URL contained in the text field of Tweets. Tweets with any URLs contained in this DB is ignored. That does not create an RSS feed from this tweets. This is used when the same tweet more than one person was retweets, to leave the first one.</dd>

<dt>url_db_period</dt>
<dd>The period that maintain the URL DB data. After the unique URL appears during this period, tweets containing the same URL is ignored.</dd>

<dt>ng_word_list_file</dt>
<dd>The NG word list file. It is a file of the UTF-8 format, and includes a one-by-one NG word on a single line. Tweets including the NG words are ignored.</dd>
</dl>

## License

twimg2rss is licensed under the MIT license.
Copyright (c) 2016, kiyoad
