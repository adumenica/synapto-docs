"""
Synapto Architecture Diagram Generator
Produces: platform_architecture_v2.png
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

# ── Canvas ───────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(22, 16))
ax.set_xlim(0, 22)
ax.set_ylim(0, 16)
ax.axis('off')
fig.patch.set_facecolor('#F8F9FA')
ax.set_facecolor('#F8F9FA')

# ── Colour palette ────────────────────────────────────────────────────────────
C = {
    'external':   '#E8944A',   # orange  – external / monitoring tools
    'gateway':    '#2C6FAC',   # dark blue – API Gateway (entry point)
    'service':    '#4A90D9',   # mid blue – platform services
    'data':       '#3D7A4E',   # dark green – PostgreSQL / Redis
    'agent_svc':  '#6B5EA6',   # purple – Agent Service
    'agent':      '#9B7ECC',   # light purple – Remote Agent
    'learning':   '#3A9FA3',   # teal – Learning Engine
    'itsm':       '#B07C3A',   # amber – ITSM Connector
    'infra':      '#5A7A8A',   # steel blue – managed infrastructure
    'auth':       '#2C6FAC',   # same as gateway (auth family)
    'frontend':   '#2C6FAC',   # same
    'bg_core':    '#E8EEF5',   # light blue bg – core pipeline section
    'bg_agent':   '#EDE8F5',   # light purple bg – agent section
    'bg_infra':   '#E8F0EE',   # light green bg – infra section
    'bg_data':    '#EBF3EB',   # lightest green bg – data layer
    'border':     '#CCCCCC',
    'arrow':      '#555555',
    'text_light': '#FFFFFF',
    'text_dark':  '#1A1A2E',
    'section_lbl':'#6B7280',
}

# ── Helper functions ──────────────────────────────────────────────────────────
def box(ax, x, y, w, h, label, sublabel=None, color='#4A90D9',
        text_color='white', fontsize=9, radius=0.18, alpha=1.0,
        border_color=None):
    """Draw a rounded-rectangle box with label."""
    bc = border_color if border_color else color
    rect = FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle=f"round,pad=0.05,rounding_size={radius}",
        facecolor=color, edgecolor=bc, linewidth=1.5, alpha=alpha, zorder=3
    )
    ax.add_patch(rect)
    if sublabel:
        ax.text(x, y + h*0.13, label, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color=text_color,
                zorder=4, linespacing=1.2)
        ax.text(x, y - h*0.22, sublabel, ha='center', va='center',
                fontsize=fontsize - 1.5, color=text_color, zorder=4,
                style='italic', alpha=0.9)
    else:
        ax.text(x, y, label, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color=text_color,
                zorder=4, linespacing=1.3, multialignment='center')

def section_bg(ax, x, y, w, h, color, label=None, label_color=None):
    """Draw a background section rectangle."""
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.05,rounding_size=0.25",
        facecolor=color, edgecolor=C['border'], linewidth=1.0,
        alpha=0.55, zorder=1
    )
    ax.add_patch(rect)
    if label:
        lc = label_color if label_color else C['section_lbl']
        ax.text(x + 0.18, y + h - 0.18, label, ha='left', va='top',
                fontsize=7.5, color=lc, fontweight='bold', zorder=2,
                style='italic')

def arrow(ax, x1, y1, x2, y2, label=None, color='#555555',
          lw=1.4, style='->', bidirectional=False, label_offset=(0,0),
          zorder=5, dashed=False):
    """Draw an annotated arrow."""
    ls = '--' if dashed else '-'
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=lw, linestyle=ls,
                                connectionstyle='arc3,rad=0.0'),
                zorder=zorder)
    if bidirectional:
        ax.annotate('', xy=(x1, y1), xytext=(x2, y2),
                    arrowprops=dict(arrowstyle=style, color=color,
                                    lw=lw, linestyle=ls,
                                    connectionstyle='arc3,rad=0.0'),
                    zorder=zorder)
    if label:
        mx = (x1 + x2) / 2 + label_offset[0]
        my = (y1 + y2) / 2 + label_offset[1]
        ax.text(mx, my, label, ha='center', va='center', fontsize=7,
                color=color, zorder=zorder+1,
                bbox=dict(boxstyle='round,pad=0.15', facecolor='#F8F9FA',
                          edgecolor='none', alpha=0.85))

def icon_box(ax, x, y, w, h, emoji, label, color='#4A90D9',
             fontsize=8.5):
    """Box with an emoji icon above the label."""
    rect = FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.05,rounding_size=0.18",
        facecolor=color, edgecolor=color, linewidth=1.5, zorder=3
    )
    ax.add_patch(rect)
    ax.text(x, y + h*0.12, emoji, ha='center', va='center',
            fontsize=14, zorder=4)
    ax.text(x, y - h*0.22, label, ha='center', va='center',
            fontsize=fontsize - 0.5, fontweight='bold',
            color='white', zorder=4)

# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT (all coordinates in data units, origin bottom-left)
# Rows (y centres):
#   Row 1 – External monitoring tools           y ≈ 14.8
#   Row 2 – User interface / API entry          y ≈ 13.0
#   Row 3 – Core pipeline                       y ≈ 10.8
#   Row 4 – Execution & Learning                y ≈  8.5
#   Row 5 – Agent Service                       y ≈  6.5
#   Row 6 – Infrastructure targets              y ≈  4.3
#   Row 7 – Data stores                         y ≈  2.0
# ─────────────────────────────────────────────────────────────────────────────

# ── Title ────────────────────────────────────────────────────────────────────
ax.text(11, 15.65, 'Synapto — Platform Architecture',
        ha='center', va='center', fontsize=17, fontweight='bold',
        color=C['text_dark'], zorder=10)
ax.text(11, 15.28, 'End-to-end data flow including distributed execution agents',
        ha='center', va='center', fontsize=9.5, color=C['section_lbl'], zorder=10)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 1  –  EXTERNAL MONITORING SOURCES
# ══════════════════════════════════════════════════════════════════════════════
section_bg(ax, 0.5, 14.05, 12.5, 0.95, '#FDF0E6',
           label='Monitoring & Alert Sources')

box(ax, 2.1,  14.5, 2.2, 0.65, 'Prometheus', color=C['external'], fontsize=8.5)
box(ax, 4.5,  14.5, 2.2, 0.65, 'CloudWatch\n/ Azure', color=C['external'], fontsize=8.5)
box(ax, 6.9,  14.5, 2.2, 0.65, 'Zabbix\n/ Nagios', color=C['external'], fontsize=8.5)
box(ax, 9.3,  14.5, 2.2, 0.65, 'Custom\nWebhooks', color=C['external'], fontsize=8.5)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 2  –  USER INTERFACE + PLATFORM ENTRY
# ══════════════════════════════════════════════════════════════════════════════
section_bg(ax, 0.5, 12.15, 21.0, 1.35, C['bg_core'],
           label='User Interface & Platform Entry')

# Frontend
box(ax, 2.3, 12.85, 2.8, 0.9, 'Frontend\n(React / Nginx :3000)',
    color=C['frontend'], fontsize=8.5, text_color='white')

# API Gateway – larger, prominent
box(ax, 6.2, 12.85, 3.0, 0.9, 'API Gateway  :8000\nAuth  |  Rate-Limit  |  Routing',
    color=C['gateway'], fontsize=8.5, text_color='white')

# Auth Service
box(ax, 11.0, 12.85, 2.6, 0.9, 'Auth Service  :8006\nJWT  |  OAuth2  |  RBAC',
    color=C['auth'], fontsize=8.5, text_color='white')

# Admin Service
box(ax, 14.0, 12.85, 2.6, 0.9, 'Admin Service  :8007\nUsers  |  Credentials  |  AI',
    color=C['service'], fontsize=8.5, text_color='white')

# ══════════════════════════════════════════════════════════════════════════════
# ROW 3  –  CORE EVENT PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
section_bg(ax, 0.5, 9.5, 21.0, 2.4, C['bg_core'],
           label='Core Event Pipeline')

# Integration Layer
box(ax, 2.5, 10.7, 2.8, 1.0, 'Integration Layer\n:8001',
    sublabel='Normalise · Deduplicate',
    color=C['service'], fontsize=9)

# Redis Stream badge
box(ax, 5.8, 10.7, 1.8, 0.7, 'Redis\nStream', color='#B5451B', fontsize=8)

# Orchestration Layer  – central, bigger
box(ax, 9.5, 10.7, 3.4, 1.1,
    'Orchestration Layer\n:8002',
    sublabel='Correlate · Policy Match · Workflow',
    color=C['gateway'], fontsize=9)

# Knowledge Layer
box(ax, 3.5, 9.85, 3.2, 0.9, 'Knowledge Layer  :8003',
    sublabel='Policies · Playbooks · SOPs · Topology',
    color=C['service'], fontsize=8.5)

# ITSM Connector
box(ax, 17.5, 10.7, 2.8, 1.0, 'ITSM Connector\n:8008',
    sublabel='ServiceNow · Jira · BMC',
    color=C['itsm'], fontsize=8.5)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 4  –  EXECUTION & LEARNING
# ══════════════════════════════════════════════════════════════════════════════
section_bg(ax, 0.5, 7.2, 21.0, 2.05, C['bg_core'],
           label='Execution & Intelligence')

# Execution Engine
box(ax, 7.5, 8.2, 3.0, 1.0,
    'Execution Engine\n:8004',
    sublabel='SSH · WinRM · Netmiko · SQL · Docker',
    color=C['service'], fontsize=8.5)

# Learning Engine
box(ax, 13.5, 8.2, 3.2, 1.0,
    'Learning Engine\n:8005',
    sublabel='Claude · OpenAI · Analytics · SOP Gen',
    color=C['learning'], fontsize=8.5)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 5  –  AGENT SERVICE   (NEW)
# ══════════════════════════════════════════════════════════════════════════════
section_bg(ax, 0.5, 5.4, 10.5, 1.6, C['bg_agent'],
           label='Distributed Agent Layer  (NEW)')

box(ax, 5.8, 6.2, 4.0, 1.0,
    'Agent Service  :50051',
    sublabel='gRPC  |  mTLS  |  Ed25519 Signing  |  SPIFFE',
    color=C['agent_svc'], fontsize=9)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 6  –  INFRASTRUCTURE TARGETS
# ══════════════════════════════════════════════════════════════════════════════
section_bg(ax, 0.5, 2.85, 21.0, 2.35, C['bg_infra'],
           label='Managed Infrastructure')

# Direct execution targets (left side)
box(ax, 3.0, 3.95, 2.0, 0.85, 'Linux\nServer', color=C['infra'], fontsize=8.5)
box(ax, 5.5, 3.95, 2.0, 0.85, 'Database\nServer', color=C['infra'], fontsize=8.5)
box(ax, 8.0, 3.95, 2.0, 0.85, 'Network\nDevice', color=C['infra'], fontsize=8.5)

# Remote agent + targets (right side)
box(ax, 13.5, 3.95, 3.4, 0.9,
    'Remote Synapto Agent',
    sublabel='synapto-agent  (managed node)',
    color=C['agent'], fontsize=8.5)

box(ax, 17.5, 3.95, 2.0, 0.85, 'Linux\nServer', color=C['infra'], fontsize=8.5)
box(ax, 19.8, 3.95, 1.8, 0.85, 'Windows\nServer', color=C['infra'], fontsize=8.5)

# Divider label between direct and agent paths
ax.text(10.8, 3.95, '─── or ───', ha='center', va='center',
        fontsize=8, color='#888888', style='italic', zorder=4)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 7  –  DATA STORES
# ══════════════════════════════════════════════════════════════════════════════
section_bg(ax, 0.5, 0.55, 21.0, 2.1, C['bg_data'],
           label='Data Persistence')

box(ax, 5.5, 1.55, 3.4, 1.0,
    'PostgreSQL  :5432',
    sublabel='Events  |  Incidents  |  Executions  |  Credentials',
    color=C['data'], fontsize=8.5)

box(ax, 11.5, 1.55, 3.0, 1.0,
    'Redis  :6379',
    sublabel='"events" Stream  |  Cache  |  Job Queue',
    color='#B5451B', fontsize=8.5)

# ══════════════════════════════════════════════════════════════════════════════
# ARROWS
# ══════════════════════════════════════════════════════════════════════════════

# --- Monitoring → Integration Layer
for mx in [2.1, 4.5, 6.9, 9.3]:
    arrow(ax, mx, 14.18, 2.5, 11.2, color='#888888', lw=1.0, zorder=4)

# Integration → Redis Stream
arrow(ax, 3.9, 10.7, 4.9, 10.7, label='publish', color='#B5451B', lw=1.5, label_offset=(0, 0.18))

# Redis Stream → Orchestration
arrow(ax, 6.7, 10.7, 7.8, 10.7, label='consume', color='#B5451B', lw=1.5, label_offset=(0, 0.18))

# Orchestration ↔ ITSM
arrow(ax, 11.2, 10.7, 16.1, 10.7, label='sync ticket', color=C['itsm'],
      lw=1.3, bidirectional=True, label_offset=(0, 0.2))

# Orchestration ↔ Knowledge Layer
arrow(ax, 8.1, 10.35, 5.1, 10.2, label='match\nplaybook', color=C['service'],
      lw=1.3, bidirectional=True, label_offset=(-0.6, 0.05))

# Orchestration → Execution Engine
arrow(ax, 9.5, 10.15, 8.0, 8.7, label='execute\nscript', color=C['service'],
      lw=1.5, label_offset=(-0.85, 0.0))

# Orchestration ↔ Learning Engine
arrow(ax, 10.5, 10.15, 13.0, 8.7, label='AI analyse\n/ generate', color=C['learning'],
      lw=1.5, bidirectional=True, label_offset=(0.9, 0.0))

# Learning ↔ Execution (results feedback)
arrow(ax, 9.0, 8.2, 11.9, 8.2, label='results', color=C['learning'],
      lw=1.3, label_offset=(0, 0.2))

# Execution Engine → Direct infra (SSH/WinRM/SQL)
arrow(ax, 6.5, 7.7, 3.0, 4.38, label='SSH\n:22', color=C['infra'], lw=1.3, label_offset=(-0.55, 0.0))
arrow(ax, 7.5, 7.7, 5.5, 4.38, label='SQL', color=C['infra'], lw=1.3, label_offset=(-0.4, 0.1))
arrow(ax, 8.5, 7.7, 8.0, 4.38, label='Netmiko\nSSH', color=C['infra'], lw=1.3, label_offset=(0.65, 0.1))

# Execution Engine → Agent Service
arrow(ax, 7.5, 7.7, 5.8, 6.7, label='dispatch\njob', color=C['agent_svc'],
      lw=1.8, label_offset=(-0.8, 0.0))

# Agent Service → Remote Agent
arrow(ax, 7.3, 5.7, 11.8, 4.38, label='gRPC stream\nmTLS · Ed25519', color=C['agent_svc'],
      lw=2.0, label_offset=(1.2, 0.15))

# Remote Agent → targets
arrow(ax, 15.2, 3.5, 17.2, 4.38, color=C['infra'], lw=1.2)
arrow(ax, 15.2, 3.5, 19.65, 4.38, color=C['infra'], lw=1.2)

# Frontend → API Gateway
arrow(ax, 3.7, 12.85, 4.7, 12.85, label='HTTPS', color=C['gateway'],
      lw=1.5, label_offset=(0, 0.22))

# API Gateway → various services (downward to orchestration)
arrow(ax, 6.2, 12.4, 5.5, 11.25, color=C['gateway'], lw=1.2, label='route')

# Auth Service → API Gateway (validates tokens)
arrow(ax, 9.7, 12.85, 7.7, 12.85, label='validate JWT', color=C['auth'],
      lw=1.3, label_offset=(0, 0.22))

# Data store connections (dashed — representative reads/writes)
# Orchestration → PostgreSQL
arrow(ax, 9.5, 10.15, 6.2, 2.05, color=C['data'], lw=0.8, dashed=True, zorder=2)
# Execution → PostgreSQL
arrow(ax, 7.5, 7.7, 6.0, 2.05, color=C['data'], lw=0.8, dashed=True, zorder=2)
# Auth/Admin → PostgreSQL
arrow(ax, 11.0, 12.4, 6.5, 2.05, color=C['data'], lw=0.8, dashed=True, zorder=2)
# Redis Stream (Integration → Redis → Orchestration shown separately above)
# Agent Service → PostgreSQL
arrow(ax, 5.8, 5.7, 5.8, 2.05, color=C['data'], lw=0.8, dashed=True, zorder=2)
# Orchestration → Redis (for DLQ / locking)
arrow(ax, 10.5, 10.15, 11.5, 2.05, color='#B5451B', lw=0.8, dashed=True, zorder=2)

# ══════════════════════════════════════════════════════════════════════════════
# LEGEND
# ══════════════════════════════════════════════════════════════════════════════
legend_x, legend_y = 15.8, 7.5
legend_w, legend_h = 5.8, 4.5
section_bg(ax, legend_x, legend_y - legend_h, legend_w, legend_h,
           '#FFFFFF', label='Legend', label_color='#333333')

legend_items = [
    (C['external'],   'External Monitoring Source'),
    (C['gateway'],    'API Gateway / Auth / Frontend'),
    (C['service'],    'Platform Service'),
    (C['itsm'],       'ITSM Connector'),
    (C['learning'],   'Learning Engine (AI)'),
    (C['agent_svc'],  'Agent Service  (gRPC/mTLS)  NEW'),
    (C['agent'],      'Remote Synapto Agent  NEW'),
    (C['infra'],      'Managed Infrastructure'),
    (C['data'],       'PostgreSQL Database'),
    ('#B5451B',       'Redis (Stream / Cache)'),
]

for i, (color, label) in enumerate(legend_items):
    ly = legend_y - 0.38 - i * 0.4
    rect = FancyBboxPatch((legend_x + 0.2, ly - 0.12), 0.55, 0.26,
                          boxstyle="round,pad=0.02", facecolor=color,
                          edgecolor='none', zorder=6)
    ax.add_patch(rect)
    ax.text(legend_x + 0.9, ly + 0.01, label, va='center', fontsize=7.8,
            color=C['text_dark'], zorder=7)

# Arrow legend entries
arrow_items = [
    (C['arrow'],      'solid',  'Synchronous HTTP call'),
    (C['agent_svc'],  'solid',  'gRPC bidirectional stream'),
    (C['data'],       'dashed', 'Read/Write to data store'),
    ('#B5451B',       'solid',  'Redis Stream publish/consume'),
]
for i, (color, style, label) in enumerate(arrow_items):
    ly = legend_y - 0.38 - (len(legend_items) + i) * 0.4
    lx = legend_x + 0.2
    ls = '--' if style == 'dashed' else '-'
    ax.annotate('', xy=(lx + 0.75, ly), xytext=(lx, ly),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5,
                                linestyle=ls), zorder=6)
    ax.text(legend_x + 0.9, ly, label, va='center', fontsize=7.8,
            color=C['text_dark'], zorder=7)

# ── Watermark / version ───────────────────────────────────────────────────────
ax.text(21.8, 0.25, 'Synapto v2  |  Architecture Diagram',
        ha='right', va='bottom', fontsize=7, color='#AAAAAA', zorder=10)

# ─────────────────────────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────────────────────────
out = r'c:\Users\AlinD\Documents\GitHub\Synapto\docs\manual\images\platform_architecture_v2.png'
plt.tight_layout(pad=0.4)
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print("Saved: " + out)
plt.close()
