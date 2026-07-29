CREATE TABLE IF NOT EXISTS funnel_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_name TEXT NOT NULL,
  offer_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  step TEXT NOT NULL DEFAULT '',
  score_band TEXT NOT NULL DEFAULT '',
  utm_source TEXT NOT NULL DEFAULT '',
  utm_medium TEXT NOT NULL DEFAULT '',
  utm_campaign TEXT NOT NULL DEFAULT '',
  source_page TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_funnel_events_created_at ON funnel_events(created_at);
CREATE INDEX IF NOT EXISTS idx_funnel_events_name_created ON funnel_events(event_name, created_at);
CREATE INDEX IF NOT EXISTS idx_funnel_events_session ON funnel_events(session_id);
