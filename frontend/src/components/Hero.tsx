import { ArrowRight, CircleCheck, Star, type LucideIcon } from "lucide-react";
import { useBooking } from "../context/BookingContext";

const stats: { value: string; label: string; icon?: LucideIcon }[] = [
  { value: "15+", label: "Years of care" },
  { value: "12k+", label: "Smiles treated" },
  { value: "4.9", label: "Patient rating", icon: Star },
];

const features = [
  "Digital X-rays & 3D imaging",
  "Same-day emergency visits",
  "Insurance & EMI accepted",
];

export default function Hero() {
  const { openVoiceBooking } = useBooking();

  return (
    <section className="relative overflow-hidden bg-white">
      {/* Soft wash behind text only — image sits flush on the right */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-y-0 left-0 hidden w-1/2 bg-gradient-to-r from-clinical-50/40 to-transparent lg:block"
      />

      <div className="relative mx-auto max-w-7xl lg:min-h-[calc(100vh-7rem)] lg:max-w-none">
        <div className="flex flex-col lg:flex-row lg:items-stretch">
          {/* Copy — overlaps the image's built-in white curve on desktop */}
          <div className="relative z-10 flex flex-col justify-center px-4 pb-10 pt-28 sm:px-6 sm:pt-32 sm:pb-12 lg:w-[46%] lg:max-w-xl lg:shrink-0 lg:px-8 lg:pb-16 lg:pt-36 xl:max-w-2xl xl:pl-16 xl:pr-0">
            <div className="inline-flex w-fit items-center gap-2 rounded-full border border-clinical-200/80 bg-white px-4 py-2 text-xs font-semibold text-clinical-700 shadow-sm">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
              </span>
              Now accepting new patients
            </div>

            <h1 className="mt-6 text-[2rem] font-extrabold leading-[1.12] tracking-tight text-slate-900 sm:text-5xl lg:text-[3.15rem] xl:text-[3.35rem]">
              Advanced dental care with a{" "}
              <span className="text-clinical-600">gentle touch</span>
            </h1>

            <p className="mt-5 max-w-lg text-base leading-relaxed text-slate-600 sm:text-lg">
              From routine check-ups to cosmetic smile makeovers — our team combines
              modern technology with compassionate care for every patient.
            </p>

            <ul className="mt-6 flex flex-wrap gap-x-5 gap-y-2">
              {features.map((f) => (
                <li key={f} className="flex items-center gap-2 text-sm font-medium text-slate-600">
                  <CircleCheck className="h-4 w-4 shrink-0 text-clinical-600" strokeWidth={2} aria-hidden />
                  {f}
                </li>
              ))}
            </ul>

            <div className="mt-9 flex flex-col gap-3 sm:flex-row sm:items-center">
              <button
                type="button"
                onClick={openVoiceBooking}
                className="inline-flex items-center justify-center gap-2 rounded-full bg-clinical-600 px-8 py-4 text-base font-semibold text-white shadow-lg shadow-clinical-600/25 transition hover:bg-clinical-700"
              >
                Book Appointment
                <ArrowRight className="h-4 w-4" aria-hidden />
              </button>
              <a
                href="#services"
                className="inline-flex items-center justify-center rounded-full border border-slate-200 bg-white px-8 py-4 text-base font-semibold text-slate-700 transition hover:border-clinical-300 hover:text-clinical-700"
              >
                View Services
              </a>
            </div>

            <dl className="mt-12 grid grid-cols-3 gap-4 border-t border-slate-200/80 pt-8 sm:gap-8">
              {stats.map((s, i) => (
                <div key={s.label} className={i > 0 ? "border-l border-slate-200 pl-4 sm:pl-8" : ""}>
                  <dt className="flex items-center gap-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                    {s.value}
                    {s.icon && <s.icon className="h-5 w-5 text-amber-500 sm:h-6 sm:w-6" fill="currentColor" strokeWidth={0} aria-hidden />}
                  </dt>
                  <dd className="mt-1 text-xs font-medium text-slate-500 sm:text-sm">{s.label}</dd>
                </div>
              ))}
            </dl>
          </div>

          {/* Image — full bleed right, no box; white curve blends into page bg */}
          <div className="relative h-[340px] w-full sm:h-[440px] lg:absolute lg:inset-y-0 lg:right-0 lg:h-auto lg:w-[58%] xl:w-[55%]">
            <img
              src="/hero.png"
              alt="Patient receiving gentle dental care at BrightSmile clinic"
              className="h-full w-full object-cover object-[68%_center] sm:object-[65%_center] lg:object-[58%_center]"
              fetchPriority="high"
            />
            {/* Feather left edge so curve merges with white (subtle) */}
            <div
              aria-hidden
              className="pointer-events-none absolute inset-y-0 left-0 w-16 bg-gradient-to-r from-white to-transparent sm:w-24 lg:w-32"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
