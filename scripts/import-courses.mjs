// Import course lessons and quizzes from the old WordPress site (Tutor LMS) into public/courses/<slug>.json.
// Lesson content is behind the paid course pages, so this needs a WordPress login:
//   WP_USER=<username> WP_APP_PASSWORD="<application password>" npm run import:courses
// Create the application password in WordPress: Users -> Profile -> Application Passwords (needs an admin account).
// Alternatively set TUTOR_API_KEY and TUTOR_API_SECRET (Tutor LMS -> Tools -> REST API).
//
// Tutor LMS endpoints differ between versions, so each lookup tries several known shapes and uses the first that answers.
// If none answer, the script stops with a clear message; the course pages keep showing "Lessons are on their way".
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';

const ROOT = resolve(dirname(new URL(import.meta.url).pathname), '..');
const DIR = join(ROOT, 'public', 'courses');
const BASE = process.env.WP_BASE || 'https://www.drinksnetwork.com.au';
const AUTH = process.env.WP_USER && process.env.WP_APP_PASSWORD
  ? 'Basic ' + Buffer.from(`${process.env.WP_USER}:${process.env.WP_APP_PASSWORD.replace(/\s+/g, '')}`).toString('base64')
  : process.env.TUTOR_API_KEY && process.env.TUTOR_API_SECRET
    ? 'Basic ' + Buffer.from(`${process.env.TUTOR_API_KEY}:${process.env.TUTOR_API_SECRET}`).toString('base64')
    : null;

// Old WordPress course slug -> new site slug (public/courses/<slug>.json)
const SLUGS = {
  'welcome-to-rice-spirits-explained': 'rice-spirits-explained',
  'welcome-to-rice-wine-explained': 'rice-wine-explained',
  'whisky-explained-master-the-art-of-whisky-from-grain-to-glass': 'whisky-explained',
  'bourbon-masterclass-drinks-network': 'bourbon-explained',
  'tequila-explained-the-ultimate-course-on-tequila-tequila-cocktails': 'tequila-explained',
};

if (!AUTH) {
  console.error('Missing login. Set WP_USER and WP_APP_PASSWORD (WordPress -> Users -> Profile -> Application Passwords), or TUTOR_API_KEY and TUTOR_API_SECRET.');
  process.exit(1);
}

async function get(path) {
  const r = await fetch(BASE + path, { headers: { Authorization: AUTH, 'User-Agent': 'DrinksNetwork-course-import' } });
  if (!r.ok) throw new Error(`${r.status} ${path}`);
  const j = await r.json();
  return j && j.data !== undefined && j.status_code ? j.data : j; // Tutor wraps results as {status_code, data}
}
async function first(paths) {
  const errs = [];
  for (const p of paths) { try { const d = await get(p); if (d && (!Array.isArray(d) || d.length || paths.length === 1)) return d; } catch (e) { errs.push(e.message); } }
  throw new Error('none of: ' + errs.join(' | '));
}
const arr = d => Array.isArray(d) ? d : (d && Array.isArray(d.data) ? d.data : d ? [d] : []);
const txt = v => (v && typeof v === 'object' ? (v.rendered ?? v.raw ?? '') : v ?? '');
const clean = h => String(h).replace(/<script[\s\S]*?<\/script>/gi, '').replace(/<style[\s\S]*?<\/style>/gi, '')
  .replace(/\s(on\w+|class|id|style|data-[\w-]+|srcset|sizes)="[^"]*"/gi, '');

function media(lesson) {
  const v = lesson.video || lesson._video || (lesson.meta && lesson.meta._video) || {};
  const src = Array.isArray(v) ? v[0] : v;
  const url = src.source_youtube || src.source_external_url || src.source_html5 || src.source_video_id || src.url || '';
  const yt = String(url).match(/(?:youtu\.be\/|v=|embed\/)([\w-]{11})/);
  if (yt || src.source === 'youtube') return { type: 'youtube', id: yt ? yt[1] : url };
  if (/\.(mp3|m4a|wav|ogg)(\?|$)/i.test(url)) return { type: 'audio', src: url };
  if (url) return { type: 'video', src: url };
  const body = txt(lesson.content || lesson.post_content);
  const audio = body.match(/<audio[^>]+src="([^"]+)"/i) || body.match(/src="([^"]+\.(?:mp3|m4a|wav))"/i);
  if (audio) return { type: 'audio', src: audio[1] };
  const ytIn = body.match(/(?:youtube\.com\/embed\/|youtu\.be\/|watch\?v=)([\w-]{11})/);
  if (ytIn) return { type: 'youtube', id: ytIn[1] };
  return { type: 'tts' }; // read aloud
}

