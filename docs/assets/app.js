/* global Vue */
(function () {
  'use strict';

  const FORM_NAMES = { 0: '长篇 / 中篇', 1: '对话小说', 3: '短篇' };
  const SERIES_ORDER = ['X征', '冬征', '春征', '秋征', '少年', '对话', '独立'];
  const SERIES_CLASS = {
    'X征': 'x', '冬征': 'winter', '春征': 'spring', '秋征': 'autumn',
    '少年': 'junior', '对话': 'dialogue', '独立': 'solo'
  };

  async function fetchJson(path) {
    const res = await fetch(path, { cache: 'no-cache' });
    if (!res.ok) throw new Error(path + ' HTTP ' + res.status);
    return res.json();
  }

  function loadError(err) {
    return '数据加载失败：' + err.message +
      '。请通过 GitHub Pages 或本地 HTTP 服务访问（例如在仓库目录运行 python -m http.server），直接双击 HTML 文件会被浏览器禁止读取 JSON。';
  }

  function shortDate(value) {
    return value ? String(value).slice(0, 10) : '—';
  }

  function formLabel(id) {
    if (Object.prototype.hasOwnProperty.call(FORM_NAMES, id)) return FORM_NAMES[id];
    if (id === '' || id === null || id === undefined) return '—';
    return '未知(' + id + ')';
  }

  function seriesOptions(contests) {
    const set = new Set(contests.map(function (c) { return c.series; }).filter(Boolean));
    return SERIES_ORDER.filter(function (s) { return set.has(s); })
      .concat(Array.from(set).filter(function (s) { return !SERIES_ORDER.includes(s); }));
  }

  function seriesClass(name) {
    return 'series-' + (SERIES_CLASS[name] || 'other');
  }

  function contestUrl(id) {
    return 'contest.html?contest_track_id=' + encodeURIComponent(id);
  }

  function awardsUrl(id) {
    return 'awards.html?contest_track_id=' + encodeURIComponent(id);
  }

  function bookUrl(nid) {
    return 'https://book.sfacg.com/Novel/' + nid + '/';
  }

  const Pager = {
    props: {
      page: { type: Number, default: 1 },
      pageSize: { type: Number, default: 50 },
      total: { type: Number, default: 0 }
    },
    emits: ['update:page'],
    computed: {
      pageCount: function () { return Math.max(1, Math.ceil(this.total / this.pageSize)); },
      from: function () { return this.total ? (this.page - 1) * this.pageSize + 1 : 0; },
      to: function () { return Math.min(this.page * this.pageSize, this.total); },
      pageNumbers: function () {
        const width = 5;
        let start = Math.max(1, this.page - Math.floor(width / 2));
        let end = Math.min(this.pageCount, start + width - 1);
        start = Math.max(1, end - width + 1);
        const out = [];
        for (let p = start; p <= end; p += 1) out.push(p);
        return out;
      },
      showStartEllipsis: function () { return this.pageNumbers[0] > 1; },
      showEndEllipsis: function () {
        return this.pageNumbers[this.pageNumbers.length - 1] < this.pageCount;
      }
    },
    methods: {
      go: function (p) {
        if (p >= 1 && p <= this.pageCount) this.$emit('update:page', p);
      }
    },
    template: [
      '<div class="pager" v-if="total > pageSize">',
      '  <span class="pager-info">{{ from }}–{{ to }} / {{ total }}</span>',
      '  <button class="btn" type="button" :disabled="page <= 1" @click="go(page - 1)">上一页</button>',
      '  <span v-if="showStartEllipsis" class="pager-ellipsis">…</span>',
      '  <button v-for="p in pageNumbers" :key="p" type="button" class="btn page-num" :class="{ active: p === page }" @click="go(p)">{{ p }}</button>',
      '  <span v-if="showEndEllipsis" class="pager-ellipsis">…</span>',
      '  <button class="btn" type="button" :disabled="page >= pageCount" @click="go(page + 1)">下一页</button>',
      '</div>'
    ].join('')
  };

  function mount(options) {
    const app = Vue.createApp(options);
    app.component('pager', Pager);
    app.mount('#app');
  }

  const pageName = document.body.dataset.page;

  if (pageName === 'index') {
    mount({
      data: function () {
        return {
          site: null,
          contests: [],
          keyword: '',
          series: '',
          sortDir: 'asc',
          page: 1,
          pageSize: 20,
          loading: true,
          error: ''
        };
      },
      computed: {
        seriesList: function () { return seriesOptions(this.contests); },
        filtered: function () {
          const kw = this.keyword.toLowerCase();
          const dir = this.sortDir === 'desc' ? -1 : 1;
          return this.contests.filter(function (c) {
            if (this.series && c.series !== this.series) return false;
            if (!kw) return true;
            return [c.contest_track_id, c.contest_name, c.series, c.api_generation]
              .some(function (v) { return String(v).toLowerCase().includes(kw); });
          }, this).sort(function (a, b) {
            return (a.contest_track_id - b.contest_track_id) * dir;
          });
        },
        paged: function () {
          const start = (this.page - 1) * this.pageSize;
          return this.filtered.slice(start, start + this.pageSize);
        }
      },
      watch: {
        keyword: function () { this.page = 1; },
        series: function () { this.page = 1; }
      },
      async mounted() {
        try {
          const pair = await Promise.all([fetchJson('data/site.json'), fetchJson('data/contests.json')]);
          this.site = pair[0];
          this.contests = pair[1];
        } catch (err) {
          this.error = loadError(err);
        } finally {
          this.loading = false;
        }
      },
      methods: {
        shortDate, contestUrl, awardsUrl, seriesClass,
        toggleSort: function () {
          this.sortDir = this.sortDir === 'asc' ? 'desc' : 'asc';
          this.page = 1;
        }
      }
    });
  }

  if (pageName === 'contest') {
    mount({
      data: function () {
        return {
          site: null,
          contest: null,
          roster: [],
          awards: [],
          rosterKeyword: '',
          formFilter: '',
          rosterPage: 1,
          rosterPageSize: 50,
          awardKeyword: '',
          awardPage: 1,
          awardPageSize: 50,
          loading: true,
          error: ''
        };
      },
      computed: {
        myAwards: function () {
          if (!this.contest) return [];
          const id = this.contest.contest_track_id;
          return this.awards.filter(function (a) { return a.contest_track_id === id; });
        },
        formOptions: function () {
          const set = new Set(this.roster.map(function (r) { return String(r.form_id); }));
          return ['0', '1', '3'].filter(function (f) { return set.has(f); })
            .concat(Array.from(set).filter(function (f) { return !['0', '1', '3'].includes(f); }));
        },
        filteredRoster: function () {
          const kw = this.rosterKeyword.toLowerCase();
          return this.roster.filter(function (r) {
            if (this.formFilter && String(r.form_id) !== this.formFilter) return false;
            if (!kw) return true;
            return [r.nid, r.title, r.author, r.intro, r.form_id]
              .some(function (v) { return String(v == null ? '' : v).toLowerCase().includes(kw); });
          }, this);
        },
        pagedRoster: function () {
          const start = (this.rosterPage - 1) * this.rosterPageSize;
          return this.filteredRoster.slice(start, start + this.rosterPageSize);
        },
        filteredAwards: function () {
          const kw = this.awardKeyword.toLowerCase();
          return this.myAwards.filter(function (a) {
            if (!kw) return true;
            return [a.nid, a.title, a.award, a.source, a.note]
              .some(function (v) { return String(v == null ? '' : v).toLowerCase().includes(kw); });
          });
        },
        pagedAwards: function () {
          const start = (this.awardPage - 1) * this.awardPageSize;
          return this.filteredAwards.slice(start, start + this.awardPageSize);
        }
      },
      watch: {
        rosterKeyword: function () { this.rosterPage = 1; },
        formFilter: function () { this.rosterPage = 1; },
        awardKeyword: function () { this.awardPage = 1; }
      },
      async mounted() {
        try {
          const trio = await Promise.all([
            fetchJson('data/site.json'),
            fetchJson('data/contests.json'),
            fetchJson('data/awards.json')
          ]);
          this.site = trio[0];
          this.awards = trio[2];
          const id = Number(new URLSearchParams(location.search).get('contest_track_id'));
          if (!id) throw new Error('缺少 contest_track_id 参数');
          this.contest = trio[1].find(function (c) { return c.contest_track_id === id; }) || null;
          if (!this.contest) throw new Error('未找到赛道 ' + id);
          if (this.contest.collected) {
            this.roster = await fetchJson('data/roster/' + id + '.json');
          }
        } catch (err) {
          this.error = loadError(err);
        } finally {
          this.loading = false;
        }
      },
      methods: { shortDate, formLabel, bookUrl, seriesClass }
    });
  }

  if (pageName === 'awards') {
    mount({
      data: function () {
        return {
          site: null,
          contest: null,
          contestId: Number(new URLSearchParams(location.search).get('contest_track_id')),
          awards: [],
          keyword: '',
          page: 1,
          pageSize: 50,
          loading: true,
          error: ''
        };
      },
      computed: {
        verifiedCount: function () {
          return this.awards.filter(function (a) { return a.verified; }).length;
        },
        goldCount: function () {
          return this.awards.filter(function (a) { return a.award === '金奖'; }).length;
        },
        filtered: function () {
          const kw = this.keyword.toLowerCase();
          return this.awards.filter(function (a) {
            if (!kw) return true;
            return [a.nid, a.title, a.award, a.source, a.note]
              .some(function (v) { return String(v == null ? '' : v).toLowerCase().includes(kw); });
          });
        },
        paged: function () {
          const start = (this.page - 1) * this.pageSize;
          return this.filtered.slice(start, start + this.pageSize);
        }
      },
      watch: {
        keyword: function () { this.page = 1; }
      },
      async mounted() {
        try {
          const pair = await Promise.all([
            fetchJson('data/site.json'),
            fetchJson('data/contests.json')
          ]);
          this.site = pair[0];
          if (!this.contestId) throw new Error('缺少 contest_track_id 参数');
          this.contest = pair[1].find(function (c) { return c.contest_track_id === this.contestId; }, this) || null;
          if (!this.contest) throw new Error('未找到赛道 ' + this.contestId);
          this.awards = (await fetchJson('data/awards.json')).filter(function (a) {
            return a.contest_track_id === this.contestId;
          }, this);
        } catch (err) {
          this.error = loadError(err);
        } finally {
          this.loading = false;
        }
      },
      methods: { bookUrl, seriesClass }
    });
  }
})();
