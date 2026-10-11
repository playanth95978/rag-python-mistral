export default function Logo({ className = "h-7 w-8" }) {
  return (
    <svg className={className} viewBox="0 0 50 40" aria-hidden="true">
      <path
        fill="#ff7000"
        d="M0 0h10v10h10V0h10v10h10V0h10v40H40V20H30v10H20V20H10v20H0z"
      />
    </svg>
  );
}
