const footerLinks = {
  Clinic: [
    { label: "Services", href: "#services" },
    { label: "About", href: "#about" },
    { label: "Doctors", href: "#doctors" },
    { label: "Contact", href: "#contact" },
  ],
  Services: [
    { label: "General Dentistry", href: "#services" },
    { label: "Cosmetic", href: "#services" },
    { label: "Implants", href: "#services" },
    { label: "Emergency", href: "#services" },
  ],
};

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-clinical-900 text-blue-100">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          <div className="sm:col-span-2 lg:col-span-1">
            <p className="text-xl font-bold text-white">BrightSmile</p>
            <p className="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-blue-300">
              Dental Clinic
            </p>
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-blue-200/80">
              Gentle, modern dental care for the whole family. Your comfort is our priority.
            </p>
          </div>

          {Object.entries(footerLinks).map(([heading, links]) => (
            <div key={heading}>
              <p className="text-sm font-bold text-white">{heading}</p>
              <ul className="mt-4 space-y-2">
                {links.map((link) => (
                  <li key={link.label}>
                    <a href={link.href} className="text-sm text-blue-200/80 transition hover:text-white">
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          <div>
            <p className="text-sm font-bold text-white">Get in touch</p>
            <ul className="mt-4 space-y-2 text-sm text-blue-200/80">
              <li>+91 98765 43210</li>
              <li>hello@brightsmile.in</li>
              <li>Mon–Sat, 9 AM – 8 PM</li>
            </ul>
          </div>
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-white/10 pt-8 sm:flex-row">
          <p className="text-xs text-blue-300/70">
            © {new Date().getFullYear()} BrightSmile Dental Clinic. All rights reserved.
          </p>
          <div className="flex gap-6 text-xs text-blue-300/70">
            <a href="#" className="hover:text-white">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-white">
              Terms of Service
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
