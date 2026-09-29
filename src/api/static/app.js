document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Global Setup & Colors ---
    Chart.defaults.color = '#8b9eb3';
    Chart.defaults.font.family = 'Inter';
    const blue = '#38bdf8';
    const green = '#10b981';
    const red = '#ef4444';
    const purple = '#8b5cf6';
    const yellow = '#f59e0b';
    const border = '#1e293b';

    // Store chart instances globally for updates
    window.dashboardCharts = {};

    // --- 2. Threats Over Time (Line Chart) ---
    const ctxTime = document.getElementById('threatsTimeChart');
    if (ctxTime) {
        window.dashboardCharts.time = new Chart(ctxTime, {
            type: 'line',
            data: {
                labels: ['01 May', '05 May', '10 May', '15 May', '20 May', '25 May', '30 May'],
                datasets: [
                    {
                        label: 'Reports',
                        data: [12, 45, 32, 67, 45, 89, 56],
                        borderColor: blue,
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'IOCs (x10)',
                        data: [23, 20, 50, 30, 60, 40, 70],
                        borderColor: green,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top', align: 'start', labels: { boxWidth: 10 } } },
                scales: {
                    x: { grid: { color: border } },
                    y: { grid: { color: border }, beginAtZero: true }
                }
            }
        });
    }

    // --- 3. Severity Distribution (Donut Chart) ---
    const ctxSeverity = document.getElementById('severityChart');
    if (ctxSeverity) {
        window.dashboardCharts.severity = new Chart(ctxSeverity, {
            type: 'doughnut',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    data: [254, 512, 320, 162],
                    backgroundColor: [red, yellow, purple, green],
                    borderWidth: 0,
                    cutout: '75%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
    }

    // --- 4. Initialize KPIs from backend ---
    fetch('/dashboard/stats')
        .then(r => r.json())
        .then(stats => {
            const kpiReports = document.getElementById('kpi-reports-val');
            if (kpiReports) kpiReports.innerText = stats.total_reports.toLocaleString();

            const kpiIocs = document.getElementById('kpi-iocs-val');
            if (kpiIocs) kpiIocs.innerText = stats.total_iocs.toLocaleString();

            const kpiActors = document.getElementById('kpi-actors-val');
            if (kpiActors) kpiActors.innerText = stats.threat_actors.toLocaleString();

            const kpiMalware = document.getElementById('kpi-malware-val');
            if (kpiMalware) kpiMalware.innerText = stats.malware_families.toLocaleString();

            const kpiAlerts = document.getElementById('kpi-alerts-val');
            if (kpiAlerts) kpiAlerts.innerText = stats.high_severity_alerts.toLocaleString();
        })
        .catch(err => console.error("Error initializing stats:", err));

    function updateDashboard(data) {
        if (!window.dashboardCharts) return;
        
        // 1. Update time chart (add a spike for today)
        if (window.dashboardCharts.time && data.normalizedEntities) {
            let reportsData = window.dashboardCharts.time.data.datasets[0].data;
            reportsData[reportsData.length - 1] += 1;
            
            let iocsData = window.dashboardCharts.time.data.datasets[1].data;
            iocsData[iocsData.length - 1] += data.normalizedEntities.length;
            
            window.dashboardCharts.time.update();
        }

        // 2. Update Severity Chart
        if (window.dashboardCharts.severity) {
            let severityScore = data.severity.score;
            let severityIdx = severityScore > 7 ? 0 : (severityScore > 4 ? 1 : 2); 
            window.dashboardCharts.severity.data.datasets[0].data[severityIdx] += 1;
            window.dashboardCharts.severity.update();
        }


        // 3. Update KPI Cards
        fetch('/dashboard/stats')
            .then(r => r.json())
            .then(stats => {
                const kpiReports = document.getElementById('kpi-reports-val');
                if (kpiReports) kpiReports.innerText = stats.total_reports.toLocaleString();

                const kpiIocs = document.getElementById('kpi-iocs-val');
                if (kpiIocs) kpiIocs.innerText = stats.total_iocs.toLocaleString();

                const kpiActors = document.getElementById('kpi-actors-val');
                if (kpiActors) kpiActors.innerText = stats.threat_actors.toLocaleString();

                const kpiMalware = document.getElementById('kpi-malware-val');
                if (kpiMalware) kpiMalware.innerText = stats.malware_families.toLocaleString();

                const kpiAlerts = document.getElementById('kpi-alerts-val');
                if (kpiAlerts) kpiAlerts.innerText = stats.high_severity_alerts.toLocaleString();
            })
            .catch(err => console.error("Error fetching stats:", err));

        // 4. Append to Latest Threats List
        const threatsList = document.getElementById('latest-threats-list');
        if (threatsList && data.normalizedEntities) {
            let primaryActor = 'Unknown';
            let actorEnt = data.normalizedEntities.find(e => e.label === 'threat_actor');
            if (actorEnt) primaryActor = actorEnt.text;
            
            let primaryMalware = '';
            let malEnt = data.normalizedEntities.find(e => e.label === 'malware');
            if (malEnt) primaryMalware = malEnt.text;

            let cve = '';
            let cveEnt = data.normalizedEntities.find(e => e.label === 'cve');
            if (cveEnt) cve = cveEnt.text;
            
            let description = 'New intelligence report analyzed';
            if (primaryActor !== 'Unknown' && cve) description = `${primaryActor} exploits ${cve}`;
            else if (primaryActor !== 'Unknown' && primaryMalware) description = `${primaryActor} deploys ${primaryMalware}`;
            else if (primaryMalware) description = `${primaryMalware} activity detected`;
            else if (primaryActor !== 'Unknown') description = `${primaryActor} activity detected`;

            let badgeClass = data.severity.level.toLowerCase() === 'critical' ? 'badge-critical' : (data.severity.level.toLowerCase() === 'high' ? 'badge-high' : 'badge-medium');
            
            let dateStr = new Date().toLocaleString('en-GB', {day:'numeric', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit'});

            const itemHtml = `
                <div class="list-item" style="animation: fade-in 0.5s ease-out;">
                    <span class="badge ${badgeClass}">${data.severity.level}</span>
                    <div class="item-details">
                        <p>${description}</p>
                        <span>${primaryActor} • ${dateStr}</span>
                    </div>
                </div>
            `;
            // Insert at the top
            threatsList.insertAdjacentHTML('afterbegin', itemHtml);
            // Keep only latest 4
            if (threatsList.children.length > 5) {
                threatsList.removeChild(threatsList.lastChild);
            }
        }

        // 5. Update Sidebar Modules History
        const tableReports = document.getElementById('table-reports');
        if (tableReports) {
            let badgeClass = data.severity.score > 7 ? 'badge-critical' : (data.severity.score > 4 ? 'badge-high' : 'badge-medium');
            let date = new Date().toLocaleString('en-GB', {day:'2-digit', month:'short', year:'numeric'});
            let id = "REP-" + Math.floor(Math.random() * 100000);
            let actor = data.normalizedEntities.find(e => e.label === 'threat_actor');
            let actorName = actor ? actor.text : 'Unknown Source';

            let newRow = document.createElement('tr');
            newRow.innerHTML = `<td>${id}</td><td>Analysis: ${actorName}</td><td>${date}</td><td><span class="badge ${badgeClass}">${data.severity.level}</span></td><td>Processed</td>`;
            tableReports.insertBefore(newRow, tableReports.children[1]);
        }

        const tableIocs = document.getElementById('table-iocs');
        if (tableIocs && data.normalizedEntities) {
            let iocs = data.normalizedEntities.filter(e => ['ip', 'domain', 'hash', 'url', 'email', 'registry_key'].includes(e.label));
            let actor = data.normalizedEntities.find(e => e.label === 'threat_actor');
            let actorName = actor ? actor.text : 'Unknown';

            iocs.forEach(ioc => {
                let newRow = document.createElement('tr');
                newRow.innerHTML = `<td>${ioc.text}</td><td>${ioc.label.toUpperCase()}</td><td>${actorName}</td><td>99%</td>`;
                tableIocs.insertBefore(newRow, tableIocs.children[1]);
            });
        }

        const gridActors = document.getElementById('grid-actors');
        if (gridActors && data.normalizedEntities) {
            let actors = data.normalizedEntities.filter(e => e.label === 'threat_actor');
            actors.forEach(actor => {
                let card = document.createElement('div');
                card.className = 'kpi-card purple';
                card.innerHTML = `
                    <div class="kpi-header"><div class="kpi-icon"><i class="fa-solid fa-user-secret"></i></div></div>
                    <h3>${actor.text}</h3><p style="color:#8b9eb3; margin-top:5px;">Origin: Unknown<br>Detected: Just now</p>
                `;
                gridActors.insertBefore(card, gridActors.firstChild);
            });
        }

        const tableMalware = document.getElementById('table-malware');
        if (tableMalware && data.normalizedEntities) {
            let malwares = data.normalizedEntities.filter(e => e.label === 'malware');
            malwares.forEach(mal => {
                let newRow = document.createElement('tr');
                newRow.innerHTML = `<td>${mal.text}</td><td>Malware</td><td>-</td><td>Yes</td>`;
                tableMalware.insertBefore(newRow, tableMalware.children[1]);
            });
        }

        const tableMitre = document.getElementById('table-mitre');
        if (tableMitre && data.normalizedTags) {
            data.normalizedTags.forEach(tag => {
                let newRow = document.createElement('tr');
                newRow.innerHTML = `<td>Observed Tactic</td><td>${tag.id} - ${tag.name}</td>`;
                tableMitre.insertBefore(newRow, tableMitre.children[1]);
            });
        }
    }

    // --- 9. Modal Logic for Analyzer ---
    const modal = document.getElementById('analyzer-modal');
    const openBtn = document.getElementById('open-analyzer-btn');
    const closeBtn = document.querySelector('.close-modal');
    const analyzeBtn = document.getElementById('analyze-btn');

    // List of all view IDs (derived from sidebar item texts)
    const allViews = [
        'view-dashboard', 'view-threat-reports', 'view-iocs', 
        'view-threat-actors', 'view-malware', 'view-vulnerabilities-cve', 
        'view-mitre-att-ck', 'view-knowledge-graph', 'view-alerts', 
        'view-reports', 'view-settings'
    ];
    let fullGraphInitialized = false;

    // Sidebar navigation interactivity
    const navItems = document.querySelectorAll('.sidebar-nav li');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
            
            const moduleName = this.innerText.trim();
            if (!moduleName) return;

            let viewId = 'view-' + moduleName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
            if (moduleName === 'Vulnerabilities (CVE)') viewId = 'view-vulnerabilities-cve';
            
            // Hide all views
            allViews.forEach(id => {
                const el = document.getElementById(id);
                if (el) el.style.display = 'none';
            });
            
            // Show the selected view
            const targetView = document.getElementById(viewId);
            if (targetView) {
                targetView.style.display = (viewId === 'view-dashboard') ? 'grid' : 'block';
                
                // Initialize or dynamically refresh full graph
                if (viewId === 'view-knowledge-graph') {
                    const colorMap = {
                        'ThreatActor': '#ef4444',
                        'Malware': '#f59e0b',
                        'IPAddress': '#06b6d4',
                        'Domain': '#8b5cf6',
                        'URL': '#3b82f6',
                        'CVE': '#ec4899',
                        'Technique': '#38bdf8',
                        'Tactic': '#10b981',
                        'Persistence': '#f97316',
                        'Hash': '#64748b'
                    };
                    fetch('/knowledge_graph/data')
                        .then(r => r.json())
                        .then(gData => {
                            const graphContainer = document.getElementById('fullGraph');
                            if (!window.fullGraphInstance && graphContainer) {
                                window.fullGraphInstance = ForceGraph3D()(graphContainer)
                                    .nodeLabel(n => `${n.name || n.id} [${n.group || 'Entity'}]`)
                                    .nodeColor(n => colorMap[n.group] || '#94a3b8')
                                    .linkColor(() => 'rgba(255,255,255,0.25)')
                                    .backgroundColor('#111a24');
                            }
                            if (window.fullGraphInstance) {
                                window.fullGraphInstance.graphData(gData);
                            }
                        })
                        .catch(err => console.error("Error loading full graph:", err));
                }
            } else {
                console.warn("View not found for:", viewId);
                document.getElementById('view-dashboard').style.display = 'grid';
            }
        });
    });

    // --- Threat Analyzer Tab Switching Logic (Side-by-Side / Analyzing Tab / Output Tab) ---
    const analyzerTabBtns = document.querySelectorAll('.analyzer-tab-btn');
    const analyzerBodyContainer = document.getElementById('analyzer-body-container');

    analyzerTabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            analyzerTabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const mode = btn.dataset.view; // 'split', 'input', or 'output'
            if (analyzerBodyContainer) {
                analyzerBodyContainer.className = `analyzer-split-body mode-${mode}`;
            }
        });
    });

    // Sample Report Presets for Split Analyzer
    const sampleApt29 = document.getElementById('sample-apt29-btn');
    if (sampleApt29) {
        sampleApt29.onclick = () => {
            document.getElementById('report-input').value = `CTI ADVISORY: APT29 (Nobelium / Midnight Blizzard) active campaign exploiting CVE-2023-23397 in Microsoft Outlook for privilege escalation. Observed malicious IP address 185.132.189.10 hosting phishing payloads and connecting to C2 infrastructure secure-login-portal-update.com. Malware payload identified as SilentHorn downloader. MITRE ATT&CK tactics observed: Initial Access (T1566 Phishing) and Command and Scripting Interpreter (T1059).`;
        };
    }

    const sampleEmotet = document.getElementById('sample-emotet-btn');
    if (sampleEmotet) {
        sampleEmotet.onclick = () => {
            document.getElementById('report-input').value = `ALERT: New Emotet malware campaign utilizing malicious PDF attachments and Word macros. Executable hash MD5: a3b92f74e6b12d59a840e6c1e13b8273 communicating with malicious loader server TrickBot at domain bad-example.com. Mapped MITRE ATT&CK techniques: User Execution (T1204) and Exfiltration Over C2 Channel (T1041).`;
        };
    }

    function renderAnalysisResults(data) {
        const emptyState = document.getElementById('analysis-empty-state');
        const resultsDiv = document.getElementById('analysis-results');
        const statusBadge = document.getElementById('result-status-badge');

        if (emptyState) emptyState.style.display = 'none';
        if (resultsDiv) resultsDiv.style.display = 'block';
        if (statusBadge) {
            statusBadge.className = 'pane-badge status-badge-active';
            statusBadge.innerHTML = '<i class="fa-solid fa-check-circle" style="color:#10b981;"></i> Complete';
        }

        // Normalize entities
        let entitiesArr = data.normalizedEntities || [];
        if (!entitiesArr.length && data.entities) {
            for (const [label, items] of Object.entries(data.entities)) {
                items.forEach(item => entitiesArr.push({text: item, label: label}));
            }
        }

        // Update Output Tab badge
        const countBadge = document.getElementById('output-badge-count');
        if (countBadge) {
            countBadge.innerText = entitiesArr.length;
            countBadge.style.display = 'inline-block';
        }

        // Normalize attack_tags
        let tagsArr = data.normalizedTags || [];
        if (!tagsArr.length && data.attack_tags && data.attack_tags.techniques) {
            for (const [id, name] of Object.entries(data.attack_tags.techniques)) {
                tagsArr.push({id: id, name: name});
            }
        }

        const score = (data.severity && data.severity.score != null) ? data.severity.score : 7;
        const level = (data.severity && data.severity.level) ? data.severity.level : 'HIGH';
        const sevColor = score >= 8 ? '#ef4444' : (score >= 5 ? '#f59e0b' : '#10b981');

        let entitiesHtml = entitiesArr.map(e => {
            let color = '#38bdf8';
            if (e.label === 'threat_actor') color = '#a855f7';
            if (e.label === 'malware') color = '#ef4444';
            if (e.label === 'cve') color = '#f59e0b';
            return `<span class="badge" style="background:#0b1120; border:1px solid ${color}44; color:${color}; margin:3px; padding:5px 9px; font-size:12px;"><i class="fa-solid fa-tag" style="font-size:10px; margin-right:4px;"></i>${e.text} <small style="opacity:0.7;">(${e.label})</small></span>`;
        }).join('');

        let tagsHtml = tagsArr.map(t => `<span class="badge" style="background:#0b1120; border:1px solid #f59e0b44; color:#f59e0b; margin:3px; padding:5px 9px; font-size:12px;"><i class="fa-solid fa-shield-halved" style="font-size:10px; margin-right:4px;"></i>${t.id} — ${t.name}</span>`).join('');

        let relationsHtml = (data.relations || []).map(r => {
            const sub = r.subject || r[0] || 'Entity';
            const rel = r.relation || r[1] || 'related_to';
            const obj = r.object || r[2] || 'Target';
            return `<div style="font-size:12px; color:#cbd5e1; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.04); display:flex; align-items:center; gap:6px;">
                <span style="color:#38bdf8; font-weight:600;">${sub}</span> 
                <span style="color:#64748b; font-style:italic; font-size:11px;">➞ [${rel}] ➞</span> 
                <span style="color:#a855f7; font-weight:600;">${obj}</span>
            </div>`;
        }).join('');

        resultsDiv.innerHTML = `
            <div class="result-card-row">
                <div class="result-stat-box" style="border-color:${sevColor}44;">
                    <div class="lbl">Threat Severity</div>
                    <div class="val" style="color:${sevColor};">${score}/10 <span style="font-size:11px; vertical-align:middle;">(${level})</span></div>
                </div>
                <div class="result-stat-box">
                    <div class="lbl">Extracted Entities</div>
                    <div class="val" style="color:#38bdf8;">${entitiesArr.length}</div>
                </div>
                <div class="result-stat-box">
                    <div class="lbl">Relations</div>
                    <div class="val" style="color:#a855f7;">${(data.relations || []).length}</div>
                </div>
            </div>

            <div class="section-block">
                <h4><i class="fa-solid fa-cube" style="color:#38bdf8;"></i> Extracted Entities (${entitiesArr.length})</h4>
                <div style="display:flex; flex-wrap:wrap; max-height:160px; overflow-y:auto;">
                    ${entitiesHtml || '<span style="color:#64748b; font-size:12px;">No entities extracted</span>'}
                </div>
            </div>

            <div class="section-block">
                <h4><i class="fa-solid fa-list-check" style="color:#f59e0b;"></i> MITRE ATT&amp;CK Mapping (${tagsArr.length})</h4>
                <div style="display:flex; flex-wrap:wrap; max-height:160px; overflow-y:auto;">
                    ${tagsHtml || '<span style="color:#64748b; font-size:12px;">No MITRE techniques mapped</span>'}
                </div>
            </div>

            ${(data.relations || []).length ? `
            <div class="section-block">
                <h4><i class="fa-solid fa-diagram-project" style="color:#a855f7;"></i> Knowledge Graph Triples</h4>
            </div>` : ''}

            <div class="section-block">
                <h4><i class="fa-solid fa-user-pen" style="color:#38bdf8;"></i> Analyst Notes &amp; Actions Taken</h4>
                <textarea class="cyber-input" placeholder="Enter additional actions taken or custom security recommendations..." style="width: 100%; height: 60px; margin-top: 10px; resize: vertical;"></textarea>
                <button class="btn-primary mt-10" style="padding: 5px 10px; font-size: 12px;" onclick="alert('Analyst notes saved successfully!')"><i class="fa-solid fa-save"></i> Save Notes</button>
            </div>
        `;
        
        // Render Recommendations in the separate tab pane
        const recWrapper = document.getElementById('recommendations-results-wrapper');
        if (recWrapper) {
            recWrapper.innerHTML = `
                <div class="section-block" style="margin-top: 15px;">
                    <div style="max-height: 450px; overflow-y: auto; padding-right: 5px;">
                        ${(data.recommendations && data.recommendations.length > 0) ? data.recommendations.map(rec => {
                            let color = '#38bdf8'; 
                            if (rec.type === 'CRITICAL' || rec.type.includes('CRITICAL') || rec.type.includes('MALWARE')) color = '#ef4444';
                            else if (rec.type === 'HIGH' || rec.type.includes('VULNERABILITY')) color = '#f97316';
                            else if (rec.type.includes('THREAT ACTOR') || rec.type.includes('ACTOR')) color = '#a855f7';
                            
                            return `
                            <div style="background: rgba(0,0,0,0.2); border-left: 3px solid ${color}; border-radius: 4px; padding: 15px; margin-bottom: 15px;">
                                <h5 style="color: ${color}; margin-top: 0; margin-bottom: 10px; font-size: 13px; text-transform: uppercase;">${rec.type}</h5>
                                <div style="margin-bottom: 12px;">
                                    <strong style="color: var(--text-light); font-size: 12px;"><i class="fa-solid fa-brain" style="margin-right: 4px;"></i> Understanding:</strong>
                                    <p style="color: var(--text-muted); font-size: 12px; margin: 4px 0 0 0;">${rec.understanding || ''}</p>
                                </div>
                                <div style="margin-bottom: 12px;">
                                    <strong style="color: var(--text-light); font-size: 12px;"><i class="fa-solid fa-wrench" style="margin-right: 4px;"></i> Action Required:</strong>
                                    <p style="color: #e2e8f0; font-size: 12px; margin: 4px 0 0 0; font-weight: 500;">${rec.explanation || ''}</p>
                                </div>
                                <div>
                                    <strong style="color: var(--text-light); font-size: 12px;"><i class="fa-solid fa-list-check" style="margin-right: 4px; color:${color};"></i> How to Implement:</strong>
                                    <p style="color: #cbd5e1; font-size: 12px; margin: 4px 0 0 0; white-space: pre-wrap;">${rec.how_to_do_it || 'No specific steps provided.'}</p>
                                </div>
                            </div>`;
                        }).join('') : '<div class="empty-state"><i class="fa-solid fa-shield-halved"></i><p>No recommendations available.</p></div>'}
                    </div>
                </div>
            `;
        }
    }

    if (openBtn) openBtn.onclick = () => modal.style.display = 'flex';
    if (closeBtn) {
        closeBtn.onclick = () => { modal.style.display = 'none'; };
    }
    const closeAnalyzerBtn = document.getElementById('close-analyzer-modal');
    if (closeAnalyzerBtn) {
        closeAnalyzerBtn.onclick = () => { modal.style.display = 'none'; };
    }
    
    if (analyzeBtn) {
        analyzeBtn.onclick = () => {
            const text = document.getElementById('report-input').value;
            if (!text) return alert("Please paste a report or select a sample preset.");
            
            analyzeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';
            fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ report_text: text, report_id: "ui_report" })
            })
            .then(res => {
                if(!res.ok) throw new Error("Server returned " + res.status);
                return res.json();
            })
            .then(data => {
                analyzeBtn.innerHTML = '<i class="fa-solid fa-play"></i> Execute Analysis';
                
                let entitiesArr = [];
                for (const [label, items] of Object.entries(data.entities || {})) {
                    items.forEach(item => entitiesArr.push({text: item, label: label}));
                }
                data.normalizedEntities = entitiesArr;

                let tagsArr = [];
                if (data.attack_tags && data.attack_tags.techniques) {
                    for (const [id, name] of Object.entries(data.attack_tags.techniques)) {
                        tagsArr.push({id: id, name: name});
                    }
                }
                data.normalizedTags = tagsArr;

                renderAnalysisResults(data);

                updateDashboard(data);
            })
            .catch(err => {
                alert("Error analyzing report: " + err.message);
                analyzeBtn.innerHTML = '<i class="fa-solid fa-play"></i> Execute Analysis';
            });
        };
    }

    const fileUpload = document.getElementById('file-upload');
    if (fileUpload) {
        fileUpload.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);
            
            if (analyzeBtn) analyzeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing File...';
            fetch('/analyze/file', {
                method: 'POST',
                body: formData
            })
            .then(res => {
                if(!res.ok) throw new Error("Server returned " + res.status);
                return res.json();
            })
            .then(data => {
                if (analyzeBtn) analyzeBtn.innerHTML = '<i class="fa-solid fa-play"></i> Execute Analysis';
                
                let entitiesArr = [];
                for (const [label, items] of Object.entries(data.entities || {})) {
                    items.forEach(item => entitiesArr.push({text: item, label: label}));
                }
                data.normalizedEntities = entitiesArr;

                let tagsArr = [];
                if (data.attack_tags && data.attack_tags.techniques) {
                    for (const [id, name] of Object.entries(data.attack_tags.techniques)) {
                        tagsArr.push({id: id, name: name});
                    }
                }
                data.normalizedTags = tagsArr;

                renderAnalysisResults(data);

                updateDashboard(data);
            })
            .catch(err => {
                alert("Error analyzing file: " + err.message);
                if (analyzeBtn) analyzeBtn.innerHTML = '<i class="fa-solid fa-play"></i> Execute Analysis';
            });
        };
    }

    const clearCacheBtn = document.getElementById('btn-clear-cache');
    if (clearCacheBtn) {
        clearCacheBtn.onclick = () => {
            if (confirm('Are you sure you want to clear the local knowledge graph cache? This will remove all analyzed data.')) {
                fetch('/knowledge_graph/clear', { method: 'POST' })
                    .then(res => res.json())
                    .then(data => {
                        alert(data.message);
                        window.location.reload();
                    })
                    .catch(err => {
                        alert("Error clearing cache: " + err.message);
                    });
            }
        };
    }

    // =========================================================================
    // SEARCH BAR — Live search across all dashboard data
    // =========================================================================
    const searchIndex = [
        { type: 'Threat Actor', label: 'badge-critical', text: 'APT29', desc: 'Russia-linked espionage group' },
        { type: 'Threat Actor', label: 'badge-critical', text: 'Lazarus Group', desc: 'North Korea-linked financial attacks' },
        { type: 'Threat Actor', label: 'badge-high',     text: 'Emotet', desc: 'Global malspam botnet' },
        { type: 'Malware',      label: 'badge-critical', text: 'SilentHorn', desc: 'Ransomware family' },
        { type: 'Malware',      label: 'badge-high',     text: 'TrickBot', desc: 'Banking trojan / loader' },
        { type: 'Malware',      label: 'badge-high',     text: 'Cobalt Strike', desc: 'Red team C2 tool' },
        { type: 'IOC',          label: 'badge-medium',   text: '185.132.189.10', desc: 'Malicious IP — APT29' },
        { type: 'IOC',          label: 'badge-medium',   text: 'secure-login-portal-update.com', desc: 'Phishing domain' },
        { type: 'IOC',          label: 'badge-high',     text: 'a3b92f74e6b12d59a840e6c1e13b8273', desc: 'MD5 hash — Emotet' },
        { type: 'CVE',          label: 'badge-critical', text: 'CVE-2023-23397', desc: 'Microsoft Outlook EoP (CVSS 9.8)' },
        { type: 'CVE',          label: 'badge-high',     text: 'CVE-2026-12345', desc: 'Zero-day firewall RCE' },
        { type: 'MITRE',        label: 'badge-medium',   text: 'T1566 - Phishing', desc: 'Initial Access tactic' },
        { type: 'MITRE',        label: 'badge-medium',   text: 'T1059 - Scripting', desc: 'Execution tactic' },
    ];

    const searchInput  = document.getElementById('global-search');
    const searchDropdown = document.getElementById('search-dropdown');

    if (searchInput && searchDropdown) {
        searchInput.addEventListener('input', () => {
            const q = searchInput.value.trim().toLowerCase();
            if (!q) { searchDropdown.style.display = 'none'; return; }

            const results = searchIndex.filter(item =>
                item.text.toLowerCase().includes(q) ||
                item.type.toLowerCase().includes(q) ||
                item.desc.toLowerCase().includes(q)
            );

            if (!results.length) {
                searchDropdown.innerHTML = `<div class="search-no-result">No results for "<strong>${q}</strong>"</div>`;
            } else {
                searchDropdown.innerHTML = results.map(r => `
                    <div class="search-result-item" data-type="${r.type}">
                        <span class="badge ${r.label}" style="font-size:10px;padding:2px 6px;">${r.type}</span>
                        <div class="search-result-text">
                            <strong>${r.text}</strong>
                            <span>${r.desc}</span>
                        </div>
                    </div>`).join('');

                // Click to navigate
                searchDropdown.querySelectorAll('.search-result-item').forEach(el => {
                    el.onclick = () => {
                        const viewMap = {
                            'Threat Actor': 'view-threat-actors',
                            'Malware':      'view-malware',
                            'IOC':          'view-iocs',
                            'CVE':          'view-vulnerabilities-cve',
                            'MITRE':        'view-mitre-att-ck'
                        };
                        const viewId = viewMap[el.dataset.type];
                        if (viewId) {
                            document.querySelectorAll('.module-view, .dashboard-grid').forEach(v => v.style.display = 'none');
                            document.getElementById(viewId).style.display = 'block';
                            document.querySelectorAll('.sidebar-nav li').forEach(li => li.classList.remove('active'));
                        }
                        searchDropdown.style.display = 'none';
                        searchInput.value = '';
                    };
                });
            }
            searchDropdown.style.display = 'block';
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
                searchDropdown.style.display = 'none';
            }
        });

        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') { searchDropdown.style.display = 'none'; searchInput.blur(); }
        });
    }

    // =========================================================================
    // DATE PICKER, NOTIFICATIONS & FILTERS
    // closeAllDropdowns is defined HERE first — before any calls to it
    // =========================================================================
    const datePickerBtn      = document.getElementById('date-picker-btn');
    const datePickerDropdown = document.getElementById('date-picker-dropdown');
    const dateRangeLabel     = document.getElementById('date-range-label');
    const notifBtnEl         = document.getElementById('notif-btn');
    const notifDropdownEl    = document.getElementById('notif-dropdown');
    const notifBadgeEl       = document.getElementById('notif-badge');

    function closeAllDropdowns(except) {
        [datePickerDropdown, notifDropdownEl].forEach(d => {
            if (d && d !== except) d.style.display = 'none';
        });
    }

    // --- Date Picker ---
    if (datePickerBtn && datePickerDropdown) {
        datePickerBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeAllDropdowns(datePickerDropdown);
            datePickerDropdown.style.display = datePickerDropdown.style.display === 'none' ? 'block' : 'none';
        });

        document.querySelectorAll('.date-preset').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const lbl = item.dataset.label;
                const now = new Date();
                let from = new Date();
                if (lbl === 'Last 7 Days')  from.setDate(now.getDate() - 7);
                if (lbl === 'Last 30 Days') from.setDate(now.getDate() - 30);
                if (lbl === 'Last 90 Days') from.setDate(now.getDate() - 90);
                if (lbl === 'This Year')    from = new Date(now.getFullYear(), 0, 1);
                const fmt = d => d.toLocaleDateString('en-GB', {day:'2-digit', month:'short', year:'numeric'});
                if (dateRangeLabel) dateRangeLabel.textContent = `${fmt(from)} - ${fmt(now)}`;
                document.querySelectorAll('.date-preset').forEach(p => p.classList.remove('active'));
                item.classList.add('active');
                datePickerDropdown.style.display = 'none';
            });
        });

        const applyDateBtn = document.getElementById('apply-date-btn');
        if (applyDateBtn) {
            applyDateBtn.onclick = (e) => {
                e.stopPropagation();
                const from = document.getElementById('date-from').value;
                const to   = document.getElementById('date-to').value;
                if (from && to) {
                    const fmt = d => new Date(d).toLocaleDateString('en-GB', {day:'2-digit', month:'short', year:'numeric'});
                    if (dateRangeLabel) dateRangeLabel.textContent = `${fmt(from)} - ${fmt(to)}`;
                    datePickerDropdown.style.display = 'none';
                } else {
                    alert('Please select both From and To dates.');
                }
            };
        }
    }

    // --- Notifications ---
    if (notifBtnEl && notifDropdownEl) {
        notifBtnEl.addEventListener('click', (e) => {
            e.stopPropagation();
            closeAllDropdowns(notifDropdownEl);
            notifDropdownEl.style.display = notifDropdownEl.style.display === 'none' ? 'block' : 'none';
        });

        const markAllRead = document.getElementById('mark-all-read');
        if (markAllRead) {
            markAllRead.onclick = (e) => {
                e.stopPropagation();
                document.querySelectorAll('.notif-item.unread').forEach(el => el.classList.remove('unread'));
                if (notifBadgeEl) notifBadgeEl.style.display = 'none';
            };
        }

        const viewAllAlerts = document.getElementById('view-all-alerts-btn');
        if (viewAllAlerts) {
            viewAllAlerts.onclick = () => {
                notifDropdownEl.style.display = 'none';
                const allViews2 = document.querySelectorAll('.module-view, #view-dashboard');
                allViews2.forEach(v => v.style.display = 'none');
                const alertView = document.getElementById('view-alerts');
                if (alertView) alertView.style.display = 'block';
                document.querySelectorAll('.sidebar-nav li').forEach(li => {
                    li.classList.toggle('active', li.innerText.trim() === 'Alerts');
                });
            };
        }
    }

    // --- Filters ---
    const filterBtn = document.getElementById('filter-btn');
    let filterActive = false;
    if (filterBtn) {
        filterBtn.onclick = () => {
            filterActive = !filterActive;
            filterBtn.classList.toggle('btn-active', filterActive);
            filterBtn.innerHTML = filterActive
                ? '<i class="fa-solid fa-filter"></i> Filters <span style="background:#38bdf8;color:#0f172a;border-radius:10px;padding:1px 6px;font-size:10px;margin-left:4px;">ON</span>'
                : '<i class="fa-solid fa-filter"></i> Filters';
        };
    }

    // Outside click: close all dropdowns
    document.addEventListener('click', (e) => {
        if (datePickerBtn && !datePickerBtn.contains(e.target) && datePickerDropdown) {
            datePickerDropdown.style.display = 'none';
        }
        if (notifBtnEl && !notifBtnEl.contains(e.target) && notifDropdownEl) {
            notifDropdownEl.style.display = 'none';
        }
    });

    // =========================================================================
    // AUTH MODAL & OTP PASSWORDLESS AUTH LOGIC
    // =========================================================================
    // =========================================================================
    // AUTHENTICATION, CREDENTIAL RETENTION, EXISTING USERS & LOGOUT
    // =========================================================================
    const userProfileBtn = document.getElementById('user-profile-btn');
    const authModal = document.getElementById('auth-modal');
    const closeAuthModal = document.getElementById('close-auth-modal');
    const authAlert = document.getElementById('auth-alert');
    const topbarLogoutBtn = document.getElementById('topbar-logout-btn');
    const modalLogoutBtn = document.getElementById('modal-logout-btn');
    const modalSwitchAccountBtn = document.getElementById('modal-switch-account-btn');
    const loginBannerLogoutBtn = document.getElementById('login-banner-logout-btn');
    const profileTabBtn = document.getElementById('profile-tab-btn');

    const STORAGE_KEY_ACTIVE_USER = 'cti_current_user';
    const STORAGE_KEY_REMEMBERED_EMAIL = 'cti_remembered_email';
    const STORAGE_KEY_SAVED_ACCOUNTS = 'cti_saved_accounts';

    let registeredUsersList = [];

    function showAlert(message, isSuccess = true) {
        if (!authAlert) return;
        authAlert.className = `auth-alert ${isSuccess ? 'success' : 'error'}`;
        authAlert.innerHTML = message;
        authAlert.style.display = 'block';
    }

    function hideAlert() {
        if (authAlert) authAlert.style.display = 'none';
    }

    // ─── LocalStorage Session & Credential Helpers ───────────────────────────
    function getActiveUser() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY_ACTIVE_USER);
            return raw ? JSON.parse(raw) : null;
        } catch (e) {
            return null;
        }
    }

    function setActiveUser(user) {
        if (!user) return;
        const session = {
            username: user.username,
            email: user.email,
            loginTime: user.loginTime || new Date().toISOString()
        };
        localStorage.setItem(STORAGE_KEY_ACTIVE_USER, JSON.stringify(session));
        saveAccountToHistory(session.email, session.username);

        const rememberMeCheck = document.getElementById('login-remember-me');
        if (!rememberMeCheck || rememberMeCheck.checked) {
            localStorage.setItem(STORAGE_KEY_REMEMBERED_EMAIL, session.email);
        }
        renderUserState(session);
    }

    function clearActiveUser() {
        localStorage.removeItem(STORAGE_KEY_ACTIVE_USER);
        renderUserState(null);
    }

    function saveAccountToHistory(email, username) {
        try {
            let history = JSON.parse(localStorage.getItem(STORAGE_KEY_SAVED_ACCOUNTS) || '[]');
            const idx = history.findIndex(item => item.email.toLowerCase() === email.toLowerCase());
            if (idx >= 0) {
                history[idx].username = username;
                history[idx].lastLogin = new Date().toISOString();
            } else {
                history.push({ email, username, lastLogin: new Date().toISOString() });
            }
            localStorage.setItem(STORAGE_KEY_SAVED_ACCOUNTS, JSON.stringify(history));
        } catch (e) {}
    }

    // ─── Render Active User in UI (Topbar & Modal) ───────────────────────────
    function renderUserState(user) {
        const userDisplayName = document.getElementById('user-display-name');
        const userDisplayRole = document.getElementById('user-display-role');
        const userStatusDot = document.getElementById('user-status-dot');
        const loginActiveBanner = document.getElementById('login-active-banner');
        const loginActiveBannerUser = document.getElementById('login-active-banner-user');
        const profileCardName = document.getElementById('profile-card-name');
        const profileCardEmail = document.getElementById('profile-card-email');
        const profileCardSessionTime = document.getElementById('profile-card-session-time');

        if (user) {
            if (userDisplayName) userDisplayName.innerText = user.username;
            if (userDisplayRole) userDisplayRole.innerText = user.email;
            if (userProfileBtn) {
                userProfileBtn.classList.add('logged-in');
                userProfileBtn.title = `Logged in as ${user.username} (${user.email}) - Click to view account / logout`;
            }
            if (userStatusDot) userStatusDot.style.display = 'block';
            if (topbarLogoutBtn) topbarLogoutBtn.style.display = 'inline-flex';
            if (profileTabBtn) profileTabBtn.style.display = 'inline-flex';

            if (profileCardName) profileCardName.innerText = user.username;
            if (profileCardEmail) profileCardEmail.innerText = user.email;
            if (profileCardSessionTime && user.loginTime) {
                const dateObj = new Date(user.loginTime);
                profileCardSessionTime.innerText = dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' (' + dateObj.toLocaleDateString() + ')';
            }
            if (loginActiveBanner) {
                loginActiveBanner.style.display = 'flex';
                if (loginActiveBannerUser) loginActiveBannerUser.innerText = `${user.username} (${user.email})`;
            }
        } else {
            if (userDisplayName) userDisplayName.innerText = 'Sign In';
            if (userDisplayRole) userDisplayRole.innerText = 'Account & SMTP';
            if (userProfileBtn) {
                userProfileBtn.classList.remove('logged-in');
                userProfileBtn.title = 'Click to Sign In / Register';
            }
            if (userStatusDot) userStatusDot.style.display = 'none';
            if (topbarLogoutBtn) topbarLogoutBtn.style.display = 'none';
            if (profileTabBtn) profileTabBtn.style.display = 'none';
            if (loginActiveBanner) loginActiveBanner.style.display = 'none';
        }
    }

    // ─── Modal Tab Switching ─────────────────────────────────────────────────
    const tabBtns = document.querySelectorAll('.auth-tab-btn');
    const tabContents = document.querySelectorAll('.auth-tab-content');

    function switchAuthTab(tabId) {
        hideAlert();
        tabBtns.forEach(b => {
            if (b.getAttribute('data-tab') === tabId) {
                b.classList.add('active');
            } else {
                b.classList.remove('active');
            }
        });
        tabContents.forEach(c => {
            c.style.display = (c.id === tabId) ? 'block' : 'none';
        });
    }

    tabBtns.forEach(btn => {
        btn.onclick = () => {
            resetSteps();
            switchAuthTab(btn.getAttribute('data-tab'));
        };
    });

    function resetSteps() {
        const ls1 = document.getElementById('login-step-1');
        const ls2 = document.getElementById('login-step-2');
        if (ls1) ls1.style.display = 'block';
        if (ls2) ls2.style.display = 'none';
        const rs1 = document.getElementById('reg-step-1');
        const rs2 = document.getElementById('reg-step-2');
        if (rs1) rs1.style.display = 'block';
        if (rs2) rs2.style.display = 'none';
    }

    // ─── Existing Users Fetch & Render ───────────────────────────────────────
    function fetchExistingUsers() {
        const listEl = document.getElementById('existing-users-list');
        const countEl = document.getElementById('existing-users-count');
        if (!listEl) return;

        fetch('/api/auth/users')
            .then(res => res.json())
            .then(data => {
                if (data.success && Array.isArray(data.users)) {
                    registeredUsersList = data.users;
                    if (countEl) countEl.innerText = `${data.users.length} user${data.users.length === 1 ? '' : 's'}`;

                    if (data.users.length === 0) {
                        listEl.innerHTML = `<div style="font-size:12px; color:#64748b; padding:4px 0;">No registered users found. Switch to Register to create an account.</div>`;
                        return;
                    }

                    let html = '';
                    data.users.forEach(u => {
                        const initial = (u.username || u.email).charAt(0).toUpperCase();
                        html += `
                            <div class="existing-user-chip" data-email="${u.email}" data-username="${u.username || ''}" title="Click to auto-fill ${u.email}">
                                <div class="user-meta">
                                    <div class="user-avatar-mini">${initial}</div>
                                    <div class="user-names">
                                        <span class="name-text">${u.username || 'Analyst'}</span>
                                        <span class="email-text">${u.email}</span>
                                    </div>
                                </div>
                                <span class="use-btn"><i class="fa-solid fa-arrow-right"></i> Fill</span>
                            </div>
                        `;
                    });
                    listEl.innerHTML = html;

                    // Bind click listeners on chips to fill credentials
                    listEl.querySelectorAll('.existing-user-chip').forEach(chip => {
                        chip.onclick = () => {
                            const email = chip.getAttribute('data-email');
                            const emailInput = document.getElementById('login-email');
                            if (emailInput) {
                                emailInput.value = email;
                                emailInput.focus();
                                checkEmailMatch(email);
                            }
                            listEl.querySelectorAll('.existing-user-chip').forEach(c => c.classList.remove('selected'));
                            chip.classList.add('selected');
                        };
                    });

                    // Trigger live check on current email field value
                    const emailInput = document.getElementById('login-email');
                    if (emailInput && emailInput.value.trim()) {
                        checkEmailMatch(emailInput.value.trim());
                    }
                }
            })
            .catch(err => {
                console.error("Failed to load existing users:", err);
                if (countEl) countEl.innerText = `0`;
            });
    }

    // ─── Real-Time Live Email Matching ───────────────────────────────────────
    function checkEmailMatch(email) {
        const feedbackEl = document.getElementById('login-email-feedback');
        if (!feedbackEl) return;
        const trimmed = email.trim().toLowerCase();
        if (!trimmed) {
            feedbackEl.style.display = 'none';
            return;
        }

        const match = registeredUsersList.find(u => u.email.toLowerCase() === trimmed);
        if (match) {
            feedbackEl.className = 'login-feedback match';
            feedbackEl.innerHTML = `<i class="fa-solid fa-circle-check"></i> Registered Account: <strong>${match.username}</strong> (${match.email})`;
            feedbackEl.style.display = 'flex';
        } else if (trimmed.includes('@') && trimmed.includes('.')) {
            feedbackEl.className = 'login-feedback unmatched';
            feedbackEl.innerHTML = `<i class="fa-solid fa-circle-info"></i> Account not found. <a href="#" id="link-quick-reg" style="color:#38bdf8; text-decoration:underline; margin-left:4px;">Click to register</a>`;
            feedbackEl.style.display = 'flex';

            const quickRegLink = document.getElementById('link-quick-reg');
            if (quickRegLink) {
                quickRegLink.onclick = (e) => {
                    e.preventDefault();
                    switchAuthTab('register-tab');
                    const regEmail = document.getElementById('reg-email');
                    if (regEmail) regEmail.value = trimmed;
                };
            }
        } else {
            feedbackEl.style.display = 'none';
        }
    }

    const loginEmailInput = document.getElementById('login-email');
    if (loginEmailInput) {
        loginEmailInput.addEventListener('input', (e) => {
            checkEmailMatch(e.target.value);
        });
    }

    // ─── Restore Credentials on Init ─────────────────────────────────────────
    function restoreLoginCredentials() {
        const savedEmail = localStorage.getItem(STORAGE_KEY_REMEMBERED_EMAIL);
        const loginEmail = document.getElementById('login-email');
        const savedHint = document.getElementById('login-saved-hint');

        if (savedEmail && loginEmail) {
            loginEmail.value = savedEmail;
            if (savedHint) savedHint.style.display = 'inline-flex';
            checkEmailMatch(savedEmail);
        }
    }

    const clearSavedCredsBtn = document.getElementById('clear-saved-creds-btn');
    if (clearSavedCredsBtn) {
        clearSavedCredsBtn.onclick = (e) => {
            e.preventDefault();
            localStorage.removeItem(STORAGE_KEY_REMEMBERED_EMAIL);
            const loginEmail = document.getElementById('login-email');
            if (loginEmail) loginEmail.value = '';
            const savedHint = document.getElementById('login-saved-hint');
            if (savedHint) savedHint.style.display = 'none';
            const feedbackEl = document.getElementById('login-email-feedback');
            if (feedbackEl) feedbackEl.style.display = 'none';
            showAlert('Cleared saved login email from device.', true);
        };
    }

    // ─── Open Profile / Login Modal ──────────────────────────────────────────
    if (userProfileBtn && authModal) {
        userProfileBtn.onclick = () => {
            const user = getActiveUser();
            if (user) {
                // If user is already logged in, show their profile view!
                hideAlert();
                resetSteps();
                fetchExistingUsers();
                restoreLoginCredentials();
                renderUserState(user);
                switchAuthTab('profile-tab');
                authModal.style.display = 'block';
            } else {
                // If unauthenticated, redirect directly to the login page
                window.location.href = '/login';
            }
        };
    }

    if (closeAuthModal && authModal) {
        closeAuthModal.onclick = () => {
            authModal.style.display = 'none';
        };
    }

    // ─── LOGOUT HANDLER (Common for topbar, modal & banner) ───────────────────
    function handleLogout() {
        const user = getActiveUser();
        fetch('/api/auth/logout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: user ? user.email : '' })
        }).catch(() => {});

        clearActiveUser();
        // Redirect directly to the login page as requested
        window.location.href = '/login?status=logged_out';
    }

    if (topbarLogoutBtn) topbarLogoutBtn.onclick = handleLogout;
    if (modalLogoutBtn) modalLogoutBtn.onclick = handleLogout;
    if (loginBannerLogoutBtn) loginBannerLogoutBtn.onclick = handleLogout;

    if (modalSwitchAccountBtn) {
        modalSwitchAccountBtn.onclick = () => {
            handleLogout();
        };
    }

    // ─── Initialize Active Session on Page Load ──────────────────────────────
    const initialUser = getActiveUser();
    renderUserState(initialUser);
    restoreLoginCredentials();
    fetchExistingUsers();

    // ─── LOGIN Step 1: Send OTP ───────────────────────────────────────────────
    const formLoginEmail = document.getElementById('form-login-email');
    if (formLoginEmail) {
        formLoginEmail.onsubmit = (e) => {
            e.preventDefault();
            hideAlert();
            const email = document.getElementById('login-email').value.trim();
            showAlert('⏳ Sending login code to your email…', true);

            fetch('/api/auth/send-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showAlert('📧 Code sent! Check your inbox.', true);
                    document.getElementById('login-otp-email-display').innerText = email;
                    document.getElementById('login-step-1').style.display = 'none';
                    document.getElementById('login-step-2').style.display = 'block';
                    document.getElementById('login-otp').value = '';
                    document.getElementById('login-otp').focus();
                } else {
                    showAlert(`❌ ${data.error}`, false);
                }
            })
            .catch(err => showAlert(`❌ Network error: ${err.message}`, false));
        };
    }

    // ─── LOGIN Step 2: Verify OTP ────────────────────────────────────────────
    const formLoginOtp = document.getElementById('form-login-otp');
    if (formLoginOtp) {
        formLoginOtp.onsubmit = (e) => {
            e.preventDefault();
            hideAlert();
            const email = document.getElementById('login-email').value.trim();
            const otp = document.getElementById('login-otp').value.trim();
            showAlert('⏳ Verifying code…', true);

            fetch('/api/auth/verify-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, otp })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Persist session & credentials in browser
                    const user = { username: data.user.username, email: data.user.email, loginTime: new Date().toISOString() };
                    setActiveUser(user);

                    showAlert(`✅ ${data.message} Welcome back, <strong>${data.user.username}</strong>!`, true);
                    setTimeout(() => {
                        authModal.style.display = 'none';
                    }, 1400);
                } else {
                    showAlert(`❌ ${data.error}`, false);
                }
            })
            .catch(err => showAlert(`❌ Network error: ${err.message}`, false));
        };
    }

    // ─── LOGIN: Resend & Back ────────────────────────────────────────────────
    const loginResendBtn = document.getElementById('login-resend-btn');
    if (loginResendBtn) {
        loginResendBtn.onclick = () => {
            hideAlert();
            const email = document.getElementById('login-email').value.trim();
            showAlert('⏳ Resending code…', true);
            fetch('/api/auth/send-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            })
            .then(res => res.json())
            .then(data => showAlert(data.success ? '📧 New code sent!' : `❌ ${data.error}`, data.success))
            .catch(err => showAlert(`❌ ${err.message}`, false));
        };
    }

    const loginBackBtn = document.getElementById('login-back-btn');
    if (loginBackBtn) {
        loginBackBtn.onclick = () => {
            hideAlert();
            document.getElementById('login-step-1').style.display = 'block';
            document.getElementById('login-step-2').style.display = 'none';
        };
    }

    // ─── REGISTER Step 1: Send Verification OTP ──────────────────────────────
    const formRegisterInit = document.getElementById('form-register-init');
    if (formRegisterInit) {
        formRegisterInit.onsubmit = (e) => {
            e.preventDefault();
            hideAlert();
            const username = document.getElementById('reg-username').value.trim();
            const email = document.getElementById('reg-email').value.trim();
            showAlert('⏳ Sending verification code to your email…', true);

            fetch('/api/auth/register/init', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showAlert('📧 Verification code sent! Check your inbox.', true);
                    document.getElementById('reg-otp-email-display').innerText = email;
                    document.getElementById('reg-step-1').style.display = 'none';
                    document.getElementById('reg-step-2').style.display = 'block';
                    document.getElementById('reg-otp').value = '';
                    document.getElementById('reg-otp').focus();
                } else {
                    showAlert(`❌ ${data.error}`, false);
                }
            })
            .catch(err => showAlert(`❌ Network error: ${err.message}`, false));
        };
    }

    // ─── REGISTER Step 2: Verify OTP & Create Account ────────────────────────
    const formRegisterVerify = document.getElementById('form-register-verify');
    if (formRegisterVerify) {
        formRegisterVerify.onsubmit = (e) => {
            e.preventDefault();
            hideAlert();
            const email = document.getElementById('reg-email').value.trim();
            const otp = document.getElementById('reg-otp').value.trim();
            showAlert('⏳ Verifying code & creating account…', true);

            fetch('/api/auth/register/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, otp })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Persist session & credentials in browser
                    const user = { username: data.user.username, email: data.user.email, loginTime: new Date().toISOString() };
                    setActiveUser(user);
                    fetchExistingUsers();

                    let msg = `✅ ${data.message}`;
                    if (data.email_status && data.email_status.success) {
                        msg += `<br>📧 <strong>Welcome Email Dispatched!</strong>`;
                    }
                    showAlert(msg, true);
                    setTimeout(() => {
                        authModal.style.display = 'none';
                    }, 1800);
                } else {
                    showAlert(`❌ ${data.error}`, false);
                }
            })
            .catch(err => showAlert(`❌ Network error: ${err.message}`, false));
        };
    }

    // ─── REGISTER: Resend & Back ─────────────────────────────────────────────
    const regResendBtn = document.getElementById('reg-resend-btn');
    if (regResendBtn) {
        regResendBtn.onclick = () => {
            hideAlert();
            const username = document.getElementById('reg-username').value.trim();
            const email = document.getElementById('reg-email').value.trim();
            showAlert('⏳ Resending verification code…', true);
            fetch('/api/auth/register/init', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email })
            })
            .then(res => res.json())
            .then(data => showAlert(data.success ? '📧 New code sent!' : `❌ ${data.error}`, data.success))
            .catch(err => showAlert(`❌ ${err.message}`, false));
        };
    }

    const regBackBtn = document.getElementById('reg-back-btn');
    if (regBackBtn) {
        regBackBtn.onclick = () => {
            hideAlert();
            document.getElementById('reg-step-1').style.display = 'block';
            document.getElementById('reg-step-2').style.display = 'none';
        };
    }
    // ─── NOTIFICATION NEWS FEED ──────────────────────────────────────────────
    const notifBtn = document.getElementById('notif-btn');
    const notifDropdown = document.getElementById('notif-dropdown');
    const newsContainer = document.getElementById('news-container');
    const notifBadge = document.getElementById('notif-badge');
    const refreshNews = document.getElementById('refresh-news');

    function fetchRecentNews() {
        if (!newsContainer) return;
        newsContainer.innerHTML = '<div style="padding:15px; text-align:center; color:#94a3b8;"><i class="fa-solid fa-spinner fa-spin"></i> Loading news...</div>';
        
        fetch('/api/news/recent')
            .then(res => res.json())
            .then(data => {
                if (data.success && data.news && data.news.length > 0) {
                    let html = '';
                    data.news.forEach((item, index) => {
                        let colorClass = index === 0 ? 'red' : (index === 1 ? 'yellow' : 'blue');
                        let icon = index === 0 ? 'fa-fire' : 'fa-newspaper';
                        html += `
                            <a href="${item.link}" target="_blank" style="text-decoration:none;">
                                <div class="notif-item unread" style="cursor:pointer; display:flex; padding:12px 15px; border-bottom:1px solid rgba(255,255,255,0.04);">
                                    <div class="notif-icon ${colorClass}" style="margin-right:12px;"><i class="fa-solid ${icon}"></i></div>
                                    <div class="notif-body">
                                        <p style="color:#f8fafc; font-size:13px; margin-bottom:4px; line-height:1.4;">${item.title}</p>
                                        <span style="color:#64748b; font-size:11px;">${item.date}</span>
                                    </div>
                                </div>
                            </a>
                        `;
                    });
                    newsContainer.innerHTML = html;
                    if (notifBadge) {
                        notifBadge.innerText = data.news.length;
                        notifBadge.style.display = 'inline-block';
                    }
                } else {
                    newsContainer.innerHTML = '<div style="padding:15px; text-align:center; color:#64748b;">No recent news found.</div>';
                }
            })
            .catch(err => {
                console.error("Error fetching news:", err);
                newsContainer.innerHTML = '<div style="padding:15px; text-align:center; color:#ef4444;">Failed to load news.</div>';
            });
    }


    if (refreshNews) {
        refreshNews.addEventListener('click', (e) => {
            e.stopPropagation();
            fetchRecentNews();
        });
    }
    
    // Initial fetch to set the badge count
    fetchRecentNews();

});
