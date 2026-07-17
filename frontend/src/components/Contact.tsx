import { Clock, Mail, Map, MapPin, Phone } from "lucide-react";
import { useState } from "react";
import SectionHeader from "./SectionHeader";

const contactInfo = [
  {
    label: "Phone",
    value: "+91 98765 43210",
    href: "tel:+919876543210",
    icon: Phone,
  },
  {
    label: "Email",
    value: "hello@brightsmile.in",
    href: "mailto:hello@brightsmile.in",
    icon: Mail,
  },
  {
    label: "Address",
    value: "42 Health Avenue, Sector 18, Gurugram",
    href: "https://maps.google.com",
    icon: MapPin,
  },
  {
    label: "Hours",
    value: "Mon–Sat: 9 AM – 8 PM",
    href: undefined,
    icon: Clock,
  },
];

export default function Contact() {
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSubmitted(true);
  }

  return (
    <section id="contact" className="bg-white py-20 sm:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeader
          label="Contact"
          title="Visit us or book online"
          description="Fill out the form and our AI receptionist will call you within 30 seconds to confirm your slot."
        />

        <div className="mt-14 grid gap-12 lg:grid-cols-5">
          <div id="book" className="scroll-mt-32 lg:col-span-3">
            <div className="rounded-2xl border border-slate-200 bg-slate-50/50 p-6 sm:p-8">
              <h3 className="text-xl font-bold text-slate-900">Book an appointment</h3>
              <p className="mt-1 text-sm text-slate-600">
                We&apos;ll connect you with our AI assistant to schedule instantly.
              </p>

              {submitted ? (
                <div className="mt-8 rounded-xl border border-emerald-200 bg-emerald-50 p-6 text-center">
                  <p className="text-lg font-semibold text-emerald-800">Request received!</p>
                  <p className="mt-2 text-sm text-emerald-700">
                    Booking integration coming next — your AI call flow will start here.
                  </p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="mt-6 space-y-4">
                  <div className="grid gap-4 sm:grid-cols-2">
                    <label className="block">
                      <span className="text-sm font-semibold text-slate-700">Full name</span>
                      <input
                        required
                        type="text"
                        placeholder="Mehak Saluja"
                        className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-clinical-500 focus:ring-2 focus:ring-clinical-500/20"
                      />
                    </label>
                    <label className="block">
                      <span className="text-sm font-semibold text-slate-700">Phone</span>
                      <input
                        required
                        type="tel"
                        placeholder="+919876543210"
                        className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-clinical-500 focus:ring-2 focus:ring-clinical-500/20"
                      />
                    </label>
                  </div>
                  <label className="block">
                    <span className="text-sm font-semibold text-slate-700">Reason for visit</span>
                    <input
                      required
                      type="text"
                      placeholder="Dental checkup, whitening..."
                      className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-clinical-500 focus:ring-2 focus:ring-clinical-500/20"
                    />
                  </label>
                  <label className="block">
                    <span className="text-sm font-semibold text-slate-700">Message (optional)</span>
                    <textarea
                      rows={3}
                      placeholder="Any notes for the clinic..."
                      className="mt-1.5 w-full resize-none rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-clinical-500 focus:ring-2 focus:ring-clinical-500/20"
                    />
                  </label>
                  <button
                    type="submit"
                    className="w-full rounded-full bg-clinical-600 py-4 text-base font-semibold text-white shadow-lg shadow-clinical-600/25 transition hover:bg-clinical-700 sm:w-auto sm:px-10"
                  >
                    Book Appointment
                  </button>
                </form>
              )}
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="space-y-4">
              {contactInfo.map(({ label, value, href, icon: Icon }) => (
                <div
                  key={label}
                  className="flex gap-4 rounded-xl border border-slate-200 bg-white p-4"
                >
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-clinical-50 text-clinical-600">
                    <Icon className="h-5 w-5" strokeWidth={1.75} aria-hidden />
                  </span>
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wide text-slate-400">{label}</p>
                    {href ? (
                      <a
                        href={href}
                        className="mt-0.5 block text-sm font-semibold text-slate-800 hover:text-clinical-600"
                      >
                        {value}
                      </a>
                    ) : (
                      <p className="mt-0.5 text-sm font-semibold text-slate-800">{value}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 overflow-hidden rounded-2xl border border-slate-200 bg-slate-100">
              <div className="flex h-48 items-center justify-center text-sm text-slate-500">
                <div className="text-center">
                  <Map className="mx-auto h-8 w-8 text-clinical-400" strokeWidth={1.75} aria-hidden />
                  <p className="mt-2 font-medium">Map embed coming soon</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
