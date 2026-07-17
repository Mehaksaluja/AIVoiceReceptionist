import About from "./components/About";
import Contact from "./components/Contact";
import Doctors from "./components/Doctors";
import Footer from "./components/Footer";
import Hero from "./components/Hero";
import Navbar from "./components/Navbar";
import Services from "./components/Services";

export default function App() {
  return (
    <div className="min-h-screen bg-white text-slate-900 antialiased">
      <Navbar />
      <main>
        <Hero />
        <Services />
        <About />
        <Doctors />
        <Contact />
      </main>
      <Footer />
    </div>
  );
}
