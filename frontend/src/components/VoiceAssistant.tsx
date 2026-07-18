import {
  CalendarCheck,
  Loader2,
  Mic,
  MicOff,
  PhoneOff,
  X,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { getSession, startWebCall, type WebCallResponse } from "../lib/api";
import { resolveVapiConstructor, type VapiClient } from "../lib/vapi";

type CallPhase = "connecting" | "active" | "booked" | "ended" | "error";

type VoiceAssistantProps = {
  open: boolean;
  onClose: () => void;
};

function VoiceOrb({ speaking, muted }: { speaking: boolean; muted: boolean }) {
  return (
    <div className="relative flex h-40 w-40 items-center justify-center">
      {speaking && (
        <>
          <span className="absolute inset-0 animate-ping rounded-full bg-clinical-500/20" />
          <span className="absolute inset-3 animate-pulse rounded-full bg-clinical-500/15" />
        </>
      )}
      <div
        className={`relative flex h-28 w-28 items-center justify-center rounded-full shadow-lg transition-all duration-300 ${
          muted
            ? "bg-slate-200 text-slate-500"
            : speaking
              ? "bg-clinical-600 text-white scale-105 shadow-clinical-600/30"
              : "bg-clinical-50 text-clinical-600 ring-1 ring-clinical-200"
        }`}
      >
        {muted ? (
          <MicOff className="h-10 w-10" strokeWidth={1.5} aria-hidden />
        ) : (
          <Mic className="h-10 w-10" strokeWidth={1.5} aria-hidden />
        )}
      </div>
      {speaking && !muted && (
        <div className="absolute -bottom-1 flex items-end gap-1">
          {[0, 1, 2, 3, 4].map((i) => (
            <span
              key={i}
              className="w-1 rounded-full bg-clinical-500"
              style={{
                height: `${8 + (i % 3) * 6}px`,
                animation: `voice-bar 0.8s ease-in-out ${i * 0.1}s infinite alternate`,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function VoiceAssistant({ open, onClose }: VoiceAssistantProps) {
  const vapiRef = useRef<VapiClient | null>(null);
  const pollRef = useRef<number | null>(null);

  const [phase, setPhase] = useState<CallPhase>("connecting");
  const [error, setError] = useState<string | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [confirmedSlot, setConfirmedSlot] = useState<string | null>(null);
  const [callerName, setCallerName] = useState("BrightSmile Dental Clinic");

  const stopPolling = useCallback(() => {
    if (pollRef.current !== null) {
      window.clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const endCall = useCallback(() => {
    stopPolling();
    vapiRef.current?.stop();
    vapiRef.current = null;
    setPhase((current) => (current === "booked" ? "booked" : "ended"));
  }, [stopPolling]);

  const handleClose = useCallback(() => {
    endCall();
    onClose();
  }, [endCall, onClose]);

  const startPolling = useCallback(
    (sessionId: string) => {
      stopPolling();
      pollRef.current = window.setInterval(async () => {
        try {
          const session = await getSession(sessionId);
          if (session.is_booked && session.confirmed_slot) {
            setConfirmedSlot(session.confirmed_slot);
            setPhase("booked");
          }
        } catch {
          // ignore transient poll errors
        }
      }, 2000);
    },
    [stopPolling],
  );

  const beginCall = useCallback(
    async (payload: WebCallResponse) => {
      setCallerName(payload.caller_display_name);

      const Vapi = resolveVapiConstructor();
      const vapi = new Vapi(payload.public_key);
      vapiRef.current = vapi;

      vapi.on("call-start", () => {
        setPhase("active");
        startPolling(payload.session_id);
      });

      vapi.on("call-end", () => {
        stopPolling();
        setPhase((current) => (current === "booked" ? "booked" : "ended"));
      });

      vapi.on("speech-start", () => setIsSpeaking(true));
      vapi.on("speech-end", () => setIsSpeaking(false));

      vapi.on("error", (e: Error | { message?: string }) => {
        const msg = e instanceof Error ? e.message : e.message ?? "Voice connection failed";
        setError(msg);
        setPhase("error");
        stopPolling();
      });

      await vapi.start(payload.assistant as Parameters<VapiClient["start"]>[0]);
    },
    [startPolling, stopPolling],
  );

  useEffect(() => {
    if (!open) return;

    let cancelled = false;

    async function boot() {
      setPhase("connecting");
      setError(null);
      setConfirmedSlot(null);
      setIsSpeaking(false);
      setIsMuted(false);

      try {
        const payload = await startWebCall();
        if (cancelled) return;
        await beginCall(payload);
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Could not start voice assistant");
        setPhase("error");
      }
    }

    void boot();

    return () => {
      cancelled = true;
      stopPolling();
      vapiRef.current?.stop();
      vapiRef.current = null;
    };
  }, [open, beginCall, stopPolling]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") handleClose();
    };
    window.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open, handleClose]);

  if (!open) return null;

  function toggleMute() {
    const next = !isMuted;
    setIsMuted(next);
    vapiRef.current?.setMuted(next);
  }

  const statusLabel =
    phase === "connecting"
      ? "Connecting…"
      : phase === "ended"
        ? "Call ended"
        : phase === "booked"
          ? "Booked"
          : phase === "error"
            ? "Something went wrong"
            : isMuted
              ? "Muted"
              : isSpeaking
                ? "Assistant speaking"
                : "Listening";

  return (
    <div className="fixed inset-0 z-100 flex items-end justify-center sm:items-center sm:p-6">
      <div
        className="absolute inset-0 bg-slate-900/50 backdrop-blur-[2px]"
        onClick={handleClose}
        aria-hidden
      />

      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="voice-assistant-title"
        className="relative flex w-full max-w-sm flex-col overflow-hidden rounded-t-3xl bg-white shadow-2xl sm:rounded-3xl"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 pt-5 pb-2">
          <div className="min-w-0">
            <p id="voice-assistant-title" className="truncate text-base font-semibold text-slate-900">
              {callerName}
            </p>
            <p className="mt-0.5 text-xs text-slate-500">Voice booking</p>
          </div>
          <button
            type="button"
            onClick={handleClose}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-500 transition hover:bg-slate-200 hover:text-slate-800"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Body */}
        <div className="flex flex-col items-center px-6 py-10">
          {phase === "connecting" && (
            <>
              <div className="flex h-28 w-28 items-center justify-center rounded-full bg-clinical-50">
                <Loader2 className="h-10 w-10 animate-spin text-clinical-600" />
              </div>
              <p className="mt-6 text-sm font-medium text-slate-800">{statusLabel}</p>
              <p className="mt-2 text-center text-xs text-slate-500">
                Allow microphone access when asked
              </p>
            </>
          )}

          {(phase === "active" || phase === "ended") && (
            <>
              <VoiceOrb speaking={isSpeaking && phase === "active"} muted={isMuted} />
              <p className="mt-8 text-sm font-medium text-slate-800">{statusLabel}</p>
              {phase === "active" && (
                <p className="mt-2 max-w-[240px] text-center text-xs leading-relaxed text-slate-500">
                  Speak naturally. The assistant will ask for your name, reason, and phone number.
                </p>
              )}
            </>
          )}

          {phase === "booked" && (
            <>
              <div className="flex h-28 w-28 items-center justify-center rounded-full bg-emerald-50">
                <CalendarCheck className="h-12 w-12 text-emerald-600" strokeWidth={1.5} />
              </div>
              <p className="mt-6 text-lg font-semibold text-slate-900">Appointment confirmed</p>
              {confirmedSlot && (
                <p className="mt-2 text-center text-sm text-slate-600">{confirmedSlot}</p>
              )}
            </>
          )}

          {phase === "error" && (
            <>
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-red-50">
                <PhoneOff className="h-8 w-8 text-red-500" strokeWidth={1.5} />
              </div>
              <p className="mt-5 text-sm font-medium text-slate-900">{statusLabel}</p>
              <p className="mt-2 max-w-[280px] text-center text-xs leading-relaxed text-slate-500">
                {error}
              </p>
            </>
          )}
        </div>

        {/* Controls */}
        <div className="flex items-center justify-center gap-5 border-t border-slate-100 px-6 py-6">
          {phase === "active" && (
            <button
              type="button"
              onClick={toggleMute}
              className={`flex h-12 w-12 items-center justify-center rounded-full transition ${
                isMuted
                  ? "bg-slate-800 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
              aria-label={isMuted ? "Unmute" : "Mute"}
            >
              {isMuted ? (
                <MicOff className="h-5 w-5" aria-hidden />
              ) : (
                <Mic className="h-5 w-5" aria-hidden />
              )}
            </button>
          )}

          {(phase === "active" || phase === "connecting") && (
            <button
              type="button"
              onClick={endCall}
              className="flex h-14 w-14 items-center justify-center rounded-full bg-red-500 text-white shadow-lg shadow-red-500/25 transition hover:bg-red-600"
              aria-label="End call"
            >
              <PhoneOff className="h-6 w-6" aria-hidden />
            </button>
          )}

          {(phase === "booked" || phase === "ended" || phase === "error") && (
            <button
              type="button"
              onClick={handleClose}
              className="rounded-full bg-clinical-600 px-10 py-3 text-sm font-semibold text-white transition hover:bg-clinical-700"
            >
              {phase === "booked" ? "Done" : "Close"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
