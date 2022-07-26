# crawsqueal 🦜

Crawl a website, save its content to a SQLite database, and search it in your browser.

![crawsqueal-screenshot](screenshot.png)

## Quickstart

Run the crawler without needing to download this repository:

```
npx cfpb/crawsqueal
```

It'll create a SQLite database named `./crawl.sqlite3`, crawl the consumerfinance.gov website, and create a record for every page that has a unique URL (including query params and hashes). This takes a couple of hours to complete.

## Running the crawler locally

To run using a local copy of this repository:

```
yarn
yarn start
```

You can optionally pass a custom filename for the database:

```
yarn start cfpb/crawsqueal db.sqlite3
```

You can also optionally pass an alternate domain name to crawl:

```
yarn start db.sqlite3 https://beta.consumerfinance.gov/
```

### Experimental: Generate a crawl database from a WARC archive

A [WARC](https://archive-it.org/blog/post/the-stack-warc-file/)
(Web ARChive)  is a container file standard for storing web content in its original context,
maintained by the International Internet Preservation Consortium (IIPC).

Many tools exist to generate WARCs.
The Internet Archive maintains the
[Heritrix](https://github.com/internetarchive/heritrix3) web crawler that can generate WARCs;
a longer list of additional tools for this purpose can be found
[here](http://dhamaniasad.github.io/WARCTools/).

The common command-line tool
[wget](https://wiki.archiveteam.org/index.php/Wget_with_WARC_output)
can also be used to generate WARCs. A sample script to do so can be found in this repository,
and can be invoked like this:

```sh
./wget_crawl.sh https://www.consumerfinance.gov/
```

This will generate a WARC archive file named `crawl.warc.gz`.
This file can then be converted to a SQLite database using a command like:

```sh
viewer/manage.py warc_to_db crawl.warc.gz crawl.sqlite3
```

Alternatively, to dump a WARC archive file to a set of CSVs:

```sh
viewer/manage.py warc_to_csv crawl.warc.gz
```

## How to query the crawler database

You can use the
[SQLite command-line client](https://www.sqlite.org/cli.html)
to make queries against the crawl result,
or a graphical client such as [DB4S](https://github.com/sqlitebrowser/sqlitebrowser) if you prefer.

To run the command-line client:

```
sqlite3 crawl.sqlite3
```

The following examples describe some common use cases.

### Dump database statistics

To list the total number of URLs and crawl timestamps:

```sql
sqlite> SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM warc_page;
23049|2022-07-20 02:50:02|2022-07-20 08:35:23
```

Note that page data is stored in a table named `warc_page`.

### List pages that link to a certain URL

```sql
sqlite> SELECT DISTINCT url
FROM warc_page
INNER JOIN warc_page_links ON (warc_page.id = warc_page_links.page_id)
INNER JOIN warc_link ON (warc_page_links.link_id = warc_link.id)
WHERE href LIKE "/plain-writing/"
ORDER BY url ASC;
```

To dump results to a CSV instead of the terminal:

```sql
sqlite> .mode csv
sqlite> .output filename.csv
sqlite> ... run your query here
sqlite> .output stdout
sqlite> .mode list
```

To search with wildcards, use the `%` character:

```sql
sqlite> SELECT DISTINCT url
FROM warc_page
INNER JOIN warc_page_links ON (warc_page.id = warc_page_links.page_id)
INNER JOIN warc_link ON (warc_page_links.link_id = warc_link.id)
WHERE href LIKE "/about-us/blog/"
ORDER BY url ASC;
```

### List pages that contain a specific design component

```sql
sqlite> SELECT DISTINCT url
FROM warc_page
INNER JOIN warc_page_components ON (warc_page.id = warc_page_components.page_id)
INNER JOIN warc_component ON (warc_page_components.component_id = warc_component.id)
WHERE warc_component.class_name LIKE "o-featured-content-module"
ORDER BY url ASC
```

See the [CFPB Design System](https://cfpb.github.io/design-system/)
for a list of common components used on CFPB websites.

### List pages with titles containing a specific string

```sql
SELECT url FROM warc_page WHERE title LIKE "%housing%" ORDER BY url ASC;
```

### List pages with body text containing a certain string

```sql
sqlite> SELECT url FROM warc_page WHERE text LIKE "%diamond%" ORDER BY URL asc;
```

### List pages with HTML containing a certain string

```sql
sqlite> SELECT url FROM warc_page WHERE html LIKE "%<br>%" ORDER BY URL asc;
```

## Running the viewer application

From the repo's root, compile front-end assets:

```
yarn
yarn build
```

Create a Python virtual environment and install requirements:

```
python3.8 -m venv venv
source venv/bin/activate
pip install -r viewer/requirements.txt
```

Optionally set the `CRAWL_DATABASE` environment variable to point to a local crawl database:

```
export CRAWL_DATABASE=cfgov.sqlite3
```

Finally, run the Django webserver:

```
viewer/manage.py runserver
```

The viewer application will be available locally at http://localhost:8000.

## Development

### Testing

To run Python unit tests, use [`tox`](https://tox.wiki/en/latest/):

```
tox
```

### Sample database file

This repository includes a sample database file ([sample.sqlite3](./sample.sqlite3)).
This file is used by the viewer application when no other crawl database file has been specified.
It is also used for Python unit testing purposes.

The source website content used to generate this file is included in this repository
under the [sample](./sample) subdirectory. To regenerate the test database from this content,
first serve the sample website locally:

```
cd sample
python -m http.server
```

Then, in another terminal at the repository root, start a crawl against the locally running site:

```
./wget_crawl.sh http://localhost:8000
```

This will create a WARC archive named `crawl.warc.gz` in your working directory.
Next, convert this to a test database file:

```
viewer/manage.py warc_to_db --recreate crawl.warc.gz sample.sqlite3
```

This will replace the existing sample database file.

----

## Open source licensing info
1. [TERMS](TERMS.md)
2. [LICENSE](LICENSE)
3. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)
