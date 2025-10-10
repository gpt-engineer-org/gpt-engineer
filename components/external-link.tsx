export function ExternalLink({
  href,
  children,
}: {
  href: string;
  children: React.ReactNode;
}) {
  return (
    <a
      href={href}
      target="_blank"
      className="inline-flex flex-1 justify-center gap-1 leading-4 hover:underline"
    >
      <span>{children}</span>
      <svg
        aria-hidden="true"
        height="7"
        viewBox="0 0 6 6"
        width="7"
        className="opacity-70"
      >
        <path
          d="M1.25215 5.54731L0.622742 4.9179L3.78169 1.75597H1.3834L1.38936 0.890915H5.27615V4.78069H4.40513L4.41109 2.38538L1.25215 5.54731Z"
          fill="currentColor"
        ></path>
      </svg>
    </a>
  );
}
