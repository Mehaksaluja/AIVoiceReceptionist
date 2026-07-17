import {
  AlignHorizontalJustifyCenter,
  ArrowRight,
  Baby,
  Siren,
  Smile,
  Sparkles,
  Wrench,
  type LucideIcon,
} from "lucide-react";
import SectionHeader from "./SectionHeader";

const services: { icon: LucideIcon; title: string; desc: string }[] = [
  {
    icon: Smile,
    title: "General Dentistry",
    desc: "Routine exams, cleanings, fillings, and preventive care to keep your smile healthy year-round.",
  },
  {
    icon: Sparkles,
    title: "Cosmetic Dentistry",
    desc: "Teeth whitening, veneers, and smile design tailored to your goals and facial features.",
  },
  {
    icon: Wrench,
    title: "Dental Implants",
    desc: "Permanent, natural-looking replacements for missing teeth with advanced 3D planning.",
  },
  {
    icon: AlignHorizontalJustifyCenter,
    title: "Orthodontics",
    desc: "Clear aligners and braces for teens and adults — straighter teeth, improved bite.",
  },
  {
    icon: Baby,
    title: "Pediatric Care",
    desc: "Gentle, kid-friendly visits that build positive habits from the very first appointment.",
  },
  {
    icon: Siren,
    title: "Emergency Care",
    desc: "Same-day relief for toothaches, broken teeth, and urgent dental injuries.",
  },
];

export default function Services() {
  return (
    <section id="services" className="bg-slate-50 py-20 sm:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeader
          label="Our Services"
          title="Complete care under one roof"
          description="From preventive visits to advanced treatments — every service is delivered with modern equipment and a comfort-first approach."
        />

        <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {services.map(({ icon: Icon, title, desc }) => (
            <article
              key={title}
              className="group rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm transition hover:border-clinical-200 hover:shadow-md"
            >
              <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-clinical-50 transition group-hover:bg-clinical-100">
                <Icon className="h-6 w-6 text-clinical-600" strokeWidth={1.75} aria-hidden />
              </span>
              <h3 className="mt-4 text-lg font-bold text-slate-900">{title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">{desc}</p>
              <a
                href="#book"
                className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-clinical-600 transition hover:text-clinical-700"
              >
                Book this service
                <ArrowRight className="h-4 w-4" aria-hidden />
              </a>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
