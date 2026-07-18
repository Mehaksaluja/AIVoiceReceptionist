import { createContext, useCallback, useContext, useState, type ReactNode } from "react";
import VoiceAssistant from "../components/VoiceAssistant";

type BookingContextValue = {
  openVoiceBooking: () => void;
  isVoiceOpen: boolean;
};

const BookingContext = createContext<BookingContextValue | null>(null);

export function BookingProvider({ children }: { children: ReactNode }) {
  const [isVoiceOpen, setIsVoiceOpen] = useState(false);

  const openVoiceBooking = useCallback(() => {
    setIsVoiceOpen(true);
  }, []);

  const closeVoiceBooking = useCallback(() => {
    setIsVoiceOpen(false);
  }, []);

  return (
    <BookingContext.Provider value={{ openVoiceBooking, isVoiceOpen }}>
      {children}
      <VoiceAssistant open={isVoiceOpen} onClose={closeVoiceBooking} />
    </BookingContext.Provider>
  );
}

export function useBooking() {
  const ctx = useContext(BookingContext);
  if (!ctx) {
    throw new Error("useBooking must be used within BookingProvider");
  }
  return ctx;
}
