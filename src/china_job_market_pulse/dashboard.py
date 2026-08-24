from __future__ import annotations

import html
import json


def to_dashboard_html(report: dict, title: str = "China Job Market Pulse") -> str:
    """Render a self-contained dashboard with no network or browser runtime dependency."""

    payload = json.dumps(report, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")
    template = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <style>
    :root { color-scheme: light; --ink: #172033; --muted: #697386; --line: #e6eaf0; --accent: #2463eb; --accent-soft: #eaf1ff; --panel: #ffffff; --bg: #f6f8fb; }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--ink); font: 15px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif; }
    .shell { max-width: 1240px; margin: 0 auto; padding: 28px 20px 56px; }
    header { display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; margin-bottom: 24px; }
    h1, h2, p { margin: 0; }
    h1 { font-size: clamp(25px, 4vw, 38px); letter-spacing: -0.03em; }
    h2 { font-size: 17px; margin-bottom: 14px; }
    .subtitle { color: var(--muted); margin-top: 6px; }
    .badge { background: var(--accent-soft); border: 1px solid #cfe0ff; border-radius: 999px; color: #174db8; padding: 8px 13px; white-space: nowrap; }
    .toolbar, .panel { background: var(--panel); border: 1px solid var(--line); border-radius: 16px; box-shadow: 0 8px 24px rgba(25, 39, 68, .05); }
    .toolbar { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; padding: 14px 16px; margin-bottom: 18px; }
    label { color: var(--muted); font-size: 13px; }
    select { min-width: 180px; margin-left: 8px; border: 1px solid var(--line); border-radius: 9px; padding: 8px 10px; color: var(--ink); background: #fff; }
    .quality { color: var(--muted); font-size: 13px; }
    .kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-bottom: 18px; }
    .kpi { padding: 17px; }
    .kpi-label { color: var(--muted); font-size: 13px; }
    .kpi-value { font-size: 25px; font-weight: 700; margin-top: 4px; }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
    .panel { padding: 18px; min-width: 0; }
    .wide { grid-column: 1 / -1; }
    .bars { display: grid; gap: 10px; }
    .bar-row { display: grid; grid-template-columns: minmax(100px, 1fr) minmax(80px, 3fr) auto; gap: 10px; align-items: center; }
    .bar-label { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .bar-track { height: 9px; background: #edf1f7; border-radius: 99px; overflow: hidden; }
    .bar-fill { height: 100%; background: linear-gradient(90deg, #2463eb, #56a5ff); border-radius: inherit; }
    .bar-value { color: var(--muted); font-variant-numeric: tabular-nums; }
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; min-width: 520px; }
    th, td { padding: 10px 8px; border-bottom: 1px solid var(--line); text-align: right; white-space: nowrap; }
    th:first-child, td:first-child { text-align: left; }
    th { color: var(--muted); font-size: 12px; font-weight: 600; }
    .empty { color: var(--muted); padding: 8px 0; }
    footer { color: var(--muted); font-size: 12px; margin-top: 20px; }
    @media (max-width: 850px) { .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); } .grid { grid-template-columns: 1fr; } .wide { grid-column: auto; } header { flex-direction: column; } }
    @media (max-width: 480px) { .kpis { grid-template-columns: 1fr; } .shell { padding-left: 14px; padding-right: 14px; } }
  </style>
</head>
<body>
  <main class="shell">
    <header>
      <div><h1>__TITLE__</h1><p class="subtitle">职位市场的薪资、技能、城市与趋势概览</p></div>
      <div class="badge" id="quality-badge">加载中</div>
    </header>
    <section class="toolbar">
      <label>城市筛选<select id="city-filter"><option value="__all__">全部城市</option></select></label>
      <div class="quality" id="source-line"></div>
    </section>
    <section class="kpis">
      <div class="panel kpi"><div class="kpi-label">职位数</div><div class="kpi-value" id="kpi-jobs">—</div></div>
      <div class="panel kpi"><div class="kpi-label">城市数</div><div class="kpi-value" id="kpi-cities">—</div></div>
      <div class="panel kpi"><div class="kpi-label">月薪中位区间</div><div class="kpi-value" id="kpi-salary">—</div></div>
      <div class="panel kpi"><div class="kpi-label">薪资缺失率</div><div class="kpi-value" id="kpi-missing">—</div></div>
    </section>
    <section class="grid">
      <article class="panel"><h2>技能需求</h2><div class="bars" id="skills"></div></article>
      <article class="panel"><h2>城市对比</h2><div class="table-wrap"><table><thead><tr><th>城市</th><th>职位数</th><th>占比</th><th>薪资中位上限</th></tr></thead><tbody id="cities"></tbody></table></div></article>
      <article class="panel"><h2>经验分布</h2><div class="bars" id="experience"></div></article>
      <article class="panel"><h2>学历分布</h2><div class="bars" id="education"></div></article>
      <article class="panel"><h2>岗位类别</h2><div class="bars" id="roles"></div></article>
      <article class="panel"><h2>按月趋势</h2><div class="bars" id="trends"></div></article>
      <article class="panel wide"><h2>数据质量</h2><div class="quality" id="quality-detail"></div></article>
    </section>
    <footer>本页面由 China Job Market Pulse 在本地生成，不依赖外部脚本或网络服务。数据来源和使用许可请以输入文件说明为准。</footer>
  </main>
  <script>
    window.__JOBPULSE_REPORT__ = __REPORT_JSON__;
    (() => {
      const report = window.__JOBPULSE_REPORT__;
      const analysis = report.analysis || report;
      const allCities = Object.keys(analysis.cities || {}).sort((a, b) => a.localeCompare(b, 'zh-CN'));
      const $ = (id) => document.getElementById(id);
      const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
      const number = (value) => value === null || value === undefined || value === '' ? '—' : Number(value).toLocaleString('zh-CN', {maximumFractionDigits: 4});
      const percent = (value) => value === null || value === undefined || value === '' ? '—' : `${(Number(value) * 100).toFixed(1)}%`;
      const setText = (id, value) => { $(id).textContent = value; };

      allCities.forEach((city) => { const option = document.createElement('option'); option.value = city; option.textContent = city; $('city-filter').appendChild(option); });
      setText('source-line', `数据文件：${report.metadata?.source_name || 'unknown'} · 分析版本：${report.analysis_version || 'unknown'}`);
      const quality = report.quality || {};
      setText('quality-badge', `质量 ${quality.error_count || 0} 错误 · ${quality.warning_count || 0} 警告`);
      setText('quality-detail', `输入 ${number(quality.total_rows)} 行，接收 ${number(quality.accepted_rows)} 行，拒绝 ${number(quality.rejected_rows)} 行，去重 ${number(quality.duplicate_rows)} 行。`);

      function renderBars(id, items, valueKey = 'job_count') {
        const target = $(id);
        if (!items || !items.length) { target.innerHTML = '<div class="empty">暂无数据</div>'; return; }
        const max = Math.max(...items.map((item) => Number(item[valueKey]) || 0), 1);
        target.innerHTML = items.slice(0, 12).map((item) => `<div class="bar-row"><div class="bar-label" title="${esc(item.name || item.period)}">${esc(item.name || item.period)}</div><div class="bar-track"><div class="bar-fill" style="width:${Math.max(3, (Number(item[valueKey]) || 0) / max * 100)}%"></div></div><div class="bar-value">${number(item[valueKey])} · ${percent(item.job_share)}</div></div>`).join('');
      }

      function renderCities(selected) {
        const entries = allCities.filter((city) => !selected || city === selected).map((city) => [city, analysis.cities[city]]);
        $('cities').innerHTML = entries.map(([city, item]) => `<tr><td>${esc(city)}</td><td>${number(item.job_count)}</td><td>${percent(item.job_share)}</td><td>${number(item.salary_max_median)}</td></tr>`).join('') || '<tr><td colspan="4" class="empty">暂无数据</td></tr>';
      }

      function render() {
        const selected = $('city-filter').value === '__all__' ? '' : $('city-filter').value;
        const scope = selected ? analysis.cities[selected] : analysis.overall;
        setText('kpi-jobs', number(scope.job_count ?? scope.total_jobs));
        setText('kpi-cities', number(selected ? 1 : analysis.overall.city_count));
        setText('kpi-salary', `${number(scope.salary_min_median)}–${number(scope.salary_max_median)}`);
        setText('kpi-missing', percent(scope.salary_missing_rate));
        renderCities(selected);
        renderBars('skills', analysis.skills);
        renderBars('experience', analysis.experience);
        renderBars('education', analysis.education);
        renderBars('roles', analysis.roles);
        renderBars('trends', analysis.trends, 'job_count');
      }
      $('city-filter').addEventListener('change', render);
      render();
    })();
  </script>
</body>
</html>
"""
    return template.replace("__TITLE__", html.escape(title)).replace("__REPORT_JSON__", payload)
