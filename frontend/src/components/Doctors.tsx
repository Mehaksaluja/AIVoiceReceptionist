import SectionHeader from "./SectionHeader";

const doctors = [
  {
    name: "Dr. Ananya Sharma",
    role: "Chief Dental Surgeon",
    specialty: "Implants & Restorative",
    experience: "12 years",
    initials: "AS",
    color: "from-clinical-500 to-clinical-700",
  },
  {
    name: "Dr. Rohan Mehta",
    role: "Cosmetic Dentist",
    specialty: "Smile Design & Veneers",
    experience: "9 years",
    initials: "RM",
    color: "from-teal-500 to-teal-700",
  },
  {
    name: "Dr. Priya Nair",
    role: "Pediatric Specialist",
    specialty: "Children's Dentistry",
    experience: "8 years",
    initials: "PN",
    color: "from-sky-500 to-sky-700",
  },
];

export default function Doctors() {
  return (
    <section id="doctors" className="bg-slate-50 py-20 sm:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeader
          label="Our Team"
          title="Meet the doctors behind your smile"
          description="Experienced, gentle, and committed to making every visit stress-free."
        />

        <div className="mt-14 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {doctors.map((doc) => (
            <article
              key={doc.name}
              className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm transition hover:shadow-md"
            >
              <div className={`bg-gradient-to-br ${doc.color} px-6 py-10 text-center`}>
                <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-white/20 text-3xl font-bold text-white ring-4 ring-white/30">
                  {doc.initials}
                </div>
              </div>
              <div className="p-6 text-center">
                <h3 className="text-lg font-bold text-slate-900">{doc.name}</h3>
                <p className="mt-1 text-sm font-semibold text-clinical-600">{doc.role}</p>
                <p className="mt-3 text-sm text-slate-600">{doc.specialty}</p>
                <p className="mt-4 inline-block rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                  {doc.experience} experience
                </p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
