"use client";

import type { RouteNarrativeResponse, NarrativeSection } from "@/lib/types";

const SEVERITY_STYLES: Record<string, { bg: string; border: string; title: string }> = {
  info: { bg: "#0f172a", border: "#1e3a5f", title: "#93c5fd" },
  success: { bg: "#052e16", border: "#166534", title: "#86efac" },
  warning: { bg: "#422006", border: "#854d0e", title: "#fde047" },
  alert: { bg: "#450a0a", border: "#991b1b", title: "#fca5a5" },
};

interface Props {
  narrative: RouteNarrativeResponse;
}

export function RouteNarrative({ narrative }: Props) {
  return (
    <div style={{ borderTop: "2px solid #1e3a5f", background: "#0a0f1a" }}>
      {/* Header */}
      <div
        style={{
          padding: "0.5rem 0.75rem",
          background: "linear-gradient(135deg, #0f172a, #1e293b)",
          borderBottom: "1px solid #1f2937",
        }}
      >
        <div style={{ fontSize: "11px", fontWeight: 700, color: "#60a5fa" }}>
          Route Intelligence Summary
        </div>
        <div style={{ fontSize: "9px", color: "#6b7280", marginTop: "2px" }}>
          {narrative.origin} → {narrative.destination}
          {narrative.vehicle_class && ` · ${narrative.vehicle_class.replace("_", " ")}`}
          {" "}| Sources: {narrative.data_sources.join(", ")}
        </div>
      </div>

      {/* Sections */}
      <div className="sidebar-scroll" style={{ maxHeight: "400px", overflowY: "auto" }}>
        {narrative.sections.map((section) => (
          <SectionCard key={section.section_id} section={section} />
        ))}
      </div>
    </div>
  );
}

function SectionCard({ section }: { section: NarrativeSection }) {
  const colors = SEVERITY_STYLES[section.severity] || SEVERITY_STYLES.info;

  return (
    <div
      style={{
        padding: "0.5rem 0.75rem",
        borderBottom: "1px solid rgba(31,41,55,0.3)",
        borderLeft: `3px solid ${colors.border}`,
        background: colors.bg,
      }}
    >
      <div
        style={{
          fontSize: "10px",
          fontWeight: 600,
          color: colors.title,
          marginBottom: "3px",
        }}
      >
        {section.icon} {section.title}
      </div>
      <div
        style={{
          fontSize: "11px",
          color: "#d1d5db",
          lineHeight: 1.55,
        }}
      >
        {section.content}
      </div>
    </div>
  );
}
