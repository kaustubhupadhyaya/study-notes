# Study notes: distributed analytics and the lakehouse

Eight self-contained HTML pages on the storage and query layer of a modern analytics platform. They cover the same material from first principles, with worked sizing, failure drills and short answer scripts.

## Pages

| Page | Topic |
|---|---|
| [`pages/dist.html`](pages/dist.html) | Distributed databases: sharing, replication, consensus, failure |
| [`pages/mpp.html`](pages/mpp.html) | MPP performance: scaling, layout, joins, memory, statistics |
| [`pages/obj.html`](pages/obj.html) | Object storage: the S3 model, on-prem options, lake layout |
| [`pages/enc.html`](pages/enc.html) | Columnar files, encoding, compression, encryption and keys |
| [`pages/ice.html`](pages/ice.html) | Apache Iceberg: metadata, commits, maintenance, catalogs |
| [`pages/design.html`](pages/design.html) | Lakehouse design: whiteboard, sizing, day-two operations, drills |
| [`pages/qa.html`](pages/qa.html) | 111 questions with mid-level and senior answers, search and drill mode |
| [`pages/lab.html`](pages/lab.html) | Optional hands-on lab: object store, Iceberg catalog, second engine |

Open any page directly in a browser, or serve `pages/` with any static file server. Each page is standalone: CSS and JavaScript are inline, and external requests are limited to Google Fonts and primary-source links.

## Build

```text
python -I build.py
```

Python 3.10 or later, standard library only. The script reads `src/frag_*.html` and `src/qa_*.json`, then writes `pages/*.html`. `urls.json` is optional; if present it maps page keys to published URLs so the set navigation links across a hosted copy.

## Source and genericisation

These notes were generalised from a private interview-preparation set. The technical substance is unchanged. The following were removed or replaced before publication:

- The employer's name, internal programme and product names, and company-specific framing.
- Interviewer, round and debrief details, and all personal career, resume and employer references.
- Internal bucket names, hostnames and local filesystem paths.
- Tailored "from your work" notes that connected the material to one person's resume.

The 40 TB figure is kept only as an explicitly illustrative design constraint. The source debrief page and the question-to-PDF index are not included: both describe a specific interview and personal preparation, so they are not generic study material.

## Licence

The text and pages are licensed under [Creative Commons Attribution 4.0 International](LICENSE) (CC BY 4.0). You may share and adapt the material for any purpose, including commercially, with attribution.

Third-party product names and linked source material remain the property of their respective owners. The licence does not cover quoted material from those sources.
