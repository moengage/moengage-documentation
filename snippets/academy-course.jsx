export const AcademyCourse = ({ title, duration, href }) => {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      style={{
        display: "flex",
        alignItems: "center",
        gap: "0.875rem",
        padding: "1rem 1.25rem",
        border: "1px solid var(--gray-200, #e5e7eb)",
        borderRadius: "0.75rem",
        textDecoration: "none",
        color: "inherit",
        margin: "0 0 1.25rem",
      }}
    >
      <svg
        width="28"
        height="28"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{ flexShrink: 0, opacity: 0.85 }}
        aria-hidden="true"
      >
        <path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z" />
        <path d="M22 10v6" />
        <path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5" />
      </svg>
      <span>
        <strong style={{ display: "block", fontSize: "1rem", lineHeight: 1.3 }}>
          {title}
        </strong>
        <span style={{ fontSize: "0.875rem", opacity: 0.7 }}>
          MoEngage Academy course · {duration}
        </span>
      </span>
    </a>
  );
};
