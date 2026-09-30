// threads-scrape-verify.js
// Self-check script to validate JSON extraction from Threads pages
// Usage: node threads-scrape-verify.js <path-to-html-file>

const fs = require('fs');
const path = require('path');

function extractNextData(html) {
  const regex = /<script id="__NEXT_DATA__" type="application\/json">([\s\S]*?)<\/script>/;
  const match = html.match(regex);
  if (!match) return null;
  try {
    return JSON.parse(match[1]);
  } catch (e) {
    console.error('Failed to parse __NEXT_DATA__:', e.message);
    return null;
  }
}

function findPosts(data) {
  const posts = [];
  function traverse(obj) {
    if (obj && typeof obj === 'object') {
      if (obj.searchResults && obj.searchResults.edges) {
        for (const edge of obj.searchResults.edges) {
          const node = edge.node;
          const thread = node.thread;
          if (thread && thread.thread_items) {
            for (const item of thread.thread_items) {
              const post = item.post;
              if (post && post.caption) {
                posts.push(post);
              }
            }
          }
        }
      }
      for (const key of Object.keys(obj)) {
        traverse(obj[key]);
      }
    } else if (Array.isArray(obj)) {
      for (const item of obj) traverse(item);
    }
  }
  traverse(data);
  return posts;
}

// Main
const filePath = process.argv[2];
if (!filePath) {
  console.error('Usage: node threads-scrape-verify.js <html-file>');
  process.exit(1);
}

const html = fs.readFileSync(filePath, 'utf8');
const nextData = extractNextData(html);

if (!nextData) {
  console.error('❌ No __NEXT_DATA__ found in HTML');
  process.exit(1);
}

const posts = findPosts(nextData);
console.log(`✅ Found ${posts.length} posts with captions`);

if (posts.length > 0) {
  console.log('\nSample post:');
  console.log(JSON.stringify(posts[0], null, 2).slice(0, 500) + '...');
}

process.exit(0);