import { Award, Check, Heart, Receipt } from "lucide-react";
import SectionHeader from "./SectionHeader";

const values = [
  {
    icon: Heart,
    title: "Patient-first always",
    desc: "We explain every step, never rush you, and tailor treatment to your comfort level.",
  },
  {
    icon: Award,
    title: "Clinical excellence",
    desc: "Board-certified specialists, digital diagnostics, and evidence-based protocols.",
  },
  {
    icon: Receipt,
    title: "Transparent pricing",
    desc: "Clear estimates upfront. Insurance, EMI, and corporate plans welcome.",
  },
];

export default function About() {
  return (
    <section id="about" className="bg-white py-20 sm:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          <div>
            <SectionHeader
              label="About Us"
              title="A clinic built on trust & technology"
              description="BrightSmile has served families for over 15 years. Our mission is simple: world-class dental care that feels calm, clear, and genuinely caring."
              align="left"
            />

            <ul className="mt-10 space-y-6">
              {values.map(({ icon: Icon, title, desc }) => (
                <li key={title} className="flex gap-4">
                  <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-clinical-600">
                    <Icon className="h-4 w-4 text-white" strokeWidth={2} aria-hidden />
                  </span>
                  <div>
                    <h3 className="font-bold text-slate-900">{title}</h3>
                    <p className="mt-1 text-sm leading-relaxed text-slate-600">{desc}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div className="relative">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-4">
                <div className="rounded-2xl bg-clinical-600 p-6 text-white shadow-lg">
                  <p className="text-4xl font-extrabold">15+</p>
                  <p className="mt-1 text-sm text-blue-100">Years serving patients</p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
                  <p className="text-4xl font-extrabold text-slate-900">98%</p>
                  <p className="mt-1 text-sm text-slate-600">Would recommend us</p>
                </div>
              </div>
              <div className="space-y-4 pt-8">
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
                  <p className="text-4xl font-extrabold text-slate-900">12k+</p>
                  <p className="mt-1 text-sm text-slate-600">Happy smiles</p>
                </div>
                <div className="flex items-start gap-3 rounded-2xl bg-clinical-900 p-6 text-white shadow-lg">
                  <Check className="mt-0.5 h-5 w-5 shrink-0 text-blue-200" aria-hidden />
                  <div>
                    <p className="text-lg font-bold">ISO-grade</p>
                    <p className="mt-1 text-sm text-blue-200">Sterilization & safety protocols</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
