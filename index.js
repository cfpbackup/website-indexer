#!/usr/bin/env node

import cliProgress from 'cli-progress';
import colors from 'ansi-colors';
import Crawler from 'simplecrawler';
import { argv } from 'process';
import DB from './db.js';
import Parser from './parser.js';

let APPROX_NUM_PAGES = 25000;

// Set up the database
const dbLocation = argv[2] || './crawl.sqlite3';
const db = DB.connect(dbLocation);
db.createTables();

// Configure target website.
const startUrl = argv[3] || 'https://www.consumerfinance.gov/';

// Set up the CLI progress bar
console.log(`\n\nCrawling ${startUrl}...`);
const progressBar = new cliProgress.SingleBar({
  format: `| ${colors.cyan('{bar}')} | {percentage}% | {value}/{total} pages | {path}`,
  barCompleteChar: '\u2588',
  barIncompleteChar: '\u2591',
  hideCursor: true
});

progressBar.start(APPROX_NUM_PAGES, 0, {
  speed: "N/A"
});

// Set up the crawler
const crawler = new Crawler(startUrl);
crawler.host = new URL(startUrl).hostname;
crawler.maxConcurrency = 10;
crawler.filterByDomain = true;
crawler.parseHTMLComments = false;
crawler.parseScriptTags = false;
crawler.respectRobotsTxt = false;

// Ignore external site URLs
crawler.addFetchCondition(function (queueItem, referrerQueueItem, callback) {
  const regex = /(\/external-site\/)/i;
  callback(null, !queueItem.path.match(regex));
});

// Don't mess with these filetypes
crawler.addFetchCondition((queueItem, referrerQueueItem, callback) => {
  const downloadRegex =
    /\.(png|jpg|jpeg|gif|ico|css|js|csv|doc|docx|svg|pdf|xls|json|ttf|xml|woff|eot|zip|wav)/i;
  callback(null, !queueItem.url.match(downloadRegex));
});

// Do cool stuff after a page is fetched
crawler.on('fetchcomplete', async function (queueItem, responseBuffer) {
  const contentType = (queueItem.stateData && queueItem.stateData.contentType) || '';

  if (!contentType.includes('text/html') || queueItem.host !== crawler.host) {
    return;
  }

  const parser = new Parser(responseBuffer);

  const record = {
    path: queueItem.path,
    title: parser.getTitle(),
    components: parser.getComponents(),
    links: parser.getLinks(),
    pageHash: parser.getHash(),
    pageHtml: await parser.getHtml(),
    timestamp: new Date()
  };

  try {
    db.insert(record);
    progressBar.increment({path: record.path})
  } catch (error) {
    console.error("Something went horribly wrong and there's nothing to handle the exception. Oh no.");
  }
});

crawler.on('complete', function () {
  console.log('All done!');
  progressBar.stop();
});

crawler.start();
