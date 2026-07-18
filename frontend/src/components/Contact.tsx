import { Clock, Mail, Map, MapPin, Mic, Phone } from "lucide-react";
import SectionHeader from "./SectionHeader";
import { useBooking } from "../context/BookingContext";

const contactInfo = [
  {
    label: "Phone",
    value: "+91 9898989898",
    href: "tel:+919898989898",
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
  const { openVoiceBooking } = useBooking();

  return (
    <section id="contact" className="bg-white py-20 sm:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeader
          label="Contact"
          title="Book with our voice assistant"
          description="No form to fill out. Start a voice session and the receptionist will ask for your details and schedule a time."
        />

        <div className="mt-14 grid gap-12 lg:grid-cols-5">
          <div id="book" className="scroll-mt-32 lg:col-span-3">
            <div className="rounded-2xl border border-slate-200 bg-slate-50/50 p-6 sm:p-8">
              <div className="flex items-start gap-4">
                <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-clinical-600 text-white">
                  <Mic className="h-6 w-6" strokeWidth={1.75} aria-hidden />
                </span>
                <div>
                  <h3 className="text-xl font-bold text-slate-900">Voice appointment booking</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-600">
                    Click below to open the assistant in your browser. It will ask for your name,
                    reason for visit, and mobile number, then check availability and confirm a slot.
                  </p>
                </div>
              </div>

              <ul className="mt-6 space-y-2 text-sm text-slate-600">
                <li className="flex gap-2">
                  <span className="font-medium text-slate-800">1.</span>
                  Allow microphone access when prompted
                </li>
                <li className="flex gap-2">
                  <span className="font-medium text-slate-800">2.</span>
                  Answer the assistant&apos;s questions naturally
                </li>
                <li className="flex gap-2">
                  <span className="font-medium text-slate-800">3.</span>
                  Confirm your preferred appointment time
                </li>
              </ul>

              <button
                type="button"
                onClick={openVoiceBooking}
                className="mt-8 inline-flex w-full items-center justify-center gap-2 rounded-full bg-clinical-600 py-4 text-base font-semibold text-white shadow-lg shadow-clinical-600/25 transition hover:bg-clinical-700 sm:w-auto sm:px-10"
              >
                <Mic className="h-5 w-5" aria-hidden />
                Start voice booking
              </button>

              <p className="mt-4 text-xs text-slate-500">
                Runs in your browser — your phone will not ring.
              </p>
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