function questions(list) {
  return arr(list).map(q => {
    const answers = arr(q.question_answers || q.answers || q.answer || []);
    const options = answers.map(a => String(a.answer_title ?? a.title ?? a.text ?? '').trim()).filter(Boolean);
    const answer = answers.findIndex(a => a.is_correct === '1' || a.is_correct === 1 || a.is_correct === true || a.correct === true);
    return { q: String(q.question_title ?? q.title ?? '').trim(), options, answer, explain: String(q.answer_explanation ?? q.explanation ?? '').replace(/<[^>]+>/g, '').trim() || undefined };
  }).filter(q => q.q && q.options.length >= 2 && q.answer >= 0);
}

const courses = arr(await first(['/wp-json/tutor/v1/courses?per_page=100', '/wp-json/wp/v2/courses?per_page=100&context=edit', '/wp-json/wp/v2/courses?per_page=100']));
console.log(`Found ${courses.length} courses`);
let imported = 0;
for (const c of courses) {
  const wpSlug = c.post_name || c.slug;
  const slug = SLUGS[wpSlug] || wpSlug;
  const id = c.ID || c.id;
  try {
    const topics = arr(await first([`/wp-json/tutor/v1/topics?course_id=${id}`, `/wp-json/tutor/v1/course-topic/${id}`, `/wp-json/wp/v2/topics?parent=${id}&per_page=100&context=edit`]));
    const lessons = [];
    for (const t of topics) {
      const tid = t.ID || t.id;
      const ls = arr(await first([`/wp-json/tutor/v1/lessons?topic_id=${tid}`, `/wp-json/tutor/v1/topic-lesson/${tid}`, `/wp-json/wp/v2/lesson?parent=${tid}&per_page=100&context=edit`]).catch(() => []));
      let quizQs = [];
      try {
        const quizzes = arr(await first([`/wp-json/tutor/v1/quizzes?topic_id=${tid}`, `/wp-json/tutor/v1/quiz/${tid}`]));
        for (const qz of quizzes) quizQs = quizQs.concat(questions(await first([`/wp-json/tutor/v1/quiz-questions?quiz_id=${qz.ID || qz.id}`, `/wp-json/tutor/v1/quiz-question-answer/${qz.ID || qz.id}`]).catch(() => [])));
      } catch { /* topic without a quiz */ }
      ls.forEach((l, i) => lessons.push({
        id: `l${lessons.length + 1}`,
        title: String(txt(l.post_title || l.title)).trim(),
        review: clean(txt(l.post_content || l.content)),
        listen: media(l),
        // a topic's quiz is asked after the last lesson in that topic
        questions: i === ls.length - 1 ? quizQs : [],
      }));
    }
    const dest = join(DIR, `${slug}.json`);
    const prev = existsSync(dest) ? JSON.parse(readFileSync(dest, 'utf8')) : {};
    const out = { ...prev, slug, title: prev.title || String(txt(c.post_title || c.title)).trim(), description: prev.description || String(txt(c.post_excerpt || c.excerpt)).replace(/<[^>]+>/g, '').trim(), lessons };
    mkdirSync(DIR, { recursive: true });
    writeFileSync(dest, JSON.stringify(out, null, 2));
    const withQ = lessons.filter(l => l.questions.length).length;
    console.log(`${slug}: ${lessons.length} lessons, ${withQ} with questions${withQ < lessons.length ? ' (lessons without questions show "Complete lesson"; add questions in the JSON to gate them)' : ''}`);
    imported++;
  } catch (e) {
    console.warn(`${slug}: could not import (${e.message})`);
  }
}
console.log(`Done: ${imported} of ${courses.length} courses imported. Then run "npm run import:wordpress" to copy course images into the project, and "npm run build".`);
