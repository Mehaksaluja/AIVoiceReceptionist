import { Menu, X } from "lucide-react";
import { useEffect, useState } from "react";
import { useBooking } from "../context/BookingContext";

function LogoMark({ className = "h-9 w-9" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 40 40" fill="none" aria-hidden>
      <rect width="40" height="40" rx="10" className="fill-clinical-600" />
      <path
        d="M20 8c-3.5 0-6 2.8-6 6.2 0 2.1.9 3.8 2.2 5.3-.8 1.5-1.4 3.2-1.4 5 0 4.2 2.4 7.5 5.2 7.5s5.2-3.3 5.2-7.5c0-1.8-.6-3.5-1.4-5 1.3-1.5 2.2-3.2 2.2-5.3C26 10.8 23.5 8 20 8z"
        fill="white"
        fillOpacity="0.95"
      />
    </svg>
  );
}

const links = [
  { label: "Services", href: "#services" },
  { label: "About", href: "#about" },
  { label: "Doctors", href: "#doctors" },
  { label: "Contact", href: "#contact" },
];

export default function Navbar() {
  const { openVoiceBooking } = useBooking();
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  return (
    <>
      <header
        className={`fixed inset-x-0 top-0 z-50 transition-all duration-300 ${
          scrolled
            ? "border-b border-slate-200/90 bg-white/95 shadow-[0_4px_24px_rgba(15,23,42,0.06)] backdrop-blur-lg"
            : "border-b border-transparent bg-white/70 backdrop-blur-md"
        }`}
      >
        <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:h-[4.25rem] sm:px-6 lg:px-8">
          <a href="#" className="group flex items-center gap-3">
            <LogoMark className="h-10 w-10 shadow-lg shadow-clinical-600/20 transition group-hover:scale-[1.02]" />
            <div className="leading-tight">
              <span className="block text-[17px] font-bold tracking-tight text-slate-900">
                BrightSmile
              </span>
              <span className="block text-[10px] font-semibold uppercase tracking-[0.2em] text-clinical-600">
                Dental Clinic
              </span>
            </div>
          </a>

          <ul className="hidden items-center gap-1 md:flex">
            {links.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  className="rounded-lg px-4 py-2 text-[13px] font-semibold text-slate-600 transition hover:bg-slate-50 hover:text-clinical-700"
                >
                  {link.label}
                </a>
              </li>
            ))}
          </ul>

          <div className="flex items-center gap-2 sm:gap-3">
            <button
              type="button"
              onClick={openVoiceBooking}
              className="hidden rounded-full bg-clinical-600 px-5 py-2.5 text-sm font-semibold text-white shadow-md shadow-clinical-600/25 transition hover:bg-clinical-700 sm:inline-block"
            >
              Book Appointment
            </button>
            <button
              type="button"
              aria-label={menuOpen ? "Close menu" : "Open menu"}
              className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-700 md:hidden"
              onClick={() => setMenuOpen((o) => !o)}
            >
              {menuOpen ? (
                <X className="h-5 w-5" strokeWidth={1.75} aria-hidden />
              ) : (
                <Menu className="h-5 w-5" strokeWidth={1.75} aria-hidden />
              )}
            </button>
          </div>
        </nav>
      </header>

      {menuOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm md:hidden"
          onClick={() => setMenuOpen(false)}
          aria-hidden
        />
      )}
      <div
        className={`fixed inset-x-0 top-16 z-50 border-b border-slate-200 bg-white px-4 py-6 shadow-xl transition md:hidden ${
          menuOpen ? "translate-y-0 opacity-100" : "pointer-events-none -translate-y-2 opacity-0"
        }`}
      >
        <ul className="flex flex-col gap-1">
          {links.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="block rounded-xl px-3 py-3 text-base font-semibold text-slate-800"
                onClick={() => setMenuOpen(false)}
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>
        <button
          type="button"
          onClick={() => {
            setMenuOpen(false);
            openVoiceBooking();
          }}
          className="mt-4 block w-full rounded-full bg-clinical-600 py-3.5 text-center text-sm font-semibold text-white"
        >
          Book Appointment
        </button>
      </div>
    </>
  );
}
