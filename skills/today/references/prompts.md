# Seed & Feed Patterns

Templates for generating briefing content. Each pattern includes
the context signal (when to use it) and the output shape.

## Seed Meta-rules

1. **Statement, not question** — give the user something to react to
2. **Specificity** — quote notes, use [[wikilinks]], cite exact phrases
3. **Assertive** — take a position, make a claim, draw a connection
4. **Concise** — 2-4 sentences max
5. **Grounded** — only vault content, never generic advice
6. **Language** — write in user's journal language (Russian)
7. **Direct wikilinks ALWAYS** — every reference must be a clickable `[[wikilink]]`. Daily notes: `[[periodic/daily/2026-02-05|05.02]]`. Never "в записи от 05.02" without a link

---

## Seed Patterns

### Pattern: Synthesis

**Signal:** Two vault notes share a theme but aren't linked to each other.

```
[[Note A]] про [X] и [[Note B]] про [Y] — это один и тот же паттерн: [паттерн].
Если это так, то [следствие/импликация].
```

### Pattern: Contradiction

**Signal:** A vault note contradicts recent journal behavior or another note.

```
В [[заметке]] ты писал "[цитата]". Но последние записи показывают [противоположное поведение].
Либо принцип неверный, либо ты его не применяешь.
```

### Pattern: Idea Extension

**Signal:** Recent journal entry or note contains a thought that can be pushed further.

```
Твоя мысль про [X] из [[заметки/записи]] имеет неочевидное продолжение:
если [X] верно, то из этого следует [Y]. А значит [Z].
```

### Pattern: Resource Highlight

**Signal:** A source note (30+ days old) has a specific insight relevant to current work.

```
В [[источнике]] [автор] утверждает [конкретный тезис] — это напрямую
касается того, над чем ты работаешь в [[проекте/заметке]].
```

### Pattern: Project Insight

**Signal:** Active project has a section that could benefit from a vault note's perspective.

```
Для [[проекта]]: секция [X] станет сильнее, если подойти со стороны
[[заметки про Y]]. Конкретно: [предложение].
```

### Pattern: Pattern Recognition

**Signal:** Same theme appears across 3+ different contexts (notes, journal, projects).

```
За последнюю неделю ты возвращаешься к [теме] с разных сторон:
[[заметка1]], [[заметка2]], записи в дневнике. Тут есть ненаписанная заметка про [концепт].
```

### Pattern: Forgotten Thread

**Signal:** An old note (30+ days) is directly relevant to something the user wrote recently.

```
Месяц назад в [[старой заметке]] ты развивал [мысль]. С тех пор
ты написал [[новую заметку]] про [связанное]. Эти две вещи стоит соединить:
[конкретное предложение].
```

### Pattern: Action Seed

**Signal:** Recent journal entries mention wanting to do something; vault has relevant material.

```
Ты писал про "[хочу/нужно/планирую X]". В хранилище уже есть материал:
[[заметка A]] про [аспект X], [[источник B]] с [конкретным методом].
Начни с [конкретный первый шаг].
```

---

## Materials Selection

### Priority Order

1. **Project-relevant, unlinked** — note matches active project but not connected
2. **Journal-theme match** — note on topic user keeps writing about
3. **Forgotten source** — source 30+ days old, relevant to current work
4. **Contradiction** — note that challenges recent thinking
5. **Unfinished work** — addition/experiment started but not developed

### Format per Material

```
- [[note title]] — [why it's relevant, 5-10 words, concrete]
```

**Good annotations:**
- `касается секции про Zotero в [[проекте]]`
- `противоречит тому, что ты писал вчера про X`
- `дочитал до середины, рейтинг 🌔, есть метод для Y`
- `не трогал 2 месяца, но напрямую связан с [темой]`

**Bad annotations:**
- `может быть полезно`
- `интересная заметка`
- `связано с темой`

---

## Project Feed Patterns

### Pattern: Unconnected Knowledge

**Signal:** Note shares `category`/`meta`/`problem` with project, not linked.

```
- [[Project]] 🟦: см. [[заметку]] — общая иерархия ([meta/category]), усилит [секцию]
```

### Pattern: Forgotten Source

**Signal:** Source covers project topic, not referenced.

```
- [[Project]] 🟦: см. [[источник]] — [автор] про [тему], рейтинг [N], не использован
```

### Pattern: Cross-Pollination

**Signal:** Note linked in project A, relevant to project B.

```
- [[Project B]] 🟥: см. [[заметку]] — уже в [[Project A]], релевантна и для [аспекта B]
```

### Pattern: Addition Match

**Signal:** An experiment/report/log relates to project themes.

```
- [[Project]] 🟦: см. [[дополнение]] — твой [эксперимент/отчёт] про [тему], пригодится для [секции]
```

---

## Threads Format

Collect from recent daily notes. Compact format:

```
- "нужно сделать видео по Zotero" (3 дня назад) — не сделано
- [ ] задача из позавчера — не закрыта
- Незаконченная мысль про [тему]: "[цитата]..."
```

### Selection
- Max 3 threads
- Prioritize: stated intentions > open tasks > trailing thoughts
- Skip threads older than 7 days (they're probably dead)
- Skip threads the user explicitly resolved

---

## Briefing Assembly Algorithm

1. Gather all context (daily notes + vault activity + active projects)
2. Generate seed — pick the STRONGEST pattern match:
   - Synthesis > Contradiction > Idea Extension > Project Insight > Pattern Recognition > Resource Highlight > Forgotten Thread > Action Seed
3. Select materials — 2-5 notes, strongest relevance first
4. Build project feed — for each active project, find unlinked matches
5. Collect threads — 2-3 unfinished items from recent days
6. Assemble briefing callout
7. Write into daily note (append after existing content)
8. Confirm in chat (1-2 lines)

### When picking the seed
- If contradiction exists — always prefer it (strongest reaction trigger)
- If no contradiction — prefer synthesis or idea extension
- Avoid action seed unless nothing else matches (it's the weakest)
- The seed must make the user want to WRITE something in response
